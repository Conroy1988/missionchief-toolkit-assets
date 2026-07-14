# MissionChief Financial Command

Financial Command uses this public repository for versioned intelligence only:

- transaction-classification rules;
- audit and risk thresholds;
- safe deep-scan policy;
- schemas, documentation and future public report templates.

## Player data model

MissionChief player financial history is **not uploaded to this repository**. The Toolkit reads the authenticated player's own MissionChief credit ledger and stores the resulting archive locally in that browser.

Users can move history between their own devices using:

- **Export Archive / Import Archive**, which contains game-financial history but no Discord webhook; or
- **Export All / Import All**, which is a private recovery backup and may contain both the Discord webhook and local financial history.

The Toolkit does not contain or request a GitHub repository token, GitHub App private key or write-capable GitHub credential.

## Public feeds

- `v1/classification-rules.json` — validated transaction classification rules.
- `v2/audit-policy.json` — validated risk thresholds and deep-scan limits.
- `v2/manifest.json` — current Financial Command architecture and feed locations.

The superseded remote player vault, Cloudflare write gateway and benchmark submission pipeline were removed for v4.6.0.
