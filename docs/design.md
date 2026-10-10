# Design

The live site is [https://sarawak.news/](https://sarawak.news/). Pages are the static output of `scripts/build.py`, styled by `site/style.css`. This note describes that system.

Every published site is one object in `data/sites.json`. That list drives the cards. The current entries are [AI.Sarawak.News](https://ai.sarawak.news/) and [Bantuan.Sarawak.News](https://bantuan.sarawak.news/). There is no PCDS card. The map is only the Sarawak outline. It does not mark sites.

## Type and colour

Type is Geist, then ui-sans-serif, system-ui, and the system sans-serif stack. Geist is the official variable font (weights 100–900), self-hosted under the SIL Open Font License from the vercel/geist-font v1.7.2 release. `site/fonts/OFL.txt` is the licence. The face uses `font-display: swap`. The head preloads `fonts/Geist-Variable.woff2` with `crossorigin`.

Colours are the same tokens as [bantuan.sarawak.news](https://bantuan.sarawak.news/): page white, ink near-black `#111827`, Sarawak red `#d22630`, red ink `#9f1d26`, yellow `#f7c948`, black `#111111`. The body is at most 840px wide. The brief, cards, and footer sit on a 760px rail.

Dark mode sets `html[data-theme="dark"]` and swaps the same tokens: canvas `#0f1115`, card `#171b22`, ink `#f3f5f7`, muted `#aeb6c2`, line `#2c333d`, red `#f15b61`, red ink `#ff8d92`. Icon tiles use a translucent yellow fill and a yellow border. Card description copy is `#374151` in light mode and `#d2d8df` in dark mode.

## Favicon

Nazirul picked F1, the yellow Sarawak shape on a black rounded tile. The source files live in `design-handoff/favicon-F1/`. The build copies four of them to the root of `dist/` and does not publish the rest of `design-handoff/`:

| Published URL | Source |
| --- | --- |
| `favicon.ico` | `favicon.ico` |
| `favicon.svg` | `f1.svg` |
| `apple-touch-icon.png` | `f1-180.png` |
| `icon-512.png` | `f1-512.png` |

The head links the SVG icon, the `.ico` with `sizes="any"`, the Apple touch icon, and the 512 PNG. `theme-color` is `#ffffff` for `prefers-color-scheme: light` and `#0f1115` for dark. The 16 and 32 pixel extras stay in the handoff folder. `favicon.ico` already carries the small sizes.

## Theme

`scripts/build.py` inlines the same boot script as bantuan. Before paint it reads `localStorage` key `sarawak-theme`. `dark` forces dark. `light` forces light. With no stored choice, `prefers-color-scheme: dark` selects dark. `site/app.js` updates the toggle label, persists a click, and follows later system changes only when nothing is stored.

The header is bantuan’s bar: wordmark, red / yellow / black rule, Sites and About, sun-and-moon toggle. Below 560px the links collapse into a menu button. The theme control stays visible.

## Hero

The home hero follows the centred brief on [bantuan.sarawak.news](https://bantuan.sarawak.news/) and [ai.sarawak.news](https://ai.sarawak.news/). The words are fixed:

- Independent Sarawak sites, in one place.
- Each site links to its sources.

`.brief` is 760px at most, centred, `text-align: center`, with `padding: 42px 8px 36px` and `margin: 32px auto 8px`. The headline is `clamp(36px, 6vw, 48px)`, weight 700, letter-spacing `-1.2px`, line-height `1.02`, `max-width: 680px`, and `margin: 0 auto 16px`. The sub-line is 18px, line-height `1.62`, `max-width: 620px`, centred, in the copy colour (`#374151` light, `#d2d8df` dark). Below 560px the headline is `clamp(2.15rem, 11vw, 3rem)`, the sub-line is 17px, and the brief padding is `32px 0 28px`. The headline wraps on its own. It is not forced onto three lines. The document `<title>`, `og:title`, and `twitter:title` on the home page are `Sarawak.News`. About keeps `<title>About Sarawak.News</title>`.

The Sarawak outline is one inline SVG (`svg.hero-map`, viewBox `0 0 614.7 411.1`) behind that type. `aria-hidden="true"` and `focusable="false"` mark it decorative. `pointer-events: none` and `z-index: 0` keep it off clicks and under the words. The only shape is `path.hero-land` from `data/sarawak-path.txt`. There are no site tiles, icons, or dotted lines. Card icons stay on the cards.

The brief is at least 400px tall on a wide page, and at least 300px below 560px, so the whole outline fits inside the hero. The shape is centred. On a wide page it is `min(72%, 500px)` wide. On a phone it is 92% of the column. `overflow: hidden` is a backstop. The shape ends before the cards.

Fill and stroke are tuned apart, and both are quieter than the previous outline. The target is the faint network behind the headline on [ai.sarawak.news](https://ai.sarawak.news/) (`svg.brief-net` in nazirulhafiy/sarawak-ai-news). That drawing uses one ink for its lines and its dots. The lines are `stroke: currentColor`, `stroke-width: 1.4`, `fill: none`. The dots are `fill: currentColor`. The SVG is 350×320 from a 520×480 viewBox, so the 1.4 stroke paints at about 0.94 CSS pixels. A horizontal mask fades the side toward the words; the strongest ink is the unmasked side.

- Light: `color: #cfd3da`, opacity 0.37, on white. The full ink blends to about `rgb(237, 239, 241)`, contrast 1.15:1. Rendered pixels on that side peak at `rgb(237, 239, 242)`, contrast 1.15:1.
- Dark: `color: #4b5563`, opacity 0.42, on `#0f1115`. The full ink blends to about `rgb(40, 46, 54)`, contrast 1.38:1. Rendered pixels peak at `rgb(38, 43, 50)`, contrast 1.33:1.

The hub keeps Sarawak yellow `#f7c948` instead of that gray. The stroke width is 1.4px in both themes, the same authored width as their lines, with `vector-effect: non-scaling-stroke` and round joins. Stroke opacity is set so the rendered stroke, painted over the fill, lands on that measured peak. The fill stays lighter than the peak. A solid shape at the line’s contrast would cover the hero more than their hairline drawing.

- Light, on white: fill `rgba(247, 201, 72, 0.06)`. Rendered fill pixels sit near `rgb(255, 252, 244)`, about 1.03:1. Stroke opacity 0.26. Rendered stroke pixels peak at `rgb(253, 238, 199)`, 1.15:1.
- Dark, on `#0f1115`: fill `rgba(247, 201, 72, 0.04)`. Rendered fill pixels sit near `rgb(23, 23, 22)`, about 1.05:1. Stroke opacity 0.11. Rendered stroke pixels peak at `rgb(46, 42, 27)`, 1.32:1.

The previous outline was stronger, especially the dark stroke. Measured on the live page before this change: light fill near `rgb(254, 249, 236)` (about 1.05:1) with a 1.75px stroke at opacity 0.50 peaking at `rgb(250, 225, 154)` (1.29:1). Dark fill near `rgb(28, 27, 22)` (about 1.10:1) with a 1.5px stroke at opacity 0.26 peaking at `rgb(83, 71, 34)` (2.06:1).

The headline and the sub-line stay at WCAG AA against that yellow. Large bold headline text needs 3:1. The 18px sub-line needs 4.5:1. The fainter shape leaves more contrast than the previous outline.

The path is Natural Earth 1:10m cultural admin-1 for Sarawak (`MY-13`), public domain. Projection stored in `data/sarawak-proj.json`: `x = (longitude − 109.528436) × 100`, `y = (4.962329 − latitude) × 100`, width 614.7, height 411.1. Terms: the Natural Earth dataset is public domain ([naturalearthdata.com](https://www.naturalearthdata.com/about/terms-of-use/)). No permission or attribution is required, so the footer does not print a map credit.

## Cards

Cards use the same `data/sites.json` list, in that order. Two columns with a 16px gap, one column below 560px. A third site wraps onto the next row. Each card has the Phosphor tile, the `tag` pill, the name, the `text`, and a Visit link to `url`. The name sits under the icon row, the description follows, and Visit sits on the right of a top border. The description grows to fill the card, so the two Visit rows line up when the paragraphs differ in length.

## Adding a site

Add one object to the `sites` array. Do not edit the template. The next build draws a card for it. The map outline does not change.

| Field | Role |
| --- | --- |
| `id` | Lowercase slug. Used on the card and as the About heading id. |
| `name` | Card heading. |
| `url` | Visit link on the card, and the hostname link on About. There is no separate domain field. |
| `tag` | Pill, such as News or Directory. |
| `icon` | File name in `site/icons/` without `.svg`. Phosphor duotone, used on the card only. |
| `text` | Card description. |

Those six fields are the whole entry. There is no `map` field and no `counts` field. The build does not fetch story or scheme totals.

## Footer

A rounded credit box with one centred line: “Built by hafiy.my, an independent publication. Not affiliated with the Sarawak Government.”

## Motion

The brief uses bantuan’s `hero-reveal`: a rise of 18px over 0.85s, easing `cubic-bezier(.22, 1, .36, 1)`. The headline and sub-line use `hero-content-reveal` (10px, 0.7s). The map does not animate on its own. `prefers-reduced-motion: reduce` removes the transform motion.

## Deploy

`scripts/build.py` writes `dist/` only. It does not fetch live pages. `design-handoff/` stays in the repo and is not copied. The build copies the repo `CNAME` (`sarawak.news`) into `dist/CNAME`. Canonical and `og:url` on the home page are `https://sarawak.news/`. About uses `https://sarawak.news/about.html`. `robots.txt` and `sitemap.xml` use the same origin. Internal links (`index.html`, `about.html`, `style.css`, `app.js`, `fonts/Geist-Variable.woff2`) are relative, so the site works at the domain root.

`.github/workflows/build.yml` tests and builds on every pull request. A push to `main` deploys that build with GitHub Pages. `workflow_dispatch` can rebuild `main` by hand. The daily schedule is gone. It only existed to refresh counts, and the cards no longer show counts.

## Docs check

`.github/workflows/docs-check.yml` runs job `docs-check` on pull requests (`opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`). It diffs the PR with three dots (`base...head`). Watched paths are `site/*`, `scripts/build.py`, `scripts/docs_check_pr.py`, `.github/workflows/*`, `data/sarawak-path.txt`, `data/sarawak-proj.json`, and `data/sites.json`. A change there fails unless `docs/` also changes, or the PR has the `no-docs-needed` label.
