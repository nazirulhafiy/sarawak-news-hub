# Sarawak.News

Hub for [Sarawak.News](https://sarawak.news/). The home headline is “Sarawak, made easy.” The sub-line is “Aggregating Sarawak info, all in one place.”

Two cards:

- [AI.Sarawak.News](https://ai.sarawak.news/) — source-linked coverage
- [Bantuan.Sarawak.News](https://bantuan.sarawak.news/) — an independent directory of Sarawak government assistance

This is not a government website. It is live at [https://sarawak.news/](https://sarawak.news/). The repo `CNAME` is `sarawak.news`, and the build copies that file into `dist/CNAME` for GitHub Pages. Pages, CSS, JS, and the font use relative paths, so they resolve at the domain root.

`design-handoff/` is Design Bot’s reference for layout A. The build does not publish it.

## Documentation

- `docs/design.md` — colour, type, theme, the riverfront hero, cards, and the docs check
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

One object in `data/sites.json` becomes a card. The fields are `id`, `name`, `url`, `tag`, `icon`, and `text`. Details are in [docs/design.md](docs/design.md) under “Adding a site”. Put a new Phosphor duotone inner SVG at `site/icons/{icon}.svg` if the card mark is new. The hero is the riverfront line drawing. Adding a site does not change it.

`tests/test_build.py` method `test_third_site_renders_card_without_map_tile` adds a dummy site in the test only, and checks that it renders as a card and that the page draws no map tiles. That dummy is not in `data/sites.json`. The Pages workflow runs `python -m unittest discover -s tests -v` on every pull request and on `main`.

## Build

`scripts/build.py` renders `dist/index.html` and `dist/about.html` from `data/sites.json`, and copies `site/style.css`, `site/app.js`, and `site/fonts/` (Geist variable font and the SIL OFL licence). The font is preloaded and uses `font-display: swap`, with system-ui in the fallback stack. It also copies the F1 favicon from `design-handoff/favicon-F1/` to `dist/favicon.ico`, `dist/favicon.svg`, `dist/apple-touch-icon.png`, and `dist/icon-512.png`. The rest of `design-handoff/` is not published. The build does not fetch the sister sites. Cards show the name, the description, and Visit. The home tab title is `Sarawak.News`. The on-page headline is “Sarawak, made easy.” The sub-line is “Aggregating Sarawak info, all in one place.” Home and About `description`, `og:description`, and `twitter:description` use that sub-line.

## Deploy

`.github/workflows/build.yml` runs the tests, builds `dist/`, and deploys that folder with GitHub Pages.

- Push to `main` deploys.
- Pull requests build and test, and do not deploy.
- `workflow_dispatch` rebuilds `main` by hand.

There is no daily schedule. It only refreshed the count lines, and those lines are gone.

GitHub Pages publishes `dist/` at [https://sarawak.news/](https://sarawak.news/). `dist/CNAME` contains `sarawak.news`. Canonical, `og:url`, `robots.txt`, and `sitemap.xml` use that origin.

## Drawing

The hero drawing is the Kuching riverfront, inlined from `site/hero-art.svg`. The Darul Hana bridge is on the left, the Dewan Undangan Negeri is in the middle, and Gunung Santubong is on the right. There is no boat. It is decorative. Dark mode changes only the line colours. About credits the three traced photos: the DUN by CEphoto (Uwe Aranas), the Darul Hana pylons by Meandkancil2020, and Gunung Santubong by Matthew Anderson Lockhart. The other reference photos, and the licences, are in [docs/SOURCES.md](docs/SOURCES.md) and [docs/design.md](docs/design.md). No photo is published. The footer stays the unaffiliated credit. The favicon is still the F1 tile.