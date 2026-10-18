# Agents

Design or behaviour changes (CSS, templates, app JS, build scripts, config) must update docs/ (usually docs/design.md) in the same PR. Use the no-docs-needed label only for changes that truly need no docs.

See [docs/design.md](docs/design.md) for the live design system.

Pull requests run the **docs check** GitHub Action on design/behaviour paths. If the check fails, update `docs/` or add the **`no-docs-needed`** label when documentation does not need to change.

## Analytics (GA4 internal traffic)

When agents, QA, cloud agents, daily scans, or screenshot checks open the **live** site ([https://sarawak.news/](https://sarawak.news/)), append `?internal=1` (for example `https://sarawak.news/?internal=1` or `https://sarawak.news/about.html?internal=1`). That sets a long-lived first-party cookie so GA4 receives `traffic_type: 'internal'`. Use `?internal=0` to clear it. GA loads only on `sarawak.news` / `www.sarawak.news` — never on localhost or preview hosts. Details: [docs/design.md](docs/design.md) (Analytics).
