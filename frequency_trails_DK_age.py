import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re


# Data from http://statbank.dk/statbank5a/default.asp?w=1280
df = pd.read_csv('data/Age_data_DK.csv', index_col='Age')

# Clean up index and remove 'years', making it an integer
df.index = pd.Index([int(re.match(r'^([0-9]+) \w{4,5}$', s).group(1)) 
			for s in df.index], name='Age (yrs)')

# Normalise each column
df_norm = df/df.sum()

# Truncate DataFrame at the last age with at least 1e-5 of the population in one of the observed years
df = df[(df_norm>1e-5).any(axis=1).sort_index(ascending=False).expanding().max().reindex(df.index)==1]

df_norm = df/df.sum()

# Create the plotting function for a single year
def plot_dist(ax, s, offset, z, rgb_color):
    ax.fill_between(s.index,offset,offset+s.get_values(), zorder=z, color=rgb_color)
    ax.plot(s.index,offset*np.ones_like(s.get_values()), color='w', zorder=z) # White line below plot
    ax.plot(s.index, offset+s.get_values(), color='w', zorder=z) # White line above plot

# Calculate the mean age of the population for each year
mean_age = (df.multiply(pd.Series(list(df.index), index=df.index), axis=0).sum()/df.sum())

# Set colour map and normalisation. Needed for plots, where the colour map is set manually
norm = mpl.colors.Normalize(vmin=mean_age.min(), vmax=mean_age.max())
cmap = mpl.cm.jet

# Instantiate scalar map and set specific array values (latter is used for colorbar)
m = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
m.set_array(np.arange(int(mean_age.min()), int(mean_age.max())+1))

# Set offset parameters and initialise dictionary for y-axis tick marks
shift = df_norm.max().max()/2
start = 0.5
no_plots = df_norm.shape[1]
yticks = dict()

# Set font options 
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'Tahoma'

# Instantiate a Figure object and add an Axes object spaning the entire figure
fig = plt.figure(figsize=(14,10))
ax = fig.add_axes((0.1,0.1,0.8,0.8))

# Add a colorbar to the Figure object and set a label
cb = fig.colorbar(m, ax=ax, fraction=0.03, use_gridspec=False, aspect=30, pad=0)
cb.set_label('Mean age of population (yrs)', labelpad = -60, y=0.5, fontdict={'fontsize': 16})

# Loop over columns, i.e. years with observations and plot distribution for each year
for n, c in enumerate(df_norm.columns):
    plot_dist(ax, df_norm[c], start+n*shift, no_plots-n, m.to_rgba(mean_age[c]))
    # Add a tick mark for every fifth year
    if n % 5 == 0:
        yticks[c] = start+n*shift

# Add a final tick mark for the last year
if n % 5 != 0:
    yticks[c] = start+n*shift

# Set ticks and labels 
ax.set_xlabel(df.index.name, fontdict={'fontsize': 16})
ax.set_yticks(list(yticks.values()))
ax.set_yticklabels(list(yticks.keys()), fontdict={'fontsize': 16})

# Remove frame and set title
ax.set_frame_on(False)
ax.set_title('Evolution of Denmark\'s age distribution over three decades', fontdict={'fontsize':24, 'fontweight': 'bold'});

# Save plot to file
fig.savefig('frequency_trails_DK_age.png', format='png', dpi=300)

