import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 10))

gdf.plot(
    ax=ax, 
    edgecolor='#b0b0b0', 
    linewidth=0.6, 
    column='pov_idx', 
    cmap='plasma', 
    legend=True, 
    legend_kwds={'label': "Low Poverty Index", 
                 'orientation': "vertical"}
    )
ax.set_axis_off()
plt.show()
