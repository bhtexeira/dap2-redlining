import pandas as pd
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 10))
gdf.plot(
    ax=ax,
    edgecolor="#b0b0b0",
    linewidth=0.4,
    column="haz_idx",
    cmap="Reds",
    legend=True,
    missing_kwds={"color": "#eeeeee", "edgecolor": "#b0b0b0", "label": "No haz_idx match"},
    legend_kwds={"label": "Environmental Hazard Index", "orientation": "vertical"},
)
ax.set_axis_off()
plt.show()
