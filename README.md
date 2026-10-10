# Sarawak.News

Hub for [Sarawak.News](https://nazirulhafiy.github.io/sarawak-news-hub/): independent Sarawak sites, in one place. Each site links to its sources.

Two cards:

- [AI.Sarawak.News](https://ai.sarawak.news/) — source-linked coverage
- [Bantuan.Sarawak.News](https://bantuan.sarawak.news/) — an independent directory of Sarawak government assistance

This is not a government website. It does not use the `sarawak.news` hostname. That needs Nazirul’s approval. There is no `CNAME` and this repo does not change DNS.

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

`SITE_URL` overrides the canonical origin. The default is `https://nazirulhafiy.github.io/sarawak-news-hub/`.

## Build

`scripts/build.py` fetches live counts, renders `dist/index.html` and `dist/about.html`, and copies `site/style.css`, `site/app.js`, and `site/fonts/` (Geist variable font and the SIL OFL licence). The font is preloaded and uses `font-display: swap`, with system-ui in the fallback stack.

If a fetch fails, that site keeps the last values in `data/counts.json`. The build still finishes. A successful fetch updates `data/counts.json` when the numbers changed.

### Data sources

| Site | Counts | Updated date |
| --- | --- | --- |
| AI.Sarawak.News | Homepage HTML: one `<article>` per story, and `data-section-filter` values other than `all` for categories. The All badge must match the article count. | `<time datetime>` inside `.updated` on the homepage |
| Bantuan.Sarawak.News | [`schemes.json`](https://bantuan.sarawak.news/schemes.json): length is the scheme count, distinct `group` values are the categories | `<time datetime>` inside `.updated` on the homepage |

There is no runtime request for these numbers.

## Deploy

`.github/workflows/build.yml` runs the tests, builds `dist/`, and deploys that folder with GitHub Pages.

- Push to `main` deploys.
- Pull requests build and test, and do not deploy.
- A daily schedule (`0 0 * * *`, 08:00 in Sarawak) rebuilds so the counts stay current.
- `workflow_dispatch` rebuilds `main` as well.

The Pages site is the project URL above. Do not add a custom domain until Nazirul approves it.

## Map

The hero outline is Natural Earth 1:10m admin-1 for Sarawak, public domain ([terms](https://www.naturalearthdata.com/about/terms-of-use/)). The simplified path is `data/sarawak-path.txt`. Projection notes are in `data/sarawak-proj.json`. The footer says “Map: Natural Earth”. Details are in `docs/design.md`.
