"""Rebuild the 2018 Cargo portfolio (yinuoyin.cargo.site) as static pages.

Input : private/cargo/*.html + *_files/ saved from the browser ("Webpage, Complete")
Output: archive/index.html, archive/<Slug>/index.html, archive/img/..., archive/assets/cargo.css

Keeps the rendered page markup and Cargo's layout CSS so pages look the same,
removes Cargo's scripts/editor UI, swaps licensed Cargo fonts for close free
Google Fonts, and rewrites links so everything stays inside /archive/.
"""
import re, shutil, sys, html
from pathlib import Path

SRC = Path(sys.argv[1])            # .../private/cargo
OUT = Path(sys.argv[2])            # .../archive
SITE = "https://yinuoyin.cargo.site/"

PAGES = {
    "Main_Page.html": "",
    "Rebalancing the Bikes - Yinuo Yin.html": "Rebalancing-the-Bikes",
    "Visualizing Green & Yellow Taxi Trips to Airports in NYC - Yinuo Yin.html": "Visualizing-Green-Yellow-Taxi-Trips-to-Airports-in-NYC",
    "Chicago Crime Risk Terrain Model - Yinuo Yin.html": "Chicago-Crime-Risk-Terrain-Model",
    "Animated Choropleth Map of Philadelphia Housing Tenure - Yinuo Yin.html": "Animated-Choropleth-Map-of-Philadelphia-Housing-Tenure",
    "Seasonal and Spatial Variation in Burglary Incidents in Philadelphia - Yinuo Yin.html": "Seasonal-and-Spatial-Variation-in-Burglary-Incidents-in-Philadelphia",
    "Dunkin’ Donuts Business Profile in Philadelphia - Yinuo Yin.html": "Dunkin-Donuts-Business-Profile-in-Philadelphia",
    "Hedonic Home Price Prediction - Yinuo Yin.html": "Hedonic-Home-Price-Prediction",
    "Sentiment and Emoji Analysis through Twitter API_ American Airlines vs. United Airlines - Yinuo Yin.html": "Sentiment-and-Emoji-Analysis-through-Twitter-API-American-Airlines-vs",
    "A Guide for You - Philadelphia Farmers Market - Yinuo Yin.html": "A-Guide-for-You-Philadelphia-Farmers-Market",
    "Condo Price Per Square Foot Near Rittenhouse Square - Yinuo Yin.html": "Condo-Price-Per-Square-Foot-Near-Rittenhouse-Square",
    "Urban Growth Boundary (UGB) - Yinuo Yin.html": "Urban-Growth-Boundary-UGB",
}
PROJECT_SLUGS = set(v for v in PAGES.values() if v)
# tag/category pages on Cargo were auto-generated filters; send them home
CUR_FILES = ""
HOME_ALIASES = {"", "Overview", "Dimensionality", "Illustration", "Cartography", "Hedonic-Home-Price-Prediction-Boston-MA"}

FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Overpass:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">')

def swap_fonts(css):
    css = css.replace('"Big Caslon FB"', '"Libre Caslon Text"').replace("Big Caslon FB", "Libre Caslon Text")
    css = re.sub(r'\bInterstate\b', 'Overpass', css)
    return css

def clean(s, slug, depth):
    up = "../" * depth
    # remove scripts, noscripts, editor/toolset, loading spinner, iframes injected by Cargo editor
    s = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<iframe id="following-frame".*?</iframe>', '', s, flags=re.S)  # hidden Cargo 'follow' widget
    s = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', s, flags=re.S)
    s = re.sub(r'<div id="toolset".*?</div>\s*</div>', '', s, count=1, flags=re.S)
    s = re.sub(r'<div class="loading"[^>]*>.*?</svg>\s*</div>\s*</div>\s*</div>', '', s, count=1, flags=re.S)
    # remove the licensed Cargo webfont stylesheet block (served for cargo.site only)
    s = re.sub(r'<style[^>]*>\s*/\*\s*\* This CSS file has been generated and is served by Cargo.*?</style>', '', s, flags=re.S)
    # head clean-up
    s = re.sub(r'<link[^>]*(preconnect|preload|shortcut icon|application/rss\+xml)[^>]*>', '', s)
    s = re.sub(r'<link href="[^"]*/stylesheet" id="member_stylesheet"[^>]*>', f'<link href="{up}assets/cargo.css" rel="stylesheet">', s)
    s = re.sub(r'<meta[^>]*(og:|twitter:|name="description")[^>]*>', '', s)
    s = s.replace('</head>', f'<meta name="robots" content="noindex">\n<link rel="icon" href="{up}../assets/img/favicon.svg" type="image/svg+xml">\n{FONT_LINK}\n<style>.scroll-transition-fade{{opacity:1!important;transform:none!important}}</style>\n</head>', 1)
    s = s.replace('</body>', f'<script src="{up}assets/slideshow.js"></script>\n</body>', 1)
    s = swap_fonts(s)

    # links
    def fix_link(m):
        url = m.group(1)
        path = url[len(SITE):] if url.startswith(SITE) else url[len("https://yinuoyin.com/"):]
        path = path.split("#")[0].strip("/")
        if path == "rss":
            return 'href="#"'
        if path in HOME_ALIASES or path not in PROJECT_SLUGS:
            return f'href="{up or "./"}"'
        return f'href="{up}{path}/"'
    s = re.sub(r'href="((?:https://yinuoyin\.cargo\.site/|https://yinuoyin\.com/)[^"]*)"', fix_link, s)
    # the Info page is not part of the archive: drop the INFO link from the header
    s = re.sub(r'<h1><a href="https://yinuoyin\.cargo\.site/Info" rel="history">INFO</a></h1>', '', s)
    s = re.sub(r'<h1><a href="[./]*" rel="history">INFO</a></h1>', '', s)
    # Cargo's script kept these links in the same tab; without it, target=_blank opens a
    # new tab, so drop it from links that stay inside the archive
    s = re.sub(r'(<a href="(?!https?:|mailto:|//)[^"]*"[^>]*?)\s+target="_blank"', r'\1', s)
    s = re.sub(r'\sdata-src="https://freight\.cargo\.site[^"]*"', '', s)
    # images that were still lazy (not loaded) when the page was saved: point them at
    # local copies placed in private/cargo/extra/ (downloaded separately)
    def fix_lazy(m):
        tag = m.group(0)
        mm = re.search(r'data-lazy(?:-src)?="//freight\.cargo\.site/[^"]*/([^"/]+)"', tag)
        if not mm or re.search(r'src="(\.\./)*img/', tag):
            return tag
        name = mm.group(1)
        extra = SRC / "extra" / name
        if not extra.exists():  # sometimes the file was saved even though the tag was still lazy
            found = sorted((SRC / CUR_FILES).glob(name))
            extra = found[0] if found else extra
        if extra.exists():
            dest = OUT / "img" / (slug or "home"); dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(extra, dest / name)
            new_src = f"{up}img/{slug or 'home'}/{name}"
        else:  # not downloaded yet: keep pointing at Cargo's image server
            print("  missing local copy, using Cargo URL:", name)
            new_src = "https:" + re.sub(r"/w/\d+/", "/t/original/", mm.group(0).split('"')[1])
        tag = re.sub(r'\ssrc="[^"]*"', '', tag)
        tag = re.sub(r'data-lazy(?:-src)?="[^"]*"', f'src="{new_src}"', tag, count=1)
        tag = re.sub(r'\sdata-lazy(?:-src)?="[^"]*"', '', tag)
        return tag
    s = re.sub(r'<img[^>]*data-lazy[^>]*>', fix_lazy, s)
    # standalone images: Cargo's script sized them in pixels for the window they were
    # saved in; size them as a share of their column instead (Cargo's "scale" setting)
    def fix_size(m):
        tag = m.group(0)
        if 'width_o=' not in tag or 'display: none' in tag:
            return tag
        sc = re.search(r'data-scale="(\d+)"', tag)
        pct = sc.group(1) if sc else "100"
        tag = re.sub(r'\sstyle="[^"]*"', '', tag)
        wo = re.search(r'width_o="(\d+)"', tag).group(1)
        return tag[:-1] + f' style="width:{pct}%;max-width:{wo}px;height:auto">'
    s = re.sub(r'<img[^>]*>', fix_size, s)
    # hidden image with no source on the home page
    s = re.sub(r'<img[^>]*src_o="[^"]*"[^>]*display: none[^>]*>', '', s)
    return s

def copy_images(s, src_html, slug, depth):
    files_dir_name = src_html.stem + "_files"
    dest = OUT / "img" / (slug or "home")
    dest.mkdir(parents=True, exist_ok=True)
    up = "../" * depth
    def fix_src(m):
        rel = html.unescape(m.group(1))
        name = rel.split("/")[-1]
        p = SRC / files_dir_name / name
        if not p.exists():
            return m.group(0)
        safe = re.sub(r'[^A-Za-z0-9._-]', '_', name)
        shutil.copy2(p, dest / safe)
        return f'src="{up}img/{slug or "home"}/{safe}"'
    return re.sub(r'src="(\./[^"]+_files/[^"]+\.(?:png|PNG|jpe?g|JPE?G|gif|GIF|webp|svg|mp4))"', fix_src, s)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    css = (SRC / "Main_Page_files" / "stylesheet").read_text(encoding="utf-8")
    (OUT / "assets" / "cargo.css").write_text(swap_fonts(css), encoding="utf-8")
    shutil.copy2(Path(__file__).parent / "archive_static" / "slideshow.js", OUT / "assets" / "slideshow.js")
    for fname, slug in PAGES.items():
        src = SRC / fname
        s = src.read_text(encoding="utf-8")
        depth = 1 if slug else 0
        global CUR_FILES
        CUR_FILES = src.stem + "_files"
        s = copy_images(s, src, slug, depth)
        s = clean(s, slug, depth)
        out = OUT / slug / "index.html" if slug else OUT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(s, encoding="utf-8")
        print("wrote", out.relative_to(OUT))

def make_info():
    """The Info page was not saved from the browser; rebuild it from a project page
    template with the content copied from the live Cargo page."""
    s = (OUT / "Urban-Growth-Boundary-UGB" / "index.html").read_text(encoding="utf-8")
    body = (Path(__file__).parent / "archive_static" / "info_content.html").read_text(encoding="utf-8")
    s = s.replace("<title>Urban Growth Boundary (UGB) - Yinuo Yin</title>", "<title>Info - Yinuo Yin</title>")
    start = s.index('data-ce-model-id="2466723">') + len('data-ce-model-id="2466723">')
    end = s.index("</bodycopy>", start)
    end = s.rindex("</div>", start, end)
    s = s[:start] + "\n" + body + "\t\t\t\t" + s[end:]
    # this page used a narrower 70% content column on Cargo
    s = s.replace('[local-style="2466723"] .container_width {\n}', '[local-style="2466723"] .container_width {\n\twidth: 70%;\n}', 1)
    s = re.sub(r'\s(width_o|height_o)="[^"]*"', '', s)
    s = s.replace('padding-top: 149.812px; padding-bottom: 149.484px;', 'padding-top: 106.203px; padding-bottom: 142.156px;')
    (OUT / "Info").mkdir(exist_ok=True)
    (OUT / "Info" / "index.html").write_text(s, encoding="utf-8")
    print("wrote Info/index.html")

if __name__ == "__main__":
    main()
