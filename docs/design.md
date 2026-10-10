# Design

The live site is [https://sarawak.news/](https://sarawak.news/). Pages are the static output of `scripts/build.py`, styled by `site/style.css`. This note describes that system.

Every published site is one object in `data/sites.json`. That list drives the card and the map tile together. The current entries are [AI.Sarawak.News](https://ai.sarawak.news/) and [Bantuan.Sarawak.News](https://bantuan.sarawak.news/). There is no PCDS card.

## Type and colour

Type is Geist, then ui-sans-serif, system-ui, and the system sans-serif stack. Geist is the official variable font (weights 100–900), self-hosted under the SIL Open Font License from the vercel/geist-font v1.7.2 release. `site/fonts/OFL.txt` is the licence. The face uses `font-display: swap`. The head preloads `fonts/Geist-Variable.woff2` with `crossorigin`.

Colours are the same tokens as [bantuan.sarawak.news](https://bantuan.sarawak.news/): page white, ink near-black `#111827`, Sarawak red `#d22630`, red ink `#9f1d26`, yellow `#f7c948`, black `#111111`. The body is at most 840px wide. The brief, cards, and footer sit on a 760px rail.

Dark mode sets `html[data-theme="dark"]` and swaps the same tokens: canvas `#0f1115`, card `#171b22`, ink `#f3f5f7`, muted `#aeb6c2`, line `#2c333d`, red `#f15b61`, red ink `#ff8d92`. Icon tiles use a translucent yellow fill and a yellow border. Card description copy is `#374151` in light mode and `#d2d8df` in dark mode.

## Theme

`scripts/build.py` inlines the same boot script as bantuan. Before paint it reads `localStorage` key `sarawak-theme`. `dark` forces dark. `light` forces light. With no stored choice, `prefers-color-scheme: dark` selects dark. `site/app.js` updates the toggle label, persists a click, and follows later system changes only when nothing is stored.

The header is bantuan’s bar: wordmark, red / yellow / black rule, Sites and About, sun-and-moon toggle. Below 560px the links collapse into a menu button. The theme control stays visible.

## Hero

The home hero is layout H1, not a placeholder and not bantuan’s category network.

On a wide page the headline and sub-line sit on the left. The map sits on the right, vertically centred with that text. Below 560px the map moves above the text and centres in the column. The words are fixed:

- Independent Sarawak sites, in one place.
- Each site links to its sources.

The headline is broken onto three lines so it matches H1: “Independent”, “Sarawak sites,”, “in one place.”

The drawing is one inline SVG (`svg.hero-map`, viewBox `0 0 614.7 411.1`). The land is a single filled path from `data/sarawak-path.txt`. It is faint: light mode fill `#e6e9ee` and stroke `#d5dae1`; dark mode fill `#1c222c` and stroke `#465062`. Dotted links (`path.hero-route`) join the tiles. The stroke is `#b7bec7` in light mode and `#8e98a6` in dark mode.

With two sites the link is one curve, bowed northwest, in list order. With three or more, the build draws a straight dotted segment for each edge of a Euclidean minimum spanning tree. Those straight edges do not cross.

Each tile is a 72-by-72 square centred on that site’s `map.x` and `map.y`. The numbers are tidy spots on the outline, not towns. The icon is the Phosphor duotone file `site/icons/{icon}.svg` (MIT), the same yellow tile treatment as bantuan’s category icons. In dark mode the icon stroke turns yellow and the duotone fill drops to opacity 0.45. AI uses `brain` at `(128, 348)`. Bantuan uses `hand-heart` at `(424, 128)`.

The path is Natural Earth 1:10m cultural admin-1 for Sarawak (`MY-13`), public domain. Projection stored in `data/sarawak-proj.json`: `x = (longitude − 109.528436) × 100`, `y = (4.962329 − latitude) × 100`, width 614.7, height 411.1. The footer credit reads “Map: Natural Earth” and links to [naturalearthdata.com](https://www.naturalearthdata.com/). Terms: the Natural Earth dataset is public domain. No permission or attribution is required; the credit is still shown.

## Cards

Cards use the same `data/sites.json` list, in that order. Two columns with a 16px gap, one column below 560px. A third site wraps onto the next row. Each card has the Phosphor tile, the `tag` pill, the name, a count line, the `text`, the hostname of `url`, and a Visit link to `url`.

The count line is `{n} {noun} · {n} {groupNoun}` from that site’s `counts` block. The noun is singular when the number is 1. CSS uppercases the line. Updated dates are fetched and stored in `data/counts.json`. They are not printed on the card.

## Adding a site

Add one object to the `sites` array. Do not edit the template. The next build draws a card and a map tile for it.

| Field | Role |
| --- | --- |
| `id` | Lowercase slug. Key in `data/counts.json`. |
| `name` | Card heading and the tile’s place in the map label. |
| `url` | Visit link. The card domain is the hostname. |
| `tag` | Pill, such as News or Directory. |
| `icon` | File name in `site/icons/` without `.svg`. |
| `text` | Card description. |
| `map.x`, `map.y` | Tile centre on the outline. Not a real place. |
| `counts.via` | `html-stories` or `schemes-json`. |
| `counts.page` | Page whose `.updated time` is the updated date. For `html-stories`, also the page of story cards. |
| `counts.json` | Required for `schemes-json`. Array length is the count. Distinct `group` values are the categories. |
| `counts.noun` | `[singular, plural]` for the main count. |
| `counts.groupNoun` | `[singular, plural]` for the category count. |

`html-stories` counts `<article>` elements and `data-section-filter` values other than `all`. The All badge must match the article count.

To place `map.x` and `map.y`: the viewBox is `0 0 614.7 411.1`, x grows east, and y grows south. The tile is 72 units square around that point, so keep the centre at least 36 units in from the coast and at least 72 units from every other centre. Order is only the card order. The dotted links are computed from the positions.

Run `python3 scripts/build.py` once while the new page answers, so `data/counts.json` gains a fallback row. A later failed fetch keeps that row. A failed fetch with no row stops the build.

## Footer

A rounded credit box, centred: “Built by hafiy.my, an independent publication. Not affiliated with the Sarawak Government.” Under it, the smaller map credit.

## Motion

The brief uses bantuan’s `hero-reveal`: a rise of 18px over 0.85s, easing `cubic-bezier(.22, 1, .36, 1)`. The headline and sub-line use `hero-content-reveal` (10px, 0.7s). The map does not animate on its own. `prefers-reduced-motion: reduce` removes the transform motion.

## Counts and deploy

`scripts/build.py` writes `dist/` only. `design-handoff/` stays in the repo and is not copied. The build copies the repo `CNAME` (`sarawak.news`) into `dist/CNAME`. Canonical and `og:url` on the home page are `https://sarawak.news/`. About uses `https://sarawak.news/about.html`. `robots.txt` and `sitemap.xml` use the same origin. Internal links (`index.html`, `about.html`, `style.css`, `app.js`, `fonts/Geist-Variable.woff2`) are relative, so the site works at the domain root. The scheduled Pages workflow rebuilds daily so the counts can change without a content commit. See `README.md` for the fetch sources and the fallback file.

## Docs check

`.github/workflows/docs-check.yml` runs job `docs-check` on pull requests (`opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`). It diffs the PR with three dots (`base...head`). Watched paths are `site/*`, `scripts/build.py`, `scripts/docs_check_pr.py`, `.github/workflows/*`, `data/sarawak-path.txt`, `data/sarawak-proj.json`, and `data/sites.json`. A change there fails unless `docs/` also changes, or the PR has the `no-docs-needed` label. `data/counts.json` is fetched content and is not watched.
