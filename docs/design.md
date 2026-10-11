# Design

The live site is [https://sarawak.news/](https://sarawak.news/). Pages are the static output of `scripts/build.py`, styled by `site/style.css`. This note describes that system.

Every published site is one object in `data/sites.json`. That list drives the cards. The current entries are [AI.Sarawak.News](https://ai.sarawak.news/) and [Bantuan.Sarawak.News](https://bantuan.sarawak.news/). There is no PCDS card. The hero is a line drawing of the Sarawak State Legislative Assembly riverfront. It does not mark sites.

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

The home hero is a centred brief. The words are fixed:

- Sarawak, made easy.
- Explore Sarawak-focused sites, all in one place.

The headline keeps the comma after Sarawak and the full stop. `.brief` is 760px at most, centred, `text-align: center`, with `padding: 44px 8px 0` and `margin: 32px auto 8px`. The headline is `clamp(36px, 6vw, 48px)`, weight 700, letter-spacing `-1.2px`, line-height `1.02`, `max-width: 680px`, and `margin: 0 auto 12px`. The sub-line is 18px, line-height `1.62`, `max-width: 620px`, centred, in the copy colour (`#374151` light, `#d2d8df` dark). Below 560px the headline is `clamp(2.15rem, 11vw, 3rem)`, the sub-line is 17px, and the brief padding is `30px 0 0`. The headline wraps on its own. On a 390px screen it breaks after the comma, so the second line is “made easy.” The document `<title>`, `og:title`, and `twitter:title` on the home page are `Sarawak.News`. About keeps `<title>About Sarawak.News</title>`.

Under the words is one inline SVG (`svg.hero-art`, viewBox `0 0 760 240`) from `site/hero-art.svg`. It is a line drawing of the Kuching riverfront. The Darul Hana bridge is on the left, the Dewan Undangan Negeri is in the middle, and Gunung Santubong is on the right. Trees and shophouses sit on the bank. The river is a few short wave strokes. There is no boat. `aria-hidden="true"` and `focusable="false"` mark it decorative. `pointer-events: none` keeps it off clicks. The drawing sits in the flow, full width of the 760px rail, with `margin-top: 22px`. A horizontal mask fades the outer 10% on each side. Below 560px the drawing is 132% of the column and shifted with `margin: 16px -16% 0`, so it bleeds off the screen edges. `html` uses `overflow-x: hidden` so that bleed does not scroll.

Light lines use `color: #8b93a1` at opacity 0.6. The building (`.dun`) is `#6b7584`. Hills, bridge, cables, river, promenade, and minor marks each have their own opacity (0.6, 0.75, 0.7, 0.75, 0.55, 0.85). Santubong (`.art-peak`) is inside the hills group, at opacity 0.9, so it reads a little stronger than the low hills. The bridge pylons (`.art-mast`) use a 1.9px stroke, heavier than the cables. The sun is Sarawak yellow: stroke `#f7c948` at 2px, fill `rgba(247, 201, 72, 0.18)`.

Dark mode changes only those inks. The drawing is `#5f6977` at opacity 0.6, the building is `#8a94a3`, and the sun fill is `rgba(247, 201, 72, 0.1)` with stroke opacity 0.6. Page, card, and type colours stay on the theme tokens.

Three shapes were traced from Wikimedia photos. About gives each one line, with the author, the licence, and links to the file and the licence page. The photos are not published.

- The DUN, from [Kuching Sarawak Dewan-Undangan-Negeri-Sarawak-01.jpg](https://commons.wikimedia.org/wiki/File:Kuching_Sarawak_Dewan-Undangan-Negeri-Sarawak-01.jpg) by CEphoto (Uwe Aranas), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- The Darul Hana pylons, from [Jambatan Darul Hana, di Bandaraya Kuching.jpg](https://commons.wikimedia.org/wiki/File:Jambatan_Darul_Hana,_di_Bandaraya_Kuching.jpg) by Meandkancil2020, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Gunung Santubong, from [Mount Santubong from Santubong Bridge.jpg](https://commons.wikimedia.org/wiki/File:Mount_Santubong_from_Santubong_Bridge.jpg) by Matthew Anderson Lockhart, [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/).

Other photos were used only to check general proportions: the rest of the assembly views, the Darul Hana promenade view, the Santubong profiles, and the Kuching river scene. The full list, without the tambang photos, is in [docs/SOURCES.md](SOURCES.md). The tambang references are omitted because the boat is not in the drawing. The footer does not carry these credits. The favicon stays the F1 Sarawak tile.

## Cards

Cards use the same `data/sites.json` list, in that order. Two columns with a 16px gap, one column below 560px. A third site wraps onto the next row. Each card has the Phosphor tile, the `tag` pill, the name, the `text`, and a Visit link to `url`. The name sits under the icon row, the description follows, and Visit sits on the right of a top border. The description grows to fill the card, so the two Visit rows line up when the paragraphs differ in length.

## Adding a site

Add one object to the `sites` array. Do not edit the template. The next build draws a card for it. The riverfront drawing does not change.

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

The brief uses bantuan’s `hero-reveal`: a rise of 18px over 0.85s, easing `cubic-bezier(.22, 1, .36, 1)`. The headline and sub-line use `hero-content-reveal` (10px, 0.7s), delayed 0.12s and 0.22s. The drawing uses `hero-art-reveal` (10px, 0.7s, delay 0.4s) and ends at opacity 0.6, so it appears last. `prefers-reduced-motion: reduce` removes the motion.

## Deploy

`scripts/build.py` writes `dist/` only. It does not fetch live pages. `design-handoff/` stays in the repo and is not copied. The build copies the repo `CNAME` (`sarawak.news`) into `dist/CNAME`. Canonical and `og:url` on the home page are `https://sarawak.news/`. About uses `https://sarawak.news/about.html`. `robots.txt` and `sitemap.xml` use the same origin. Internal links (`index.html`, `about.html`, `style.css`, `app.js`, `fonts/Geist-Variable.woff2`) are relative, so the site works at the domain root.

`.github/workflows/build.yml` tests and builds on every pull request. A push to `main` deploys that build with GitHub Pages. `workflow_dispatch` can rebuild `main` by hand. The daily schedule is gone. It only existed to refresh counts, and the cards no longer show counts.

## Docs check

`.github/workflows/docs-check.yml` runs job `docs-check` on pull requests (`opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`). It diffs the PR with three dots (`base...head`). Watched paths are `site/*`, `scripts/build.py`, `scripts/docs_check_pr.py`, `.github/workflows/*`, and `data/sites.json`. A change there fails unless `docs/` also changes, or the PR has the `no-docs-needed` label.
