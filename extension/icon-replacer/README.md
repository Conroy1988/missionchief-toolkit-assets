# Matching icon replacement — 1.3.2 test

Operations → Copy station icons → Switch Icon.

Scan custom building icons by building type and dispatch centre, or across all owned buildings. Identical URLs are downloaded once; at most four image reads run together. Pixel fingerprints group identical images under different URLs. The catalogue is saved per account and scope, without image bytes.

Choose the original and replacement thumbnails, preview the matches, deselect any buildings to retain, then review and confirm replacement. Default game icons and unreadable images are excluded. The selected scope supplies both icon choices.

Each building is checked against its recorded identity and original pixels before upload. The existing native form copier preserves other fields and verifies the saved image. Progress is saved before each upload. Pause and Review & resume retain the plan; uncertain uploads are verified without automatic replay. A user can explicitly exclude unresolved buildings from the remaining plan.

Operations rows use shared name, description and status columns, with descriptions below the title on narrow panels.

The popup is simplified to the enable switch, apply/reload, Discord Support and a small Ko-fi link. It retains the reload checks for running tasks and unsaved settings. Old setup, statistics and task panels are removed.

Build: `python3 extension/build-icon-replacer-test.py`.
Test: `node --test extension/icon-replacer/*.test.mjs` after building.

Output: `.dev/MissionChief-Toolkit-Extension-1.3.2-test.zip`.
Live uploads and visual browser acceptance remain pending. The stable Store build script and previous submission are unchanged.

Progress remains visible in a sticky, high-contrast panel with processed counts, percentage, current action/building and elapsed time. Stage messages appear before network requests complete; the verified count only advances after verification or an explicit skip.

Preview reuses the chosen scan group, refreshing only building records to exclude removed or out-of-scope buildings. It does not rescan images. New or changed icons require Scan / refresh icons; execution rechecks the original pixels before each upload.
