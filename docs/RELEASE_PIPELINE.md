# Release Pipeline

The MissionChief Map Command Toolkit uses GitHub as the canonical source and Greasy Fork as the public distribution mirror.

## Controlled release path

```text
src/MissionChief_Map_Command_Toolkit.user.js
        ↓
Validation and JavaScript syntax checks
        ↓
Byte-identical dist .user.js and .txt files
        ↓
Version and CHANGELOG verification
        ↓
Immutable release bundle and SHA-256 manifest
        ↓
GitHub tag and Release
        ↓
Greasy Fork release webhook and source sync
        ↓
Live Greasy Fork version verification
        ↓
Discord release announcement
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
- Greasy Fork release synchronization is enabled;
- the GitHub Release does not already exist;
- the operator enters the explicit `RELEASE` confirmation.

Discord is notified only after Greasy Fork serves the expected version.

## Standard release procedure

1. Update the canonical source under `src/`.
2. Increase `@version`.
3. Add the matching section to `CHANGELOG.md`.
4. Allow the validation workflow to pass.
5. Run **Actions → Release Toolkit**.
6. Enter the version and type `RELEASE`.
7. Review the workflow summary, GitHub Release, Greasy Fork version and Discord post.

## Recovery behaviour

If GitHub publishes successfully but Greasy Fork has not yet synchronized, the workflow does not send Discord. The fallback monitor continues checking and can report a verified release without repeating previously announced versions.

## Public asset stability

Existing audio, images, manifests and theme paths are treated as public API. They must not be moved or renamed until every live reference has been migrated or compatibility aliases are in place.
