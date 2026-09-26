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


def sfr_validation():
    """Left: matched cells are far more homogeneous than the tract as a whole.
    Right: index growth vs. a published house price index."""
    rng = np.random.default_rng(5)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.2))
    tract_cv = rng.gamma(9, 0.035, 400)
    cell_cv = rng.gamma(6, 0.018, 400)
    bins = np.linspace(0, 0.7, 36)
    a.hist(tract_cv, bins=bins, color=QUIET, label="Whole tract", rwidth=0.9)
    a.hist(cell_cv, bins=bins, color=ACCENT, alpha=0.9, label="Matched cell", rwidth=0.9)
    a.set_title("Spread within groups (lower is better)")
    a.set_xlabel("Coefficient of variation, price/sq ft")
    a.set_ylabel("Number of groups")
    a.legend(fontsize=9.5)
    a.grid(axis="x", visible=False)

    x = rng.normal(4, 4, 160)
    y = 0.95 * x + rng.normal(0, 1.4, 160)
    r2 = np.corrcoef(x, y)[0, 1] ** 2
    lim = (-8, 16)
    b.plot(lim, lim, color=MUTED, linewidth=0.8)
    b.scatter(x, y, s=22, color=BLUE, edgecolor="white", linewidth=1, zorder=3)
    b.set_xlim(lim); b.set_ylim(lim)
    b.set_title("Index growth vs. published index")
    b.set_xlabel("Published index, annual growth %")
    b.set_ylabel("Our index, annual growth %")
    b.text(-7, 13.5, f"R² = {r2:.2f} (synthetic)", fontsize=9.5, color=INK)
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-validation.svg")


def sfr_backtest():
    """Left: walk-forward backtest windows. Right: a weighted ensemble gives
    steadier rankings than any single member (synthetic)."""
    rng = np.random.default_rng(12)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1, 1.1]})
    folds = 6
    for k in range(folds):
        y = folds - k
        a.barh(y, 6 + k, left=0, height=0.55, color="#d6e3ee")
        a.barh(y, 1, left=6 + k, height=0.55, color=ACCENT)
    a.set_yticks(range(1, folds + 1)); a.set_yticklabels([f"Fold {folds - i + 1}" for i in range(1, folds + 1)])
    a.set_xticks([]); a.set_xlabel("Time →")
    a.set_title("Walk-forward backtest")
    a.grid(False)
    a.text(0.2, folds + 0.62, "train on the past", fontsize=9, color=MUTED)
    a.text(6.2, folds + 0.62, "test on the next period", fontsize=9, color=ACCENT)
    a.set_ylim(0.4, folds + 1.0)

    t = np.arange(1, 21)
    members = [0.45 + rng.normal(0, 0.14, len(t)) for _ in range(5)]
    for m in members:
        b.plot(t, m, color=QUIET, linewidth=1.2)
    ens = 0.55 + rng.normal(0, 0.04, len(t))
    b.plot(t, ens, color=ACCENT, label="Weighted ensemble")
    b.plot([], [], color=QUIET, linewidth=1.2, label="Single models")
    b.set_ylim(0, 1)
    b.set_title("Ranking accuracy by test period")
    b.set_xlabel("Test period")
    b.set_ylabel("Rank correlation (synthetic)")
    b.legend(loc="lower right", fontsize=9.5)
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-backtest.svg")


def sfr_avm():
    """Left: raw prices mix market trend, neighborhood level and the home itself.
    Right: after removing tract level and market trend, what is left is the
    property premium, which a hedonic model explains with home features."""
    rng = np.random.default_rng(31)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.2))
    n = 90
    t = rng.uniform(2014, 2024, n)
    tract = rng.choice([0, 1], n)
    sqft = rng.uniform(1100, 2800, n)
    premium = 0.00022 * (sqft - 1900) + rng.normal(0, 0.06, n)
    level = np.where(tract == 1, 0.35, 0.0)
    trend = 0.06 * (t - 2014)
    price = 250 * np.exp(level + trend + premium)
    for k, color, lab in [(0, BLUE, "Tract A"), (1, ACCENT, "Tract B")]:
        m = tract == k
        a.scatter(t[m], price[m], s=24, color=color, edgecolor="white", linewidth=1, label=lab, zorder=3)
    a.set_title("Raw sale prices")
    a.set_ylabel("Sale price, $K (synthetic)")
    a.legend(fontsize=9.5, loc="upper left")

    b.scatter(sqft, premium * 100, s=24, color=MUTED, edgecolor="white", linewidth=1, zorder=3)
    xs = np.linspace(1100, 2800, 2)
    b.plot(xs, 0.022 * (xs - 1900), color=ACCENT, label="Hedonic fit")
    b.axhline(0, color=MUTED, linewidth=0.8)
    b.set_title("After removing tract and market trend")
    b.set_xlabel("Living area, sq ft")
    b.set_ylabel("Property premium, %")
    b.legend(fontsize=9.5, loc="upper left")
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-avm.svg")


def sfr_returns():
    """From gross rent yield to IRR for one zip code (illustrative numbers)."""
    steps = [
        ("Gross rent\nyield", 8.0, "total"),
        ("Vacancy and\nmanagement", -1.2, "minus"),
        ("Property\ntax", -1.4, "minus"),
        ("Capex", -0.9, "minus"),
        ("Insurance\nand other", -0.5, "minus"),
        ("Net yield", None, "total"),
        ("Forecast\nappreciation", 4.3, "plus"),
        ("IRR\n(simplified)", None, "total"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    level = 0.0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "total":
            if v is not None:
                level = v
            ax.bar(i, level, width=0.6, color=ACCENT)
            ax.text(i, level + 0.2, f"{level:.1f}%", ha="center", fontsize=9.5, color=INK)
        else:
            bottom = level + min(v, 0)
            ax.bar(i, abs(v), bottom=bottom, width=0.6, color=BLUE if v > 0 else QUIET)
            ax.text(i, level + max(v, 0) + 0.2, f"{v:+.1f}", ha="center", fontsize=9.5, color=MUTED)
            level += v
    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([s[0] for s in steps], fontsize=9)
    ax.set_ylabel("% of home value (illustrative)")
    ax.set_ylim(0, 10.5)
    ax.set_title("From rent to return, one zip code (illustrative)")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "fig-sfr-returns.svg")


def sfr_simulation():
    """Left: rank candidates by forecast IRR; buy top-down until the budget runs
    out, skipping homes once a market hits its cap. Right: simulated portfolio
    vs. institutional owners over backtest periods (synthetic)."""
    rng = np.random.default_rng(8)
    n = 36
    irr = np.sort(rng.normal(9, 2.2, n))[::-1]
    cost = rng.uniform(0.6, 1.4, n)
    market = rng.choice(list("ABCDE"), n, p=[0.35, 0.2, 0.2, 0.15, 0.1])
    cap, budget = 3, 11.0
    status, spent, held = [], 0.0, {}
    for i in range(n):
        if spent + cost[i] > budget:
            status.append("left")
        elif held.get(market[i], 0) >= cap:
            status.append("capped")
        else:
            status.append("bought"); spent += cost[i]; held[market[i]] = held.get(market[i], 0) + 1
    status = np.array(status)
    cut = int(np.max(np.where(status != "left")[0])) + 1

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(n)
    m = status == "bought"
    a.bar(x[m], irr[m], width=0.72, color=ACCENT, linewidth=0, label="Bought")
    m = status == "capped"
    a.bar(x[m], irr[m], width=0.72, color="white", edgecolor=ACCENT, hatch="////", linewidth=1, label="Skipped: market cap reached")
    m = status == "left"
    a.bar(x[m], irr[m], width=0.72, color=QUIET, linewidth=0, label="Not bought")
    a.axvline(cut - 0.5, color=INK, linewidth=1, linestyle=(0, (3, 3)))
    a.text(cut - 0.1, irr.max() * 1.08, "budget exhausted", fontsize=9, color=INK, va="top")
    a.set_title("Rank by forecast IRR, buy from the top")
    a.set_ylabel("Forecast IRR, % (synthetic)")
    a.set_xlabel("Candidate homes, ranked", labelpad=2)
    a.set_xticks([])
    a.set_ylim(0, irr.max() * 1.12)
    a.grid(axis="x", visible=False)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, fontsize=8.5, handlelength=1.2, columnspacing=0.8)

    p = np.arange(1, 9)
    bench = 10 + np.cumsum(rng.normal(0.1, 0.35, len(p)))
    port = bench + 1.4 + rng.normal(0, 0.35, len(p))
    b.plot(p, bench, color=BLUE, label="Institutional owners")
    b.plot(p, port, color=ACCENT, label="Simulated portfolio")
    b.scatter(p, port, s=30, color=ACCENT, edgecolor="white", linewidth=1.5, zorder=3)
    b.scatter(p, bench, s=30, color=BLUE, edgecolor="white", linewidth=1.5, zorder=3)
    b.set_title("Backtest vs. institutional owners")
    b.set_xlabel("Backtest period")
    b.set_ylabel("Median IRR (illustrative)")
    b.set_yticklabels([])
    b.set_xticks(p)
    b.legend(loc="lower right", fontsize=9.5)
    b.set_ylim(bench.min() - 2.5, port.max() + 0.8)
    fig.tight_layout(w_pad=2.5)
    save(fig, "fig-sfr-simulation.svg")


# ---------------------------------------------------------------- industrial

def ind_signals():
    """Rolling rank correlation of two signals and their 50/50 blend (synthetic).
    Point: the signals fail at different times, so the blend is steadier."""
    rng = np.random.default_rng(3)
    t = np.arange(0, 100)
    base = 0.55 + 0.12 * np.sin(t / 9)
    shock = np.exp(-((t - 38) ** 2) / 40)
    momentum = base - 0.55 * shock + rng.normal(0, 0.03, len(t))
    occupancy = 0.35 + 0.15 * np.sin(t / 13 + 2) + 0.25 * shock + rng.normal(0, 0.03, len(t))
    blend = 0.5 * momentum + 0.5 * occupancy + 0.08
    k = 4
    sm = lambda x: np.convolve(x, np.ones(k) / k, mode="valid")
    tt = t[k - 1:]
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.plot(tt, sm(momentum), color=BLUE, label="Rent momentum")
    ax.plot(tt, sm(occupancy), color=QUIET, linewidth=2, label="Occupancy forecast")
    ax.plot(tt, sm(blend), color=ACCENT, linewidth=2.6, label="50/50 revenue blend")
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvspan(31, 46, color=GRID, alpha=0.6, linewidth=0)
    ax.text(38.5, 0.93, "market shock", ha="center", fontsize=9, color=MUTED)
    ax.set_ylim(-0.2, 1.0)
    ax.set_xticks([])
    ax.set_xlabel("Backtest quarters (synthetic)")
    ax.set_ylabel("Rank correlation vs.\nrealized 3-yr revenue")
    ax.set_title("Two signals that fail at different times")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=9.5, ncol=3)
    fig.tight_layout()
    save(fig, "fig-ind-signals.svg")


def ind_beta():
    """Beta regression vs. OLS on occupancy bounded in [0, 1] (synthetic)."""
    rng = np.random.default_rng(9)
    x = rng.uniform(-3, 3, 140)
    mu = 1 / (1 + np.exp(-(1.9 + 0.9 * x)))
    phi = 40
    y = rng.beta(mu * phi, (1 - mu) * phi)
    xs = np.linspace(-3.4, 3.4, 200)
    A = np.vstack([np.ones_like(x), x]).T
    b0, b1 = np.linalg.lstsq(A, y, rcond=None)[0]
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.scatter(x, y * 100, s=18, color=QUIET, edgecolor="white", linewidth=0.8, zorder=2)
    ax.plot(xs, (b0 + b1 * xs) * 100, color=BLUE, label="Linear regression (OLS)")
    ax.plot(xs, 100 / (1 + np.exp(-(1.9 + 0.9 * xs))), color=ACCENT, linewidth=2.6, label="Beta regression")
    ax.axhline(100, color=INK, linewidth=1, linestyle=(0, (3, 3)))
    ax.text(-3.35, 102, "100% occupied: a hard ceiling", fontsize=9, color=INK)
    ax.set_ylim(40, 112)
    ax.set_xlabel("Demand driver (standardized, synthetic)")
    ax.set_ylabel("Market occupancy, %")
    ax.set_title("Occupancy is bounded; the model should be too")
    ax.legend(loc="lower right", fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig-ind-beta.svg")


def _leaseup(h0, decay, q):
    h = h0 * np.exp(-decay * q)
    surv = np.cumprod(1 - h)
    return h, 1 - surv


def ind_survival():
    """Discrete-time survival: per-quarter hazard -> cumulative lease-up."""
    q = np.arange(1, 13)
    h_new, c_new = _leaseup(0.24, 0.02, q)
    h_rel, c_rel = _leaseup(0.16, 0.03, q)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.3), gridspec_kw={"width_ratios": [1, 1.2]})
    w = 0.38
    a.bar(q - w / 2, h_new * 100, width=w, color=ACCENT, label="New construction")
    a.bar(q + w / 2, h_rel * 100, width=w, color=BLUE, label="Re-lease")
    a.set_title("Step 1: hazard each quarter")
    a.set_xlabel("Quarters since vacant")
    a.set_ylabel("P(lease this quarter | still vacant), %")
    a.set_xticks([1, 4, 8, 12])
    a.grid(axis="x", visible=False)
    for c, col, lab in [(c_new, ACCENT, "New construction"), (c_rel, BLUE, "Re-lease")]:
        b.plot(np.r_[0, q], np.r_[0, c] * 100, color=col, marker="o", markersize=4.5,
               markeredgecolor="white", markeredgewidth=1.2, label=lab)
    b.axvline(8, color=INK, linewidth=1, linestyle=(0, (3, 3)))
    b.text(8.2, 6, "8-quarter\nhorizon", fontsize=9, color=INK)
    b.set_ylim(0, 100)
    b.set_xticks([0, 4, 8, 12])
    b.set_title("Step 2: roll into a lease-up curve")
    b.set_xlabel("Quarters since vacant")
    b.set_ylabel("P(leased by quarter), %")
    b.text(8.2 + 0.1, c_new[7] * 100 + 3, f"{c_new[7]*100:.0f}%", fontsize=9, color=INK)
    b.text(8.2 + 0.1, c_rel[7] * 100 - 7, f"{c_rel[7]*100:.0f}%", fontsize=9, color=INK)
    h, l = b.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=9.5, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=2.5)
    save(fig, "fig-ind-survival.svg")


def ind_catchment():
    """A 15-minute drive-time catchment around one warehouse (synthetic)."""
    rng = np.random.default_rng(14)
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ang = np.linspace(0, 2 * np.pi, 13)[:-1]
    r = 1 + 0.35 * np.sin(3 * ang) + rng.uniform(-0.15, 0.15, len(ang))
    r[[2, 3]] += 0.6          # stretched along the highway
    r[[8, 9]] += 0.5
    px, py = r * np.cos(ang), r * np.sin(ang)
    ax.fill(np.r_[px, px[0]], np.r_[py, py[0]], color=ACCENT, alpha=0.10, linewidth=0)
    ax.plot(np.r_[px, px[0]], np.r_[py, py[0]], color=ACCENT, linewidth=1.5)
    ax.plot([-2.6, 2.6], [-1.6, 1.9], color=INK, linewidth=3, solid_capstyle="butt")
    ax.text(2.0, 1.95, "highway", fontsize=9, color=INK)
    bx = rng.uniform(-2.5, 2.5, 60); by = rng.uniform(-1.8, 1.8, 60)
    from matplotlib.path import Path as MPath
    inside = MPath(np.c_[px, py]).contains_points(np.c_[bx, by])
    same = rng.random(60) < 0.6
    ax.scatter(bx[inside & same], by[inside & same], s=34, marker="s", color=BLUE, edgecolor="white", linewidth=1, label="Same-subtype buildings (counted)", zorder=3)
    ax.scatter(bx[inside & ~same], by[inside & ~same], s=34, marker="s", facecolor="white", edgecolor=BLUE, linewidth=1.2, label="Other subtypes (excluded)", zorder=3)
    ax.scatter(bx[~inside], by[~inside], s=20, marker="s", color=QUIET, linewidth=0, label="Outside 15 minutes", zorder=2)
    ax.scatter([0], [0], s=160, marker="*", color=ACCENT, edgecolor="white", linewidth=1, zorder=4, label="Subject warehouse")
    ax.scatter([1.9], [-1.25], s=60, marker="^", color=INK, zorder=4)
    ax.text(1.98, -1.5, "port", fontsize=9, color=INK)
    ax.set_xlim(-2.7, 2.9); ax.set_ylim(-1.9, 2.3)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_aspect("equal")
    ax.set_title("15-minute drive-time catchment (illustrative)")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9.5, frameon=False)
    fig.tight_layout()
    save(fig, "fig-ind-catchment.svg")


def ind_terciles():
    """Tercile test: forward rent growth by exposure to an outside signal."""
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    labels = ["Low exposure", "Mid exposure", "High exposure"]
    vals = [3.1, 3.9, 5.2]
    ax.barh(labels[::-1], vals[::-1], height=0.42, color=[ACCENT, QUIET, QUIET])
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 0.08, i, f"{v:.1f}%", va="center", fontsize=9.5, color=INK)
    ax.set_xlim(0, 6.2)
    ax.set_xlabel("Forward 3-year rent growth, annualized (synthetic)")
    ax.set_title("Does the signal separate winners from losers?")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save(fig, "fig-ind-terciles.svg")


if __name__ == "__main__":
    sfr_matching()
    sfr_index()
    sfr_validation()
    sfr_forecast()
    sfr_backtest()
    sfr_avm()
    sfr_returns()
    sfr_simulation()
    ind_signals()
    ind_beta()
    ind_survival()
    ind_catchment()
    ind_terciles()
