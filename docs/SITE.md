# GitHub Pages documentation site

The public MissionChief Map Command Toolkit site is generated from repository-controlled source data and deployed through GitHub Actions.

## Public URL

`https://conroy1988.github.io/missionchief-toolkit-assets/`

## Source model

The site is deliberately separated into:

| Source | Purpose |
|---|---|
| `docs/site-data.json` | Feature catalogue, themes, documentation chapters, shortcuts and troubleshooting |
| `docs/site-assets/site.css` | Responsive visual system |
| `docs/site-assets/site.js` | Navigation, filtering, date formatting and copy controls |
| `status/release-dashboard.json` | Current version and verified release health |
| `.github/release-settings.json` | Greasy Fork installation and project links |
| `CHANGELOG.md` | Release history |
| `README.md` | Primary GitHub landing page and installation summary |
| `help/index.html` | Searchable Help Centre loaded by the userscript |
| `docs/greasyfork-description.md` | Greasy Fork-synchronised Additional Info page |
| `.github/scripts/build_pages_site.py` | Deterministic static-site generator and link validator |

The generated `_site/` directory is an Actions artifact. It is not committed to `main`.

## Pages

- Home and installation
- Complete feature catalogue
- Interface-theme and payout-presentation gallery
- Documentation centre
- Generated changelog
- Generated release status

## Validation

Every relevant pull request:

1. Compiles the Python generator.
2. Checks the site JavaScript.
3. Validates the JSON catalogue.
4. Builds all pages.
5. Verifies internal links and base-path handling.
6. Enforces output file-count and size limits.
7. Cross-checks the README, Help Centre, Pages catalogue and Greasy Fork description for current version, theme, feature and privacy claims.
8. Retains a complete preview artifact for 14 days.

A deployment occurs only from `main` or a manual workflow run.

## Maintaining content

Edit the structured catalogue rather than generated HTML. The build script escapes user-facing source values and fails when required sections, release data, pages or internal targets are missing.

Feature documentation should describe current public behaviour. The README, Help Centre, Pages catalogue and Greasy Fork description form one public documentation contract and must be updated together when shared claims change. Experimental ideas belong in issues or Discussions rather than the published catalogue.

## Theme safety

The site contains independent CSS-rendered previews. It does not import, rewrite or override any userscript theme code. Existing Toolkit theme styling and stable public asset paths remain compatibility-critical.

## GitHub Pages setting

The repository Pages source must be set to **GitHub Actions**. The deployment workflow cannot enable Pages with the default `GITHUB_TOKEN`; GitHub requires an administrative token for automatic enablement.
