"""Project 2 figures, regenerated from the course dataset.

Data: World Bank climate-change indicators, as cleaned in
light-and-salt/World-Bank-Data-by-Indicators (climate-change.csv), 1960-2018.
Run: .venv/bin/python make_viz.py  ->  for.png, against.png
"""

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

KT = "average_value_CO2 emissions (kt)"
PC = "average_value_CO2 emissions (metric tons per capita)"
RED, BLUE, GRAY, INK, MUTED = "#c0392b", "#1f5f8b", "#a8a8a8", "#1a1a1a", "#6b6b6b"
SOURCE = "Source: World Bank, World Development Indicators (CO₂ emissions, 1960–2018)."

df = pd.read_csv("data/climate-change.csv")
d = df[df["Country Code"].isin(["CHN", "USA", "EUU"])]
mt = d.pivot(index="Year", columns="Country Code", values=KT) / 1e3          # kt -> million t
pc = d.pivot(index="Year", columns="Country Code", values=PC)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})


def frame(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK)


# ---------------------------------------------------------------- FOR

a = mt.loc[1990:2018]
us_eu = a["USA"] + a["EUU"]
# exact crossing of China's line with the US+EU total, by linear interpolation
y0, y1 = 2010, 2011
g0 = a.loc[y0, "CHN"] - us_eu[y0]
g1 = a.loc[y1, "CHN"] - us_eu[y1]
xc = y0 + g0 / (g0 - g1)
yc = a.loc[y0, "CHN"] + (xc - y0) * (a.loc[y1, "CHN"] - a.loc[y0, "CHN"])

fig, ax = plt.subplots(figsize=(8, 5.6), dpi=200)
ax.plot(a.index, a["USA"], color=GRAY, lw=2.2)
ax.plot(a.index, a["EUU"], color=GRAY, lw=2.2)
ax.plot(a.index, a["CHN"], color=RED, lw=3.2)
ax.scatter([xc], [yc], s=36, color=RED, zorder=5, edgecolor="white", linewidth=1.2)

ax.text(2018.6, a.loc[2018, "CHN"], "China", color=RED, weight="bold", va="center")
ax.text(2018.6, a.loc[2018, "USA"], "United States", color=MUTED, va="center")
ax.text(2018.6, a.loc[2018, "EUU"], "European Union", color=MUTED, va="center")

ax.annotate(
    f"China passes the US and EU combined\n"
    f"(2011: {a.loc[2011, 'CHN']:,.0f} vs {us_eu[2011]:,.0f} million tonnes)",
    xy=(xc, yc), xytext=(1991.5, 8350), color=INK, fontsize=10, va="center",
    arrowprops=dict(arrowstyle="->", color=INK, lw=1.1, shrinkA=4, shrinkB=5),
)

ax.set_xlim(1990, 2024)
ax.set_ylim(0, 11500)
ax.set_xticks(range(1990, 2021, 5))
ax.set_xlabel("Year")
ax.set_ylabel("Annual CO₂ emissions (million tonnes)")
ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("China now emits more CO₂ than the United States\nand the European Union combined",
             loc="left", weight="bold", fontsize=14, pad=12)
frame(ax)
fig.text(0.1, 0.012, SOURCE + "\nConverted from kilotonnes to million tonnes.",
         color=MUTED, fontsize=8.5)
fig.subplots_adjust(left=0.13, right=0.97, top=0.86, bottom=0.165)
fig.savefig("for.png")
plt.close(fig)

# ---------------------------------------------------------------- AGAINST

cum = mt.loc[1960:2018].cumsum() / 1e3                                          # billion t
fig, ax = plt.subplots(figsize=(8, 5.6), dpi=200)
ax.plot(cum.index, cum["CHN"], color=GRAY, lw=2.2)
ax.plot(cum.index, cum["EUU"], color=GRAY, lw=2.2)
ax.plot(cum.index, cum["USA"], color=BLUE, lw=3.2)

ax.text(2019, cum.loc[2018, "USA"], f"United States\n{cum.loc[2018, 'USA']:.0f} bn t",
        color=BLUE, weight="bold", va="center")
ax.text(2019, cum.loc[2018, "CHN"] + 9, f"China\n{cum.loc[2018, 'CHN']:.0f} bn t",
        color=MUTED, va="center")
ax.text(2019, cum.loc[2018, "EUU"] - 14, f"European Union\n{cum.loc[2018, 'EUU']:.0f} bn t",
        color=MUTED, va="center")
ax.text(1962.5, 243,
        f"China's per-person emissions today ({pc.loc[2018, 'CHN']:.1f} tonnes)\n"
        f"are still below America's in 1960 ({pc.loc[1960, 'USA']:.1f} tonnes)",
        color=INK, fontsize=10, va="center")

ax.set_xlim(1960, 2030)
ax.set_ylim(0, 300)
ax.set_xticks(range(1960, 2021, 10))
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative CO₂ emitted since 1960\n(billion tonnes, bn t)")
ax.set_title("Carbon dioxide stays in the air for centuries.\n"
             "No country has put more of it there than the United States",
             loc="left", weight="bold", fontsize=14, pad=12)
frame(ax)
fig.text(0.1, 0.012, SOURCE + "\nRunning total of each year's emissions from 1960, "
         "the first year in the data.", color=MUTED, fontsize=8.5)
fig.subplots_adjust(left=0.13, right=0.97, top=0.86, bottom=0.165)
fig.savefig("against.png")
plt.close(fig)

print(f"crossing x={xc:.2f} y={yc:.0f}; cumulative 2018 (bn t):",
      cum.loc[2018].round(0).to_dict())
