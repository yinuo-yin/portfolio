"""Generate the decorative SVGs (hero art + project thumbnails).

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
    # two lease-up curves
    w, h = 480, 300
    x0, x1, y0, y1 = 50, 440, 250, 50
    parts = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{LINE}" stroke-width="2"/>',
             f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{LINE}" stroke-width="2"/>']
    for k, color in [(0.22, ACCENT), (0.12, SLATE)]:
        pts = []
        for i in range(0, 61):
            t = i / 60
            p = 1 - math.exp(-k * i / 3)
            pts.append(f"{x0 + t * (x1 - x0):.1f},{y0 - p * (y0 - y1) * 0.95:.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
    (OUT / "thumb-industrial.svg").write_text(svg(w, h, "\n".join(parts), "Two lease-up curves"))


def thumb_urbint():
    # hexagon risk surface
    w, h = 480, 300
    hot = [(150, 110), (340, 190)]

    def fill(x, y):
        d = min(math.hypot(x - a, y - b) for a, b in hot)
        if d < 30:
            return ACCENT, "#fff"
        if d < 75:
            return "#e2a88f", "#fff"
        if d < 120:
            return ACCENT_SOFT, "#fff"
        return "#ffffff", LINE

    (OUT / "thumb-urbint.svg").write_text(svg(w, h, hex_field(w, h, 18, fill), "Hexagon grid shaded by risk"))


def thumb_clinic():
    # irregular polygons split by 'roads'
    w, h = 480, 300
    parts = []
    polys = [
        ("40,40 200,30 230,140 60,160", ACCENT_SOFT),
        ("200,30 440,50 420,120 230,140", "#ffffff"),
        ("60,160 230,140 250,270 50,260", "#ffffff"),
        ("230,140 420,120 440,270 250,270", ACCENT_SOFT),
        ("300,160 380,150 390,230 310,240", ACCENT),
    ]
    for pts, fill in polys:
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    parts.append(f'<path d="M20 150 C 140 140, 300 135, 460 115" fill="none" stroke="{SLATE}" stroke-width="5"/>')
    (OUT / "thumb-clinic.svg").write_text(svg(w, h, "\n".join(parts), "Regions split along roads"))


if __name__ == "__main__":
    hero()
    thumb_sfr()
    thumb_industrial()
    thumb_urbint()
    thumb_clinic()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
