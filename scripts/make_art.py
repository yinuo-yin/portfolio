"""Generate the decorative SVGs (hero art + project thumbnails).
The Data Clinic thumbnail is a synthetic region split into tract-like cells (needs shapely + scipy).

Everything here is illustrative: shapes and curves are synthetic, not data.
Run from the repo root:  python3 scripts/make_art.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#161616"
ACCENT = "#b4491f"
ACCENT_SOFT = "#f4e3db"
SLATE = "#4f6479"
SLATE_B = "#2f6f9f"
LINE = "#d9d5cf"
WASH = "#f6f4f1"


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{label}">\n'
        f'<rect width="{w}" height="{h}" fill="{WASH}"/>\n{body}\n</svg>\n'
    )


def hexagon(cx, cy, r):
    pts = []
    for k in range(6):
        a = math.radians(60 * k + 30)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def hex_field(w, h, r, fill_fn):
    parts = []
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    row = 0
    y = r
    while y < h + r:
        x = (dx / 2 if row % 2 else 0)
        while x < w + dx:
            fill, stroke = fill_fn(x, y)
            parts.append(
                f'<polygon points="{hexagon(x, y, r * 0.96)}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1"/>'
            )
            x += dx
        y += dy
        row += 1
    return "\n".join(parts)


def hero():
    random.seed(7)
    w, h = 520, 420
    hot = [(300, 150), (180, 260), (380, 300)]

    def fill(x, y):
        d = min(math.hypot(x - a, y - b) for a, b in hot)
        if d < 40:
            return ACCENT, "#fff"
        if d < 90:
            return ACCENT_SOFT, "#fff"
        return "#ffffff", LINE

    body = hex_field(w, h, 22, fill)
    # a rising trend line across the map
    pts = []
    for i in range(0, 41):
        x = 30 + i * 11.5
        y = 360 - 180 * (1 - math.exp(-i / 14)) + 10 * math.sin(i / 2.5)
        pts.append(f"{x:.1f},{y:.1f}")
    body += (
        f'\n<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" '
        f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    (OUT / "hero.svg").write_text(svg(w, h, body, "Abstract map of hexagons with a rising trend line"))


def thumb_sfr():
    # rows of little houses, a few highlighted as the selected portfolio
    w, h = 480, 300
    random.seed(3)
    parts = []
    for r in range(4):
        for c in range(8):
            x = 40 + c * 52
            y = 50 + r * 58
            chosen = random.random() < 0.22
            fill = ACCENT if chosen else "#ffffff"
            stroke = ACCENT if chosen else "#b9b3aa"
            parts.append(
                f'<path d="M{x} {y+16} L{x+16} {y} L{x+32} {y+16} V{y+38} H{x} Z" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            )
    (OUT / "thumb-sfr.svg").write_text(svg(w, h, "\n".join(parts), "Grid of houses with selected homes highlighted"))


def thumb_industrial():
    """Technical-style lease-up curves: P(leased by quarter) for two populations."""
    W, H = 480, 300
    x0, x1, y0, y1 = 70, 440, 240, 40            # plot box (y0 = bottom)
    X = lambda q: x0 + (x1 - x0) * q / 12
    Y = lambda p: y0 - (y0 - y1) * p
    mono = 'font-family="Roboto Mono, monospace"'
    parts = []
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        parts.append(f'<line x1="{x0}" y1="{Y(p):.1f}" x2="{x1}" y2="{Y(p):.1f}" stroke="#e4e2de" stroke-width="1"/>')
        parts.append(f'<text x="{x0-8}" y="{Y(p)+4:.1f}" text-anchor="end" {mono} font-size="11" fill="#5c5c5c">{int(p*100)}%</text>')
    for q in (0, 4, 8, 12):
        parts.append(f'<text x="{X(q):.1f}" y="{y0+18}" text-anchor="middle" {mono} font-size="11" fill="#5c5c5c">{q}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#8a847c" stroke-width="1.2"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#8a847c" stroke-width="1.2"/>')
    parts.append(f'<text x="{(x0+x1)/2}" y="{y0+38}" text-anchor="middle" {mono} font-size="11.5" fill="#161616">Quarters since vacant</text>')
    parts.append(f'<text transform="translate(22 {(y0+y1)/2}) rotate(-90)" text-anchor="middle" {mono} font-size="11.5" fill="#161616">P(leased)</text>')
    parts.append(f'<line x1="{X(8):.1f}" y1="{y1}" x2="{X(8):.1f}" y2="{y0}" stroke="{INK}" stroke-width="1" stroke-dasharray="4 4"/>')
    for h0, d, color, lab, dy in [(0.24, 0.02, ACCENT, "New construction", -10), (0.16, 0.03, SLATE_B, "Re-lease", 22)]:
        surv, pts = 1.0, [(X(0), Y(0))]
        for q in range(1, 13):
            surv *= 1 - h0 * math.exp(-d * q)
            pts.append((X(q), Y(1 - surv)))
        parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"/>')
        for x, y in pts[1:]:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color}" stroke="{WASH}" stroke-width="1.5"/>')
        parts.append(f'<text x="{pts[-1][0]-4:.1f}" y="{pts[-1][1]+dy:.1f}" text-anchor="end" font-family="Rubik, system-ui, sans-serif" font-size="12" fill="#161616">{lab}</text>')
    parts.append(f'<text x="{X(8)+5:.1f}" y="{y0-8}" {mono} font-size="10" fill="#161616">8Q</text>')
    (OUT / "thumb-industrial.svg").write_text(svg(W, H, "\n".join(parts), "Lease-up curves: probability a vacant building is leased by quarter, new construction versus re-lease"))


def thumb_urbint():
    """A stylized daily queue of 811 tickets ranked by damage risk (made-up rows)."""
    W, H = 480, 300
    mono = 'font-family="Roboto Mono, monospace"'
    sans = 'font-family="Rubik, system-ui, sans-serif"'
    rows = [
        ("#4417", "Water service repl", 0.94),
        ("#4390", "Road work, trench", 0.88),
        ("#4452", "Pole replacement", 0.71),
        ("#4408", "Landscaping", 0.46),
        ("#4461", "Fence install", 0.31),
        ("#4433", "Hydro-vac locate", 0.14),
        ("#4447", "Sign post", 0.09),
    ]
    x0, top, rh = 36, 62, 30
    parts = [
        f'<text x="{x0}" y="36" {mono} font-size="11" font-weight="600" letter-spacing="1" fill="{ACCENT}">TODAY\'S TICKETS · RANKED BY RISK</text>',
        f'<line x1="{x0}" y1="{top - 10}" x2="{W - 36}" y2="{top - 10}" stroke="{LINE}"/>',
    ]
    for i, (tid, work, r) in enumerate(rows):
        y = top + i * rh
        hot = i < 3
        if hot:
            parts.append(f'<rect x="{x0 - 8}" y="{y - 2}" width="{W - 56}" height="{rh - 4}" rx="6" fill="#ffffff"/>')
        parts.append(f'<text x="{x0}" y="{y + 16}" {mono} font-size="11" fill="#5c5c5c">{i + 1:>2}</text>')
        parts.append(f'<text x="{x0 + 24}" y="{y + 16}" {mono} font-size="11" fill="#5c5c5c">{tid}</text>')
        parts.append(f'<text x="{x0 + 80}" y="{y + 16}" {sans} font-size="12.5" fill="{INK}">{work}</text>')
        bx, bw = 250, 120
        parts.append(f'<rect x="{bx}" y="{y + 7}" width="{bw}" height="10" rx="5" fill="#ebe7e1"/>')
        parts.append(f'<rect x="{bx}" y="{y + 7}" width="{bw * r:.1f}" height="10" rx="5" fill="{ACCENT if hot else "#c9c4bd"}"/>')
        if hot:
            parts.append(f'<rect x="{bx + bw + 14}" y="{y + 3}" width="54" height="18" rx="9" fill="{ACCENT}"/>')
            parts.append(f'<text x="{bx + bw + 41}" y="{y + 16}" text-anchor="middle" {mono} font-size="10" font-weight="600" fill="#ffffff">INSPECT</text>')
    parts.append(f'<text x="{x0}" y="{top + len(rows) * rh + 14}" {mono} font-size="10" fill="#5c5c5c">illustrative · made-up tickets</text>')
    (OUT / "thumb-urbint.svg").write_text(svg(W, H, "\n".join(parts), "A daily list of excavation tickets ranked by damage risk, with the top three marked for inspection"))


def thumb_sfr_map():
    """US map with a dot per 'zip code', shaded by a synthetic IRR field.
    Outline: us-atlas (ISC license), contiguous US, Albers projection."""
    import json
    from matplotlib.path import Path as MPath
    rings = json.loads((Path(__file__).resolve().parent / "data" / "us-nation-albers.json").read_text())["rings"]
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    W, H = 480, 300
    s = min((W - 40) / (x1 - x0), (H - 50) / (y1 - y0))
    ox = (W - s * (x1 - x0)) / 2 - s * x0
    oy = 18 - s * y0
    T = lambda x, y: (ox + s * x, oy + s * y)
    paths = [MPath([T(x, y) for x, y in r]) for r in rings]

    random.seed(5)
    bumps = [(random.uniform(60, 420), random.uniform(40, 250), random.uniform(25, 60), random.uniform(0.5, 1.0)) for _ in range(9)]
    def irr(x, y):
        v = sum(a * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (2 * r * r)) for bx, by, r, a in bumps)
        return v + random.uniform(-0.12, 0.12)
    ramp = ["#f6e2d9", "#eab7a0", "#d98661", "#c4602f", "#8f3413"]  # light -> dark, one hue

    body = []
    for r in rings:
        pts = " ".join(f"{T(x, y)[0]:.1f},{T(x, y)[1]:.1f}" for x, y in r)
        body.append(f'<polygon points="{pts}" fill="#ffffff" stroke="{LINE}" stroke-width="1"/>')
    dots = []
    step = 5.6
    y = 10.0
    row = 0
    while y < H:
        x = 10.0 + (step / 2 if row % 2 else 0)
        while x < W:
            if any(p.contains_point((x, y)) for p in paths):
                dots.append((x, y, irr(x, y)))
            x += step
        y += step * 0.87
        row += 1
    # quantile bins so most zips are mid/low and a few clusters stand out
    vals = sorted(v for _, _, v in dots)
    cuts = [vals[int(q * (len(vals) - 1))] for q in (0.35, 0.62, 0.82, 0.94)]
    for x, y, v in dots:
        k = sum(v > c for c in cuts)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="{ramp[k]}"/>')
    # legend
    lx, ly = W - 150, H - 22
    for i, c in enumerate(ramp):
        body.append(f'<rect x="{lx + 40 + i * 16}" y="{ly - 7}" width="14" height="8" rx="2" fill="{c}"/>')
    body.append(f'<text x="{lx + 34}" y="{ly}" text-anchor="end" font-family="Roboto Mono, monospace" font-size="9" fill="#5c5c5c">IRR low</text>')
    body.append(f'<text x="{lx + 124}" y="{ly}" font-family="Roboto Mono, monospace" font-size="9" fill="#5c5c5c">high</text>')
    (OUT / "thumb-sfr.svg").write_text(svg(W, H, "\n".join(body), "Map of the contiguous US with every zip code shaded by forecast IRR (illustrative)"))


def thumb_clinic():
    """A synthetic region split into tract-like cells (cell edges follow a few
    hidden 'roads'), with some cells merged into highlighted regions. Illustrative only."""
    import numpy as np
    from scipy.spatial import Voronoi
    from shapely.geometry import Polygon, LineString
    from shapely.ops import unary_union

    W, H = 480, 300
    rng = np.random.default_rng(12)
    # irregular outline: a wobbly blob with a flat 'coast' on the right
    ang = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    r = 1 + 0.10 * np.sin(3 * ang + 0.5) + 0.07 * np.sin(7 * ang) + rng.normal(0, 0.025, len(ang))
    ox = 230 + 190 * r * np.cos(ang)
    oy = 150 + 118 * r * np.sin(ang)
    ox = np.minimum(ox, 405 + 12 * np.sin(oy / 9))
    outline = Polygon(np.c_[ox, oy]).buffer(0)

    # seeds: denser in an 'urban' pocket near the coast
    urban = rng.normal([355, 140], [30, 38], (70, 2))
    rural = np.c_[rng.uniform(40, 420, 55), rng.uniform(30, 275, 55)]
    pts = np.r_[urban, rural]
    pts = np.r_[pts, [[-900, -900], [1400, -900], [-900, 1200], [1400, 1200]]]
    vor = Voronoi(pts)
    cells = []
    for i in range(len(pts) - 4):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg:
            continue
        c = Polygon(vor.vertices[reg]).intersection(outline)
        if not c.is_empty and c.area > 30:
            cells.append(c)

    # tract boundaries follow roads: split every cell along the road lines
    from shapely.ops import split
    roads = [LineString([(20, 190), (160, 150), (300, 160), (470, 110)]),
             LineString([(210, 10), (230, 140), (250, 300)]),
             LineString([(300, 160), (330, 300)])]
    split_cells = []
    for c in cells:
        pieces = [c]
        for rd in roads:
            nxt = []
            for pc in pieces:
                try:
                    nxt.extend([g for g in split(pc, rd).geoms if g.area > 8])
                except Exception:
                    nxt.append(pc)
            pieces = nxt
        split_cells.extend(pieces)
    cells = split_cells

    def poly_pts(g):
        geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
        return [" ".join(f"{x:.1f},{y:.1f}" for x, y in gg.exterior.coords) for gg in geoms if gg.geom_type == "Polygon"]

    # a few merged 'regions' highlighted (neighbouring cells unioned)
    order = sorted(range(len(cells)), key=lambda i: cells[i].centroid.x)
    highlight = {}
    picks = [(order[int(len(order) * 0.82)], ACCENT), (order[int(len(order) * 0.35)], SLATE_B),
             (order[int(len(order) * 0.93)], SLATE_B), (order[int(len(order) * 0.6)], ACCENT)]
    for seed, color in picks:
        group = [j for j in range(len(cells)) if cells[j].distance(cells[seed]) < 0.5][:4]
        for j in group:
            highlight.setdefault(j, color)

    fills = [ACCENT_SOFT, "#ffffff", "#d6e3ee", "#ffffff", ACCENT_SOFT]
    parts = []
    for i, c in enumerate(cells):
        fill = highlight.get(i, fills[i % len(fills)])
        for pp in poly_pts(c):
            parts.append(f'<polygon points="{pp}" fill="{fill}" stroke="#8a847c" stroke-width="0.9" stroke-linejoin="round"/>')
    for pp in poly_pts(outline):
        parts.append(f'<polygon points="{pp}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    (OUT / "thumb-clinic.svg").write_text(svg(W, H, "\n".join(parts), "Illustrative region split along roads into tract-like cells, with a few merged regions highlighted"))


if __name__ == "__main__":
    hero()
    thumb_sfr_map()
    thumb_industrial()
    thumb_urbint()
    thumb_clinic()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
