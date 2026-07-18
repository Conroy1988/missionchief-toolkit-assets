PAYLOAD = '''## [4.15.4] - 2026-07-18

### Added
- Mission Requirements now shows bounded loading, explicit empty and explicit unavailable states instead of silently disappearing.
- Added a compact Report Mission control that opens a sanitised, pre-filled GitHub issue composer using the Mission Info Missing label.

### Fixed
- Native MissionChief mission windows are discovered even when `#missing_text` is absent, delayed, empty or moved.
- Fallback panels automatically upgrade to the live matrix when MissionChief later exposes valid requirement data.
- Reporting excludes tokens, webhooks, coordinates, addresses, chat, vehicle IDs and unrelated page HTML.

### Compatibility
- MissionChief remains the sole mission-window and requirement authority; no GitHub token or direct issue-creation credential is embedded in the userscript.
- Single-owner mounting, LSSM coexistence and Desktop, Tablet and iOS layouts remain intact.

'''
