# MissionChief Financial Vault Gateway

This Cloudflare Worker is the security boundary between the public userscript and GitHub.

The userscript contains **no GitHub repository token, GitHub App private key, installation token or HMAC secret**. The Worker creates short-lived GitHub App installation tokens server-side and accepts only two fixed operations:

- `POST /v1/vault/sync` — validate and merge a player-linked Financial Vault.
- `POST /v1/benchmark` — validate one aggregate benchmark sample.

Clients cannot choose a repository path. The gateway derives storage paths from the validated MissionChief player ID/name and splits ledger history into monthly JSON files. A random Financial Vault link key is used to link the same player across devices. The stored ownership proof is an HMAC generated with a server-only secret.

## Required setup

1. Create a dedicated GitHub repository for vault data. Public or private is supported; private is recommended even when the game data is not considered sensitive.
2. Create a GitHub App with **Contents: Read and write** access only to that repository.
3. Install the App on the vault repository.
4. Deploy this Worker with Wrangler.
5. Set these as Cloudflare Worker secrets using `wrangler secret put`:
   - `GITHUB_APP_ID`
   - `GITHUB_INSTALLATION_ID`
   - `GITHUB_APP_PRIVATE_KEY`
   - `VAULT_HMAC_SECRET`
6. Copy `wrangler.toml.example` to `wrangler.toml`, fill in the non-secret repository values, and deploy.
7. Enter the deployed HTTPS Worker URL in the Toolkit's **Secure gateway URL** field.

## Server-side restrictions

- MissionChief origins only, plus explicitly configured extra origins.
- HTTPS/CORS enforced.
- Fixed endpoint and schema validation.
- Maximum request, transaction and history limits.
- Player-derived paths only; no arbitrary filename or branch input.
- One ownership proof per player vault.
- Monthly ledger chunks to avoid unbounded GitHub files.
- Conflict retries for multi-device writes.
- Anonymous benchmark submissions are restricted to one overwriteable daily file per source IP.

Cloudflare rate-limiting rules should also be applied to both POST endpoints before public launch.
