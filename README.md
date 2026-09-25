# yinuoyin.com

Source for my personal website: selected data science work in real estate investing, geospatial modeling, and public research.

Plain HTML/CSS, no build step. Served with GitHub Pages at https://www.yinuoyin.com.

## Layout

```
index.html              home: hero, selected work, experience, contact
work/*.html             one page per case study
assets/css/style.css    the only stylesheet
assets/img/             SVG art and figures
scripts/make_art.py     regenerates the decorative SVGs (synthetic shapes, no data)
```

Preview locally: `python3 -m http.server` in this folder, then open http://localhost:8000.

## Content rules

- No vendor names, internal model names, or performance numbers from current work.
- Charts are illustrative and built from synthetic data.
- Raw source material lives in `private/`, which is git-ignored and never committed.

## Credits

- US outline: [us-atlas](https://github.com/topojson/us-atlas) (ISC license), simplified in `scripts/data/`.
