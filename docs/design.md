# Design

The live site is [https://sarawak.news/](https://sarawak.news/). Pages are the static output of `scripts/build.py`, styled by `site/style.css`. This note describes that system.

Every published site is one object in `data/sites.json`. That list drives the cards. The current entries are [AI.Sarawak.News](https://ai.sarawak.news/), [Bantuan.Sarawak.News](https://bantuan.sarawak.news/), and [Events.Sarawak.News](https://events.sarawak.news). Events uses the Phosphor calendar tile (`site/icons/calendar.svg`). There is no PCDS card. The hero is a line drawing of the Sarawak State Legislative Assembly riverfront, with Wisma Sanyan, Menara Kidurong and the Grand Old Lady derrick added. It does not mark sites.

## Type and colour

Type is Geist, then ui-sans-serif, system-ui, and the system sans-serif stack. Geist is the official variable font (weights 100–900), self-hosted under the SIL Open Font License from the vercel/geist-font v1.7.2 release. `site/fonts/OFL.txt` is the licence. The face uses `font-display: swap`. The head preloads `fonts/Geist-Variable.woff2` with `crossorigin`.

Colours are the same tokens as [bantuan.sarawak.news](https://bantuan.sarawak.news/): page white, ink near-black `#111827`, Sarawak red `#d22630`, red ink `#9f1d26`, yellow `#f7c948`, black `#111111`. The body is at most 840px wide. The brief, cards, and footer sit on a 760px rail.

Dark mode sets `html[data-theme="dark"]` and swaps the same tokens: canvas `#0f1115`, card `#171b22`, ink `#f3f5f7`, muted `#aeb6c2`, line `#2c333d`, red `#f15b61`, red ink `#ff8d92`. Icon tiles use a translucent yellow fill and a yellow border. Card description copy is `#374151` in light mode and `#d2d8df` in dark mode.

The table is generated from `:root` and `html[data-theme="dark"]` in `site/style.css`.

<!-- BEGIN GENERATED: design-tokens -->
| Token | `:root` | `html[data-theme="dark"]` |
| --- | --- | --- |
| `--canvas` | #ffffff | #0f1115 |
| `--page` | #ffffff | #0f1115 |
| `--card` | #ffffff | #171b22 |
| `--ink` | #111827 | #f3f5f7 |
| `--muted` | #6b7280 | #aeb6c2 |
| `--line` | #e2e4e9 | #2c333d |
| `--sarawak-red` | #d22630 | #f15b61 |
| `--sarawak-red-ink` | #9f1d26 | #ff8d92 |
| `--sarawak-yellow` | #f7c948 | #f7c948 |
| `--sarawak-yellow-soft` | #fffbea | #3a3110 |
| `--sarawak-black` | #111111 | #111111 |
| `--group-icon-tile` | #fff6d2 | rgba(247, 201, 72, 0.16) |
| `--group-icon-border` | #f7c948 | rgba(247, 201, 72, 0.7) |
| `--copy` | #374151 | #d2d8df |
| `--page-gutter` | 20px |  |
<!-- END GENERATED: design-tokens -->

## Favicon

Nazirul approved the Design Bot solid3 hub favicon (Chief `#fav-s3live`, approved 19 Oct 2026): the yellow (`#f7c948`) origami hornbill on a near-black (`#111111`) rounded tile. The source files live in `design-handoff/favicon-F1/`. The build copies them to the root of `dist/` and does not publish the rest of `design-handoff/`:

| Published URL | Source |
| --- | --- |
| `favicon.ico` | `favicon.ico` |
| `favicon.svg` | `favicon.svg` |
| `apple-touch-icon.png` | `apple-touch-icon.png` |
| `icon-192.png` | `icon-192.png` |
| `icon-512.png` | `icon-512.png` |

The head links the SVG icon, the `.ico` with `sizes="any"`, the Apple touch icon, and the 192 and 512 PNGs. There is no web app manifest. Each icon `href` gets a content hash query string from `versioned_href` in `kit/python/asset_urls.py`. The value is the first 12 hex characters of the SHA-256 of that file. `og:image` and `twitter:image` use the same function on `site/og.png`. Replacing a file changes its query string, so browsers fetch the new bytes after publish. `tests/test_asset_urls.py` fails if `scripts/`, `kit/`, `docs/`, `README.md`, `AGENTS.md`, or site HTML, JS, CSS, or SVG contain a hand-typed asset query stamp outside a generated block. `theme-color` is `#ffffff` for `prefers-color-scheme: light` and `#0f1115` for dark. `favicon.ico` already carries the 16 and 32 pixel sizes. The favicon and the app icons stay this rounded tile. They are not the share image.

## Social image

`site/og.png` is a 1200×630 PNG. The build copies it to `dist/og.png`. The background is the dark canvas `#0f1115` and runs to every edge. The file is RGB, with no alpha and no rounded corners. Centred in the frame are the yellow Sarawak map from the F1 mark (`#f7c948`) and, beside it, the hub title from `data/site.json` in Geist (`#f3f5f7`). There is no tagline on the card.

Home and About point `og:image` and `twitter:image` at `https://sarawak.news/og.png` plus the content hash query string of `site/og.png`. `og:image:width` is 1200 and `og:image:height` is 630. `twitter:card` is `summary_large_image`.

## Theme

`scripts/build.py` inlines the same boot script as bantuan. Before paint it reads `localStorage` key `sarawak-theme`. `dark` forces dark. `light` forces light. With no stored choice, `prefers-color-scheme: dark` selects dark. `site/app.js` updates the toggle label, persists a click, and follows later system changes only when nothing is stored.

The header is bantuan’s bar: wordmark, red / yellow / black rule, Sites and About, sun-and-moon toggle. Below 560px the links collapse into a menu button. The theme control stays visible.

The home link (`.brand`) starts with Design Bot’s origami line hornbill (`#snnav`), then the hub `title` from `data/site.json`, with a small gap. Canonical mark files live in `kit/assets/icons/` (`nav-mark-transparent.svg` light, `nav-mark-transparent-dark.svg` dark; transparent, no `#111` square). Matching copies under `site/icons/` are kept in sync by `python3 kit/sync.py`. The build copies the kit marks to `dist/icons/`. Images use `alt=""`; the text labels the link. Mark height matches the wordmark line (`1.15em`). The brand stays on one line (`white-space: nowrap`) down to 375px. SVGs are used as supplied — no recolouring.

The masthead bar scrolls with the page. `.bar` is a full-viewport shell (`position: relative`) with a solid page-colour background in light and dark mode. At rest there is no full-bleed gray hairline under the bar; only the Sarawak tri-colour segments mark the bottom edge. The wordmark, Sites, About, the theme toggle, and the menu stay on the 760px rail inside `.bar-inner`. On viewports wider than 560px the tri-colour rule stays on that rail: red under the wordmark, yellow and black splitting the rest, including under the theme control. From 560px down the rule runs edge to edge, from the left of the viewport to the right (`0` to `100vw`), including behind the theme and menu icons. `html` uses `overflow-x: clip`, and from 560px down the body does too, so the full-bleed bar and the mobile drawing do not widen the page (`scrollWidth` stays the viewport width). The skip link stacks above the bar.

## Hero

The home hero is a centred brief. Hub wording is owned by `data/site.json` (`title`, `tagline`, `description`, `about_lead`). The build fills every surface from that file. Do not hand-type those strings outside `data/site.json`, except inside a generated block. `tests/test_site_copy.py` fails if they appear elsewhere. `python3 kit/generate_docs.py` writes the table from `data/site.json`.

<!-- BEGIN GENERATED: site-copy -->
| Field | Value |
| --- | --- |
| `title` | Sarawak.News |
| `tagline` | Sarawak, made easy. |
| `description` | Aggregating key information, all in one place. |
<!-- END GENERATED: site-copy -->

- `tagline` → home `<h1>`
- `description` → `p.brief-deck`, meta / og / twitter descriptions on Home and About, and the footer note
- `title` → home `<title>` / `og:title` / `twitter:title`, header and footer brand, `og:site_name`
- About page title is `About` plus `title`; the lede is `about_lead` (must equal `tagline` + space + `description`)

The headline keeps the comma after Sarawak and the full stop when the tagline uses that form. `.brief` is 760px at most, centred, `text-align: center`, with `padding: 44px 8px 0` and `margin: 32px auto 8px`. The headline is `clamp(36px, 6vw, 48px)`, weight 700, letter-spacing `-1.2px`, line-height `1.02`, `max-width: 680px`, and `margin: 0 auto 12px`. The visible sub-line, `p.brief-deck`, is 18px, line-height `1.62`, `max-width: 620px`, centred, in the copy colour (`#374151` light, `#d2d8df` dark). It uses `text-wrap: balance`, with `text-wrap: pretty` declared first so a browser that does not understand `balance` still avoids a short last line. Below 560px the headline is `clamp(2.15rem, 11vw, 3rem)`, the sub-line is 17px, and the brief padding is `30px 0 0`. The headline wraps on its own. On a 390px screen the current tagline breaks after the comma, so the second line is “made easy.” The sub-line stays on one line.

Under the words is one inline SVG (`svg.hero-art`, viewBox `0 0 760 240`) from `site/hero-art.svg`. It is a line drawing of the Kuching riverfront. The Darul Hana bridge is on the left, the Dewan Undangan Negeri stays in the centre, and Gunung Santubong is on the right. Trees sit on the bank. The kampung houses are gone. Wisma Sanyan, the Sibu tower, stands on the left of the assembly, clear of the trees. Menara Kidurong, the Bintulu tower, is also drawn in. The Grand Old Lady derrick, from Miri, stands on the right. Filled shapes (`.occl`) cover the bank line behind the added buildings. In light mode the fill is `#fff`, the same as the page (`#ffffff`). In dark mode it is `#0f1115`. The river is a few short wave strokes. There is no boat. `aria-hidden="true"` and `focusable="false"` mark it decorative. `pointer-events: none` keeps it off clicks. The drawing sits in the flow, full width of the 760px rail, with `margin-top: 22px`. A horizontal mask fades the outer 10% on each side. Below 560px the drawing is 115% of the column and shifted with `margin: 16px -7.5% 0`, so it bleeds off the screen edges. `html` and `body` use `overflow-x: clip` at that width so the bleed does not scroll. The clip edge is the screen edge, so the drawing still runs off both sides of the column.

Light lines use `color: #8b93a1` at opacity 0.6. The building (`.dun`) is `#6b7584`. Hills, bridge, cables, river, promenade, and minor marks each have their own opacity (0.6, 0.75, 0.7, 0.75, 0.55, 0.85). Santubong (`.art-peak`) is inside the hills group, at opacity 0.9, so it reads a little stronger than the low hills. The bridge pylons (`.art-mast`) use a 1.9px stroke, heavier than the cables. The sun is Sarawak yellow: stroke `#f7c948` at 2px, fill `rgba(247, 201, 72, 0.18)`. Light mode keeps that circle. Dark mode replaces it with a moon in the same place and at the same size: a crescent whose outer limb is the sun’s circle (`cx` 652, `cy` 44, `r` 13). The moon uses the same 2px stroke and the same Sarawak yellow. Its fill is `rgba(247, 201, 72, 0.1)` and its stroke opacity is 0.6.

Dark mode also changes the line inks. The drawing is `#5f6977` at opacity 0.6 and the building is `#8a94a3`. Page, card, and type colours stay on the theme tokens.

Shapes were traced from Wikimedia photos. About does not list those photo credits on the page. The photos are not published.

Other photos were used only to check general proportions: the rest of the assembly views, the Darul Hana promenade view, the Santubong profiles, and the Kuching river scene. The full list, without the tambang photos, is in [docs/SOURCES.md](SOURCES.md). The tambang references are omitted because the boat is not in the drawing. The footer does not carry these credits. The favicon stays the Design Bot solid3 hub favicon (Chief `#fav-s3live`): the yellow (`#f7c948`) origami hornbill on a near-black (`#111111`) rounded tile in `design-handoff/favicon-F1/`. Icon links use a content hash query string.

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

## Shared kit

Fleet chrome that every sarawak.news site should share lives in `kit/` in this hub repo (source of truth). Sisters vendor that tree at a pinned hub commit; see `kit/README.md`. Delivery is a **vendored copy + `kit/PIN` + `python3 kit/sync.py --check`**, not a git submodule and not a separate kit repository.

| Kit path | Provides |
| --- | --- |
| `kit/python/shell.py` | Header, footer (always includes Contact `mailto:contact@sarawak.news`), back-to-top markup |
| `kit/python/analytics_loader.py` | Registry-driven production loader (`data-sn-analytics-loader`) |
| `kit/python/analytics_registry.py` | `data/analytics.json` validation (each site keeps its own registry file) |
| `kit/python/asset_urls.py` | Content-hash query strings for icon and share-image URLs |
| `kit/python/docs_facts.py` | Fact blocks for site copy, analytics, hosting, and colour tokens |
| `kit/generate_docs.py` | Writes those blocks, or checks them with `--check` |
| `kit/favicon_sheet.py` | Proof contact sheet of the favicon at 16, 32, and 48 pixels. Not published. |
| `kit/assets/icons/` | Origami hornbill nav marks |
| `kit/css/back-to-top.css` / `kit/js/back-to-top.js` | Back-to-top rules and behaviour (mirrored into `site/style.css` / `site/app.js` inside `sn-kit:back-to-top` markers) |
| `kit/css/footer-column-stacks.css` | Column-stack footer layout (mirrored into `site/style.css` inside `sn-kit:footer-column-stacks` markers; hub production uses `layout="column_stacks"`) |

Hub CI runs `python3 kit/sync.py --check` before tests. That check fails on invariant breaks (for example removing Contact or hand-editing back-to-top) and on consumer drift.

## Footer

Structured, contained footer on the 760px rail, rendered by `kit.python.shell.render_footer` with `layout="column_stacks"`: independent left stack (brand from `data/site.json` `title` and the deck line from `description`, then fleet sister-site links) and right stack (**Explore** with vertical Home / About / Contact links; Contact uses `mailto:contact@sarawak.news`, same `site-footer-link` styling as the other Explore links). Fleet cross-links from `kit/fleet-cross-links.json` are plain `https://` anchors to sister sites; the hub entry is omitted. Visible fleet labels are short (**AI**, **Events**, **Bantuan**); hrefs stay `ai.sarawak.news` / `events.sarawak.news` / `bantuan.sarawak.news`. Site cards and brand titles keep the full `*.Sarawak.News` names from `data/sites.json`. The fleet block heading and `aria-label` are **Hub** (`fleet_section_label="Hub"` in `scripts/build.py`; JSON `section_label` stays **Sarawak News** for other consumers). No `rel="nofollow"`. Shared column-stack rules live in `kit/css/footer-column-stacks.css` (synced `sn-kit:footer-column-stacks` region in `site/style.css`). Desktop grid uses `align-items: stretch` so the right-stack vertical rule runs the full height of the main footer row (including when there is no Categories block); stack contents still top-align inside each flex column. The fleet divider is column-local on the left stack; Explore sits in the right stack. The column split is a dedicated 1px grid track on `.site-footer-main` (kit `::before`) so the vertical rule spans the full main row height and meets the credit `border-top` with no gap; the Hub fleet `border-top` meets that track on the left stack edge. Hub has no footer Categories block. On mobile (≤560px) order is brand, then **Hub**, then Explore. Full-width builder and independence attribution row (“Built by hafiy.my, an independent publication. Not affiliated with the Sarawak Government.”). Hub passes a single `brand_note` string (no mid-note break). Sites that need a forced line break in the footer note (AI.Sarawak.News) pass `brand_note_parts` so the kit inserts `<br class="site-footer-note-break" />` between escaped sentences; that markup lives only in `kit/python/shell.py` (`FOOTER_NOTE_BREAK`).

Sister sites with footer Categories (Events, Bantuan) use the same `layout="column_stacks"` API with `extra_nav_right` for a Categories block after Explore and a full-width `<hr class="site-footer-grid-explore-divider">`. Per-site track sizing uses CSS variables on `.site-footer-main--column-stacks` (`--sn-footer-col-left`, `--sn-footer-col-right`, `--sn-footer-stack-inset`, `--sn-footer-fleet-gap`, `--sn-footer-explore-link-pad-bottom`, `--sn-footer-mobile-gutter`).

## Back to top

Markup comes from `kit.python.shell.render_back_to_top`. CSS and JS are owned by `kit/css/back-to-top.css` and `kit/js/back-to-top.js`, mirrored into `site/style.css` / `site/app.js` between `/* sn-kit:back-to-top:begin|end */` markers. The shared `prefers-reduced-motion` rule in `site/style.css` still includes `.back-to-top` with the other motion resets. The control matches ai.sarawak.news: a `button.back-to-top` with `type="button"`, `aria-label="Back to top"`, a “Back to top” label, and an `↑` arrow. It starts `hidden`, so it is not focusable. The kit JS shows it only when `scrollY` is at least 600, and hides it again below that. The home page cannot scroll that far, so the control stays absent there. Wider than 560px it is the ai.sarawak.news pill: “Back to top ↑” in Geist at 11px, weight 850, line-height 1.3, padding `8px 12px`, a 3.08px gap, and a 999px radius. It is fixed 24px from the viewport’s right and bottom edges, with a `0 4px 14px rgb(17 24 39 / 10%)` shadow, and it rises 6px as it fades. From 560px down it is a 44px circle (`border-radius: 50%`), arrow only, at 18px, inset with `max(14px, env(safe-area-inset-*) + 14px)`. The chip is `#111` and the label and arrow are `#f7c948` in both themes. Those colours are written on the control, not taken from the page tokens. Light mode’s border is 1px `#111`. Dark mode’s border is 1px `#f7c948`. The same Geist variable face already on the page supplies weight 850. It fades over 180ms. `prefers-reduced-motion: reduce` drops the fade and scrolls to the top instantly; otherwise the click scrolls smoothly. The focus ring is 3px `#f7c948` with a 2px offset. The control sits in the screen corner (`z-index` 5) and does not cover the header when visible.

## Motion

The brief uses bantuan’s `hero-reveal`: a rise of 18px over 0.85s, easing `cubic-bezier(.22, 1, .36, 1)`. The headline and sub-line use `hero-content-reveal` (10px, 0.7s), delayed 0.12s and 0.22s. The drawing uses `hero-art-reveal` (10px, 0.7s, delay 0.4s) and ends at opacity 0.6, so it appears last. `prefers-reduced-motion: reduce` removes the motion.

## Build pipeline

`scripts/build.py` is the hub’s static site generator: it validates `data/sites.json`, renders `dist/index.html` and `dist/about.html` from `kit/python`, and copies CSS, JS, fonts, favicons, `og.png`, and `CNAME`. Nav marks are copied from `kit/assets/icons/`. `python3 kit/sync.py --check` runs in CI before the tests. `python3 kit/generate_docs.py --check` runs after that. It fails when a generated block in `docs/design.md` or `README.md` does not match `data/site.json`, the analytics registry, `CNAME` or `data/hosting.json`, or the custom properties in `site/style.css`. There is no discovery, review queue, or scheduled ingestion workflow. The only publish path is this build step and GitHub Actions on push. Sister-site totals are not fetched at build time.

## Deploy

`scripts/build.py` writes `dist/` only. It does not fetch live pages. `design-handoff/` stays in the repo and is not copied. The build copies the repo `CNAME` into `dist/CNAME`. Canonical and `og:url` on the home page are `https://sarawak.news/`. About uses `https://sarawak.news/about.html`. `robots.txt` and `sitemap.xml` use the same origin. Internal links (`index.html`, `about.html`, `style.css`, `app.js`, `fonts/Geist-Variable.woff2`) are relative, so the site works at the domain root.

<!-- BEGIN GENERATED: hosting -->
| Field | Value |
| --- | --- |
| `hostname` | `sarawak.news` |
| `target` | GitHub Pages |
<!-- END GENERATED: hosting -->

`.github/workflows/build.yml` tests and builds on every pull request. A push to `main` deploys that build with GitHub Pages. `workflow_dispatch` can rebuild `main` by hand. The daily schedule is gone. It only existed to refresh counts, and the cards no longer show counts.

## Docs check

`.github/workflows/docs-check.yml` runs job `docs-check` on pull requests (`opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`). It diffs the PR with three dots (`base...head`). Watched paths are `site/*`, `kit/*` / `kit/**/*`, `scripts/build.py`, `scripts/analytics_registry.py`, `scripts/check_analytics_dist.py`, `scripts/docs_check_pr.py`, `.github/workflows/*`, `data/sites.json`, `data/site.json`, and `data/analytics.json`. A change there fails unless `docs/` also changes, or the PR has the `no-docs-needed` label. That prose check stays. `python3 kit/generate_docs.py --check` is a separate check. It only compares generated blocks to their source files.

## Analytics

IDs, cookie name, and CF `spa` live in `data/analytics.json` (fleet kit shape, `version: 1`, same as bantuan). The loader implementation lives in `kit/python/analytics_loader.py`. The registry implementation lives in `kit/python/analytics_registry.py`, and `scripts/analytics_registry.py` re-exports it. `scripts/build.py` calls `render_analytics_loader()` and emits one inline `<script data-sn-analytics-loader>` per page (edit the registry or the kit, not `dist/`). CI runs `scripts/check_analytics_dist.py` so each built HTML page has exactly one loader, only registry GA4 / CF tokens, only the registry cookie (plus per-host `legacy_internal_cookies` honour), and CF `spa` matching the registry (`false` here).

Registry fields for this site come from `data/analytics.json`. Per-host `legacy_internal_cookies` repeats the primary cookie name, and the loader still honours that list so already-marked devices stay excluded.

<!-- BEGIN GENERATED: analytics -->
| Field | Value |
| --- | --- |
| `ga4_measurement_id` | `G-SJMJ0R0GJS` |
| `cf_beacon_token` | `092a061973fc4d899cd2e4b52952af89` |
| `internal_cookie` | `sn_internal` |
| `hosts` | `sarawak.news`, `www.sarawak.news` |
<!-- END GENERATED: analytics -->

Loader behaviour:

1. **Production host gate** — runs only when `location.hostname` is the primary host or an alias. It does not load on localhost, `*.pages.dev`, `*.github.io`, `*.vercel.app`, or any other host.
2. **Internal traffic cookie** — `?internal=1` sets the registry `internal_cookie` (`sn_internal=1`; `path=/`, `max-age=31536000` ≈ 1 year, `SameSite=Lax`, plus `Secure` on HTTPS). `?internal=0` clears the primary and every listed `legacy_internal_cookies` name. A visit counts as internal when the primary **or** any legacy cookie is `=1`. While internal, `gtag('config', …, { traffic_type: 'internal' })` and the Cloudflare beacon is not loaded. Agents and automated checks that open the live site must use `?internal=1` (see `AGENTS.md`).
3. **Google Analytics 4.** After the host gate, the loader loads the measurement ID shown in the table above.
4. **Cloudflare Web Analytics.** The hub is served by GitHub Pages, not proxied through Cloudflare, so the loader embeds the zone site token from the table above. That token is shared with ai.sarawak.news. Filter by hostname in the dashboard. `spa` is false. The beacon loads only on registry hosts and only when the visit is not internal.

- No Content-Security-Policy is set; if one is added, allow `www.googletagmanager.com`, `*.google-analytics.com` and `static.cloudflareinsights.com`.
