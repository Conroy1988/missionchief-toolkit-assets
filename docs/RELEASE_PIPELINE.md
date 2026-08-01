# Release Pipeline

The MissionChief Map Command Toolkit uses GitHub as the canonical source and immutable package archive. TKB owns the supported public install/update URLs. Greasy Fork is a non-blocking discovery mirror.

## Controlled release path

```text
src/MissionChief_Map_Command_Toolkit.user.js
        ↓
Validation and JavaScript syntax checks
        ↓
Full TKB script plus install, update and metadata assets
        ↓
Version and CHANGELOG verification
        ↓
Immutable release bundle and SHA-256 manifest
        ↓
GitHub tag and immutable Release assets
        ↓
TKB redirect routes resolve the verified assets
        ↓
First-party package, metadata and private-backup verification
        ↓
Discord release announcement and non-blocking Greasy Fork check
        ↓
Dashboard and migration records updated
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

- the requested version is valid and matches the userscript metadata;
- `CHANGELOG.md` contains an entry for that exact version;
- the JavaScript parses successfully;
- the generated `.user.js` and `.txt` files are byte-identical;
- the release manifest hash matches the generated userscript;
- the TKB install and update assets are byte-identical to the canonical release;
- the TKB metadata asset reports the requested version;
- the separate Greasy Fork mirror is below both the governed 1,750,000-character budget and the service's 2,097,152-character hard limit;
- the Greasy Fork stylesheet resource is immutable and SHA-256 pinned;
- the GitHub Release does not already exist;
- the operator enters the explicit `RELEASE` confirmation.

Discord is notified only after the first-party TKB distribution and private backup are verified. Greasy Fork delay is recorded but does not block production.

If Greasy Fork rejects or delays a release, keep TKB production live and investigate the mirror separately. Never upload a different executable payload manually. The governed mirror removes only the embedded non-executable stylesheet and loads that exact release resource through a SHA-256 integrity pin.

## Standard release procedure

1. Update the canonical source under `src/`.
2. Increase `@version`.
3. Add the matching section to `CHANGELOG.md`.
4. Allow the validation workflow to pass.
5. Run **Actions → Release Toolkit**.
6. Enter the version and type `RELEASE`.
7. Review the workflow summary, TKB routes, statistics feed, GitHub Release, mirror state and Discord post.

## Recovery behaviour

If GitHub and the TKB routes publish successfully but Greasy Fork has not synchronized, the release still completes. The mirror monitor may record later propagation without repeating the release, backup or announcement.

## Public asset stability

Existing audio, images, manifests and theme paths are treated as public API. They must not be moved or renamed until every live reference has been migrated or compatibility aliases are in place.
