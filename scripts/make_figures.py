"""Generate the illustrative charts used in the case studies.

All data here is SYNTHETIC. The charts explain techniques; they do not show
real results. Run from the repo root:  python3 scripts/make_figures.py
Requires: numpy, matplotlib.
"""
from pathlib import Path
import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", message="findfont")
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

# Palette (validated: lightness band, chroma floor, CVD separation, contrast)
ACCENT = "#b4491f"   # series 1 - terracotta
BLUE = "#2f6f9f"     # series 2 - steel blue
QUIET = "#c9c4bd"    # context marks
INK = "#161616"
MUTED = "#5c5c5c"
GRID = "#e4e2de"

plt.rcParams.update({
    "svg.fonttype": "none",            # keep text as text; the page's fonts apply
    "font.family": ["Rubik", "DejaVu Sans"],
    "font.size": 10.5,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.titlesize": 11.5,
    "axes.titleweight": "semibold",
    "axes.titlecolor": INK,
    "axes.titlelocation": "left",
    "axes.titlepad": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "lines.linewidth": 2,
    "lines.solid_capstyle": "round",
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- single-family

def sfr_matching():
    """Left: homes in one census tract, grouped into matched cells.
    Right: sales inside one cell over time form 'same house' pairs."""
    rng = np.random.default_rng(11)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.3), gridspec_kw={"width_ratios": [1, 1.25]})

    n = 70
    xy = rng.uniform(0, 1, size=(n, 2))
    cell = rng.choice([0, 1, 2], size=n, p=[0.2, 0.2, 0.6])
    for k, color, label in [(2, QUIET, "Other cells"), (1, BLUE, "Cell B"), (0, ACCENT, "Cell A")]:
        m = cell == k
        a.scatter(xy[m, 0], xy[m, 1], s=46, color=color, edgecolor="white", linewidth=1.5, label=label, zorder=3)
    a.set_title("One tract, homes grouped into cells")
    a.set_xticks([]); a.set_yticks([]); a.grid(False)
    for s in a.spines.values():
        s.set_visible(True); s.set_color(GRID)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=9.5, handletextpad=0.2, columnspacing=1)
    a.text(0.5, -0.2, "cell = similar age · bedrooms · living area", transform=a.transAxes,
           ha="center", color=MUTED, fontsize=9)

    # Sales inside Cell A over time
    years = np.linspace(2012.3, 2023.7, 12) + rng.uniform(-0.3, 0.3, 12)
    trend = 100 * np.exp(0.055 * (years - 2012))
    price = trend * np.exp(rng.normal(0, 0.05, len(years)))
    b.plot(years, price, color=ACCENT, linewidth=1.2, alpha=0.45, zorder=2)
    b.scatter(years, price, s=48, color=ACCENT, edgecolor="white", linewidth=1.5, zorder=3)
    b.set_title("Cell A sales form \"same house\" pairs")
    b.set_ylabel("Sale price (index, illustrative)")
    b.set_xlim(2011.5, 2024.5)
    i = 5
    b.annotate("consecutive sales of\ndifferent homes in the\nsame cell = one pair",
               xy=((years[i] + years[i + 1]) / 2, (price[i] + price[i + 1]) / 2),
               xytext=(2012.2, price.max() * 0.93), fontsize=9, color=MUTED,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-matching.svg")


def sfr_index():
    """Same-store growth index for prices and rents (synthetic metro)."""
    t = np.arange(2010, 2024.01, 0.25)
    rng = np.random.default_rng(4)
    g_price = np.where(t < 2012, -0.035, np.where(t < 2020, 0.06, np.where(t < 2022.5, 0.16, 0.01)))
    g_rent = np.where(t < 2012, 0.01, np.where(t < 2020, 0.035, np.where(t < 2022.5, 0.09, 0.03)))
    price = 100 * np.exp(np.cumsum(g_price * 0.25 + rng.normal(0, 0.004, len(t))))
    rent = 100 * np.exp(np.cumsum(g_rent * 0.25 + rng.normal(0, 0.002, len(t))))

    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.plot(t, price, color=ACCENT, label="Price index")
    ax.plot(t, rent, color=BLUE, label="Rent index")
    ax.axhline(100, color=MUTED, linewidth=0.8)
    for y, lab in [(price[-1], "Price"), (rent[-1], "Rent")]:
        ax.text(t[-1] + 0.25, y, lab, va="center", color=INK, fontsize=10)
    ax.set_xlim(2010, 2025.3)
    ax.set_ylabel("Index (2010 = 100)")
    ax.set_title("Same-store growth index, one metro (synthetic)")
    ax.legend(loc="upper left", fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig-sfr-index.svg")


def sfr_forecast():
    """Why the forecast target is normalized across metros."""
    rng = np.random.default_rng(21)
    t = np.arange(2012, 2024.01, 0.5)
    national = 5 + 4 * np.sin((t - 2012) / 2.2) + np.where((t > 2020) & (t < 2022.5), 8, 0)
    k = 10
    tilt = np.linspace(-1.8, 1.8, k)
    rng.shuffle(tilt)
    raw = national[None, :] + tilt[:, None] + rng.normal(0, 0.35, (k, len(t)))
    z = (raw - raw.mean(0)) / raw.std(0)
    hi, lo = int(np.argmax(tilt)), int(np.argmin(tilt))

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.2))
    for ax, data, title, ylab in [
        (a, raw, "Raw target: mostly the national cycle", "Price growth, % (synthetic)"),
        (b, z, "Normalized target: who beats the average", "Growth vs. all metros (z-score)"),
    ]:
        for i in range(k):
            if i in (hi, lo):
                continue
            ax.plot(t, data[i], color=QUIET, linewidth=1.2)
        ax.plot(t, data[hi], color=ACCENT, label="Outperforming metro")
        ax.plot(t, data[lo], color=BLUE, label="Lagging metro")
        ax.set_title(title)
        ax.set_ylabel(ylab)
        ax.set_xticks([2012, 2016, 2020, 2024])
    b.axhline(0, color=MUTED, linewidth=0.8)
    handles, labels = a.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=9.5, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.06, 1, 1), w_pad=2.5)
    save(fig, "fig-sfr-forecast.svg")


def sfr_simulation():
    """Left: rank candidates by forecast IRR and buy until the budget runs out.
    Right: simulated portfolio vs. a benchmark over backtest periods."""
    rng = np.random.default_rng(8)
    n = 36
    irr = np.sort(rng.normal(9, 2.2, n))[::-1]
    cost = rng.uniform(0.6, 1.4, n)
    budget = 12.0
    bought = np.cumsum(cost) <= budget
    cut = int(bought.sum())

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.3), gridspec_kw={"width_ratios": [1.2, 1]})
    a.bar(np.arange(n), irr, width=0.72, color=np.where(bought, ACCENT, QUIET), linewidth=0)
    a.axvline(cut - 0.5, color=INK, linewidth=1, linestyle=(0, (3, 3)))
    a.text(cut - 0.1, irr.max() * 0.98, "budget\nexhausted", fontsize=9, color=INK, va="top")
    a.set_title("Rank by forecast IRR, buy from the top")
    a.set_ylabel("Forecast IRR, % (synthetic)")
    a.set_xlabel("Candidate homes, ranked")
    a.set_xticks([])
    a.set_ylim(0, irr.max() * 1.1)
    a.grid(axis="x", visible=False)

    p = np.arange(1, 9)
    bench = 10 + np.cumsum(rng.normal(0.1, 0.35, len(p)))
    port = bench + 1.4 + rng.normal(0, 0.35, len(p))
    b.plot(p, bench, color=BLUE, label="Benchmark owners")
    b.plot(p, port, color=ACCENT, label="Simulated portfolio")
    b.scatter(p, port, s=30, color=ACCENT, edgecolor="white", linewidth=1.5, zorder=3)
    b.scatter(p, bench, s=30, color=BLUE, edgecolor="white", linewidth=1.5, zorder=3)
    b.set_title("Backtest vs. realized owner returns")
    b.set_xlabel("Backtest period")
    b.set_ylabel("Median IRR (illustrative)")
    b.set_yticklabels([])
    b.set_xticks(p)
    b.legend(loc="lower right", fontsize=9.5)
    b.set_ylim(bench.min() - 2.5, port.max() + 0.8)
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-simulation.svg")


if __name__ == "__main__":
    sfr_matching()
    sfr_index()
    sfr_forecast()
    sfr_simulation()
