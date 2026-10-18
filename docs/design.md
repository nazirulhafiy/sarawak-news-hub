# Design

The live site is [https://sarawak.news/](https://sarawak.news/). Pages are the static output of `scripts/build.py`, styled by `site/style.css`. This note describes that system.

Every published site is one object in `data/sites.json`. That list drives the cards. The current entries are [AI.Sarawak.News](https://ai.sarawak.news/), [Bantuan.Sarawak.News](https://bantuan.sarawak.news/), and [Events.Sarawak.News](https://events.sarawak.news). Events uses the Phosphor calendar tile (`site/icons/calendar.svg`). There is no PCDS card. The hero is a line drawing of the Sarawak State Legislative Assembly riverfront, with Wisma Sanyan, Menara Kidurong and the Grand Old Lady derrick added. It does not mark sites.

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

The head links the SVG icon, the `.ico` with `sizes="any"`, the Apple touch icon, and the 512 PNG. `theme-color` is `#ffffff` for `prefers-color-scheme: light` and `#0f1115` for dark. The 16 and 32 pixel extras stay in the handoff folder. `favicon.ico` already carries the small sizes. The favicon and the app icon stay this rounded F1 tile. They are not the share image.

## Social image

`site/og.png` is a 1200×630 PNG. The build copies it to `dist/og.png`. The background is the dark canvas `#0f1115` and runs to every edge. The file is RGB, with no alpha and no rounded corners. Centred in the frame are the yellow Sarawak map from the F1 mark (`#f7c948`) and, beside it, the name Sarawak.News in Geist (`#f3f5f7`). There is no tagline on the card.

Home and About point `og:image` and `twitter:image` at `https://sarawak.news/og.png`. `og:image:width` is 1200 and `og:image:height` is 630. `twitter:card` is `summary_large_image`.

## Theme

`scripts/build.py` inlines the same boot script as bantuan. Before paint it reads `localStorage` key `sarawak-theme`. `dark` forces dark. `light` forces light. With no stored choice, `prefers-color-scheme: dark` selects dark. `site/app.js` updates the toggle label, persists a click, and follows later system changes only when nothing is stored.

The header is bantuan’s bar: wordmark, red / yellow / black rule, Sites and About, sun-and-moon toggle. Below 560px the links collapse into a menu button. The theme control stays visible.

The bar is sticky. `.bar` is a full-viewport shell (`position: sticky; top: 0`) with a solid page-colour background in light and dark mode, so the page scrolls underneath it. The wordmark, Sites, About, the theme toggle, and the menu stay on the 760px rail inside `.bar-inner`. On viewports wider than 560px the tri-colour rule stays on that rail: red under the wordmark, yellow and black splitting the rest, including under the theme control. From 560px down the rule runs edge to edge, from the left of the viewport to the right (`0` to `100vw`), including behind the theme and menu icons. `site/app.js` adds `.is-scrolled` after any scroll. That class paints a thin bottom edge and a soft shadow. At the top of the page there is no shadow. Light mode uses `0 6px 16px rgb(17 24 39 / 8%)`. Dark mode uses `0 6px 16px rgb(0 0 0 / 35%)`. `html` uses `overflow-x: clip`, and from 560px down the body does too, so the full-bleed bar and the mobile drawing do not widen the page (`scrollWidth` stays the viewport width). `scroll-padding-top` is 72px, and 76px from 560px down, so a jump to `#content` clears the bar. The skip link stacks above the bar.

## Hero

The home hero is a centred brief. The words are fixed (constants `HEADLINE` and `SUBTITLE` in `scripts/build.py`; `DECK` matches `SUBTITLE` for meta tags):

- Sarawak, made easy.
- Aggregating key information, all in one place.

The headline keeps the comma after Sarawak and the full stop. `.brief` is 760px at most, centred, `text-align: center`, with `padding: 44px 8px 0` and `margin: 32px auto 8px`. The headline is `clamp(36px, 6vw, 48px)`, weight 700, letter-spacing `-1.2px`, line-height `1.02`, `max-width: 680px`, and `margin: 0 auto 12px`. The visible sub-line, `p.brief-deck`, is 18px, line-height `1.62`, `max-width: 620px`, centred, in the copy colour (`#374151` light, `#d2d8df` dark). It uses `text-wrap: balance`, with `text-wrap: pretty` declared first so a browser that does not understand `balance` still avoids a short last line. Below 560px the headline is `clamp(2.15rem, 11vw, 3rem)`, the sub-line is 17px, and the brief padding is `30px 0 0`. The headline wraps on its own. On a 390px screen it breaks after the comma, so the second line is “made easy.” The sub-line stays on one line. The document `<title>`, `og:title`, and `twitter:title` on the home page are `Sarawak.News`. About keeps `<title>About Sarawak.News</title>`.

`description`, `og:description`, and `twitter:description` on Home and About use the same sentence as `p.brief-deck`: “Aggregating key information, all in one place.” The About lede repeats it after “Sarawak, made easy.”

Under the words is one inline SVG (`svg.hero-art`, viewBox `0 0 760 240`) from `site/hero-art.svg`. It is a line drawing of the Kuching riverfront. The Darul Hana bridge is on the left, the Dewan Undangan Negeri stays in the centre, and Gunung Santubong is on the right. Trees sit on the bank. The kampung houses are gone. Wisma Sanyan, the Sibu tower, stands on the left of the assembly, clear of the trees. Menara Kidurong, the Bintulu tower, is also drawn in. The Grand Old Lady derrick, from Miri, stands on the right. Filled shapes (`.occl`) cover the bank line behind the added buildings. In light mode the fill is `#fff`, the same as the page (`#ffffff`). In dark mode it is `#0f1115`. The river is a few short wave strokes. There is no boat. `aria-hidden="true"` and `focusable="false"` mark it decorative. `pointer-events: none` keeps it off clicks. The drawing sits in the flow, full width of the 760px rail, with `margin-top: 22px`. A horizontal mask fades the outer 10% on each side. Below 560px the drawing is 115% of the column and shifted with `margin: 16px -7.5% 0`, so it bleeds off the screen edges. `html` and `body` use `overflow-x: clip` at that width so the bleed does not scroll. The clip edge is the screen edge, so the drawing still runs off both sides of the column.

Light lines use `color: #8b93a1` at opacity 0.6. The building (`.dun`) is `#6b7584`. Hills, bridge, cables, river, promenade, and minor marks each have their own opacity (0.6, 0.75, 0.7, 0.75, 0.55, 0.85). Santubong (`.art-peak`) is inside the hills group, at opacity 0.9, so it reads a little stronger than the low hills. The bridge pylons (`.art-mast`) use a 1.9px stroke, heavier than the cables. The sun is Sarawak yellow: stroke `#f7c948` at 2px, fill `rgba(247, 201, 72, 0.18)`. Light mode keeps that circle. Dark mode replaces it with a moon in the same place and at the same size: a crescent whose outer limb is the sun’s circle (`cx` 652, `cy` 44, `r` 13). The moon uses the same 2px stroke and the same Sarawak yellow. Its fill is `rgba(247, 201, 72, 0.1)` and its stroke opacity is 0.6.

Dark mode also changes the line inks. The drawing is `#5f6977` at opacity 0.6 and the building is `#8a94a3`. Page, card, and type colours stay on the theme tokens.

Three shapes were traced from Wikimedia photos. About gives each one line, with the author, the licence, and links to the file and the licence page. The photos are not published.

- The DUN, from [Kuching Sarawak Dewan-Undangan-Negeri-Sarawak-01.jpg](https://commons.wikimedia.org/wiki/File:Kuching_Sarawak_Dewan-Undangan-Negeri-Sarawak-01.jpg) by CEphoto (Uwe Aranas), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- The Darul Hana pylons, from [Jambatan Darul Hana, di Bandaraya Kuching.jpg](https://commons.wikimedia.org/wiki/File:Jambatan_Darul_Hana,_di_Bandaraya_Kuching.jpg) by Meandkancil2020, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Gunung Santubong, from [Mount Santubong from Santubong Bridge.jpg](https://commons.wikimedia.org/wiki/File:Mount_Santubong_from_Santubong_Bridge.jpg) by Matthew Anderson Lockhart, [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/).

Other photos were used only to check general proportions: the rest of the assembly views, the Darul Hana promenade view, the Santubong profiles, and the Kuching river scene. The full list, without the tambang photos, is in [docs/SOURCES.md](SOURCES.md). The tambang references are omitted because the boat is not in the drawing. The footer does not carry these credits. The favicon stays the F1 Sarawak tile.

## Cards

Cards use the same `data/sites.json` list, in that order. Two columns with a 16px gap, one column below 560px. A third site wraps onto the next row. Each card has the Phosphor tile, the `tag` pill, the name, the `text`, and a Visit link to `url`. The name sits under the icon row, the description follows, and Visit sits on the right of a top border. The description grows to fill the card, so the two Visit rows line up when the paragraphs differ in length. Pointer hover uses the shared ai-style motion documented under “Card hover” (not a flat static card).

## Card hover

The hover matches ai.sarawak.news story cards. On devices with hover (`@media (hover: hover)`), a card lifts 3px and tilts a quarter degree: odd cards (`-.25deg`), even cards (`:nth-child(even)`, `.25deg`), so neighbours lean apart. The border goes to `#cbd1da` (dark `#4b5663`) and the shadow to `0 8px 20px rgb(17 24 39 / 8%)` (dark `rgb(0 0 0 / 28%)`). Transform eases over 0.18s, and shadow, border and background over 0.22s. There is no top bar, no yellow border, no scaling and no text colour change. The card is not a link, so keyboard focus uses `.hub-card:has(.hub-visit:focus-visible)`: a 3px `#f7c948` outline at 3px offset in both modes, with no lift or shadow. That outline replaces the link's own ring. `prefers-reduced-motion: reduce` removes transitions and the lift and tilt. The border and shadow still change.

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

## Back to top

The control uses the same markup as ai.sarawak.news: a `button.back-to-top` with `type="button"`, `aria-label="Back to top"`, a “Back to top” label, and an `↑` arrow. It starts `hidden`, so it is not focusable. `site/app.js` shows it only when `scrollY` is at least 600, and hides it again below that. The home page cannot scroll that far, so the control stays absent there. Wider than 560px it is the ai.sarawak.news pill: “Back to top ↑” in Geist at 11px, weight 850, line-height 1.3, padding `8px 12px`, a 3.08px gap, and a 999px radius. It is fixed 24px from the viewport’s right and bottom edges, with a `0 4px 14px rgb(17 24 39 / 10%)` shadow, and it rises 6px as it fades. From 560px down it is a 44px circle (`border-radius: 50%`), arrow only, at 18px, inset with `max(14px, env(safe-area-inset-*) + 14px)`. The chip is `#111` and the label and arrow are `#f7c948` in both themes. Those colours are written on the control, not taken from the page tokens. Light mode’s border is 1px `#111`. Dark mode’s border is 1px `#f7c948`. The same Geist variable face already on the page supplies weight 850. It fades over 180ms. `prefers-reduced-motion: reduce` drops the fade and scrolls to the top instantly; otherwise the click scrolls smoothly. The focus ring is 3px `#f7c948` with a 2px offset. The control sits in the screen corner, under the sticky bar (`z-index` 5, bar 40), and does not cover the header.

## Motion

The brief uses bantuan’s `hero-reveal`: a rise of 18px over 0.85s, easing `cubic-bezier(.22, 1, .36, 1)`. The headline and sub-line use `hero-content-reveal` (10px, 0.7s), delayed 0.12s and 0.22s. The drawing uses `hero-art-reveal` (10px, 0.7s, delay 0.4s) and ends at opacity 0.6, so it appears last. `prefers-reduced-motion: reduce` removes the motion.

## Build pipeline

`scripts/build.py` is the hub’s static site generator: it validates `data/sites.json`, renders `dist/index.html` and `dist/about.html`, and copies CSS, JS, fonts, favicons, `og.png`, and `CNAME`. There is no discovery, review queue, or scheduled ingestion workflow—only this build step and GitHub Actions on push. Sister-site totals are not fetched at build time.

## Deploy

`scripts/build.py` writes `dist/` only. It does not fetch live pages. `design-handoff/` stays in the repo and is not copied. The build copies the repo `CNAME` (`sarawak.news`) into `dist/CNAME`. Canonical and `og:url` on the home page are `https://sarawak.news/`. About uses `https://sarawak.news/about.html`. `robots.txt` and `sitemap.xml` use the same origin. Internal links (`index.html`, `about.html`, `style.css`, `app.js`, `fonts/Geist-Variable.woff2`) are relative, so the site works at the domain root.

`.github/workflows/build.yml` tests and builds on every pull request. A push to `main` deploys that build with GitHub Pages. `workflow_dispatch` can rebuild `main` by hand. The daily schedule is gone. It only existed to refresh counts, and the cards no longer show counts.

## Docs check

`.github/workflows/docs-check.yml` runs job `docs-check` on pull requests (`opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`). It diffs the PR with three dots (`base...head`). Watched paths are `site/*`, `scripts/build.py`, `scripts/docs_check_pr.py`, `.github/workflows/*`, and `data/sites.json`. A change there fails unless `docs/` also changes, or the PR has the `no-docs-needed` label.

## Analytics

Every page `<head>` includes both trackers from `scripts/build.py` (edit the build, not `dist/`).

- Google Analytics 4: measurement ID `G-SJMJ0R0GJS`. `render_ga_script()` emits one inline script that:

  1. **Production host gate** — loads gtag only when `location.hostname` is `sarawak.news` or `www.sarawak.news`. It does not load on localhost, `*.pages.dev`, `*.github.io`, `*.vercel.app`, or any other host.
  2. **Internal traffic cookie** — `?internal=1` sets a first-party `sn_internal=1` cookie (`path=/`, `max-age=31536000` ≈ 1 year, `SameSite=Lax`, plus `Secure` on HTTPS). `?internal=0` clears it. While the cookie is set, `gtag('config', 'G-SJMJ0R0GJS', { traffic_type: 'internal' })` so GA4 can filter agent/QA hits. Agents and automated checks that open the live site must use `?internal=1` (see `AGENTS.md`).

- Cloudflare Web Analytics: the hub is served by GitHub Pages (not proxied through Cloudflare), so `render_cf_beacon()` embeds the zone site token manually:

  `<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token":"092a061973fc4d899cd2e4b52952af89"}'></script>`

  Token `092a061973fc4d899cd2e4b52952af89` is the sarawak.news zone Web Analytics site (shared with ai.sarawak.news; filter by hostname in the dashboard). Cloudflare is not gated by hostname the same way as GA4.

- No Content-Security-Policy is set; if one is added, allow `www.googletagmanager.com`, `*.google-analytics.com` and `static.cloudflareinsights.com`.
