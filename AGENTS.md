# Agents

Design or behaviour changes (CSS, templates, app JS, build scripts, config) must update docs/ (usually docs/design.md) in the same PR. Use the no-docs-needed label only for changes that truly need no docs.

See [docs/design.md](docs/design.md) for the live design system.

Pull requests run the **docs check** GitHub Action on design/behaviour paths. If the check fails, update `docs/` or add the **`no-docs-needed`** label when documentation does not need to change.

## Analytics (internal traffic)

When agents, QA, cloud agents, daily scans, or screenshot checks open the **live** site ([https://sarawak.news/](https://sarawak.news/)), append `?internal=1` (for example `https://sarawak.news/?internal=1` or `https://sarawak.news/about.html?internal=1`). That sets the registry cookie from `data/analytics.json` (`sn_internal`, ~1 year) so:

- GA4 receives `traffic_type: 'internal'`
- the Cloudflare Web Analytics beacon is **not** loaded (test visits are not counted there either)

Use `?internal=0` to clear the primary and listed `legacy_internal_cookies`. The loader also treats any per-host `legacy_internal_cookies` entry as internal (on hub that list is `["sn_internal"]` — same as primary). Both trackers load only on `sarawak.news` / `www.sarawak.news` — never on localhost or preview hosts. Details: [docs/design.md](docs/design.md) (Analytics).
