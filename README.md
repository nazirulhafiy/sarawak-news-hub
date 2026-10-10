# Sarawak.News

Hub for [Sarawak.News](https://sarawak.news/): independent Sarawak sites, in one place. Each site links to its sources.

Two cards:

- [AI.Sarawak.News](https://ai.sarawak.news/) — source-linked coverage
- [Bantuan.Sarawak.News](https://bantuan.sarawak.news/) — an independent directory of Sarawak government assistance

This is not a government website. It is live at [https://sarawak.news/](https://sarawak.news/). The repo `CNAME` is `sarawak.news`, and the build copies that file into `dist/CNAME` for GitHub Pages. Pages, CSS, JS, and the font use relative paths, so they resolve at the domain root.

`design-handoff/` is Design Bot’s reference for layout A. The build does not publish it.

## Documentation

- `docs/design.md` — colour, type, theme, the H1 map hero, cards, and the docs check
- `AGENTS.md` — docs must ship with design or behaviour changes

## Run

The build uses Python 3 and the standard library only.

```bash
python3 scripts/build.py
python3 -m http.server 43123 --directory dist
```

Open `http://127.0.0.1:43123/`.

Checks:

```bash
python3 -m unittest discover -s tests -v
```

The default canonical origin is `https://sarawak.news/`. `SITE_URL` overrides it. An empty `SITE_URL` omits the canonical and `og:url` tags.

## Add a site

One object in `data/sites.json` becomes a card. The hero map is only the Sarawak outline: a faint Sarawak-yellow stroke, with no site tiles and no dotted lines. Fields and the two count fetchers are in [docs/design.md](docs/design.md) under “Adding a site”. Put a new Phosphor duotone inner SVG at `site/icons/{icon}.svg` if the card mark is new. Then run the build so `data/counts.json` stores a fallback for that `id`.

`tests/test_build.py` method `test_third_site_renders_card_without_map_tile` adds a dummy site in the test only, and checks that it renders as a card and that the page draws no map tiles. That dummy is not in `data/sites.json`. The Pages workflow runs `python -m unittest discover -s tests -v` on every pull request and on `main`.

## Build

`scripts/build.py` fetches live counts, renders `dist/index.html` and `dist/about.html`, and copies `site/style.css`, `site/app.js`, and `site/fonts/` (Geist variable font and the SIL OFL licence). The font is preloaded and uses `font-display: swap`, with system-ui in the fallback stack.

If a fetch fails, that site keeps the last values in `data/counts.json`. The build still finishes. A successful fetch updates `data/counts.json` when the numbers changed.

### Data sources

Each site’s `counts` block in `data/sites.json` says how to fetch. The two supported values of `counts.via`:

| `via` | Counts | Updated date |
| --- | --- | --- |
| `html-stories` | `counts.page` HTML: one `<article>` per story, and `data-section-filter` values other than `all` for categories. The All badge must match the article count. | `<time datetime>` inside `.updated` on that page |
| `schemes-json` | `counts.json`: array length is the count, distinct `group` values are the categories | `<time datetime>` inside `.updated` on `counts.page` |

AI uses `html-stories` on https://ai.sarawak.news/. Bantuan uses `schemes-json` at https://bantuan.sarawak.news/schemes.json and the updated date on the homepage.

There is no runtime request for these numbers.

## Deploy

`.github/workflows/build.yml` runs the tests, builds `dist/`, and deploys that folder with GitHub Pages.

- Push to `main` deploys.
- Pull requests build and test, and do not deploy.
- A daily schedule (`0 0 * * *`, 08:00 in Sarawak) rebuilds so the counts stay current.
- `workflow_dispatch` rebuilds `main` as well.

GitHub Pages publishes `dist/` at [https://sarawak.news/](https://sarawak.news/). `dist/CNAME` contains `sarawak.news`. Canonical, `og:url`, `robots.txt`, and `sitemap.xml` use that origin.

## Map

The hero outline is Natural Earth 1:10m admin-1 for Sarawak, public domain ([terms](https://www.naturalearthdata.com/about/terms-of-use/)). It is a faint Sarawak-yellow stroke beside the headline, with no site tiles and no dotted lines. The simplified path is `data/sarawak-path.txt`. Projection notes are in `data/sarawak-proj.json`. The footer says “Map: Natural Earth”. Light and dark stroke values are in `docs/design.md`.
