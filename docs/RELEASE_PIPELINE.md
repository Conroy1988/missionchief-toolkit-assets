# Release Pipeline

The MissionChief Map Command Toolkit uses GitHub as its canonical source and immutable package archive. The TKB Website is the sole supported public installation and automatic-update authority. Greasy Fork is fully retired and is not generated, published, verified, monitored or used for recovery.

## Controlled release path

```text
src/MissionChief_Map_Command_Toolkit.user.js
        ↓
Exact-head validation and JavaScript syntax checks
        ↓
Immutable TKB install, update and metadata candidate
        ↓
Version, changelog and SHA-256 verification
        ↓
GitHub Release archive
        ↓
Live TKB install, update and metadata verification
        ↓
Private recovery backup
        ↓
Discord release announcement
        ↓
Governed release dashboard, manifest and telemetry
```

## Release channels

| Event | Destination |
|---|---|
| Ordinary development commits | `Mission-Chief-Dev` |
| Verified public releases | `Mission-Chief` |
| Validation failures | GitHub Actions only |
| No-change checks | No notification |

## Release safety gates

A production release is blocked unless:

- the requested version is valid and matches userscript and runtime metadata;
- `CHANGELOG.md` contains an entry for that exact version;
- the JavaScript parses successfully;
- generated install and update assets are byte-identical to the canonical source;
- the release manifest SHA-256 matches the generated userscript;
- the GitHub Release does not already exist;
- the live TKB install and update routes serve the exact canonical release bytes;
- the live TKB metadata route reports the requested version;
- the private recovery archive is verified;
- the operator enters the explicit `RELEASE` confirmation.

Discord is notified only after the live TKB distribution and private backup are verified. No retired external channel participates in release success.

## Standard release procedure

1. Update the canonical source under `src/`.
2. Increase `@version` and the internal runtime version.
3. Add the matching section to `CHANGELOG.md`.
4. Allow the exact-head validation workflow to pass.
5. Run **Actions → Release Toolkit** or the guarded owner release command.
6. Enter the version and type `RELEASE`.
7. Review the workflow summary, TKB routes, GitHub Release, private backup, release ledger and Discord post.

## Recovery behaviour

Recovery can verify a release, retry the private backup, retry Discord, reconstruct the governed dashboard or repair stable GitHub Release assets. Every retained operation verifies TKB Website authority and records operational state on `release-state`; none can publish to Greasy Fork.

## Public asset stability

Existing audio, images, manifests and theme paths are treated as public API. They must not be moved or renamed until every live reference has been migrated or compatibility aliases are in place.
