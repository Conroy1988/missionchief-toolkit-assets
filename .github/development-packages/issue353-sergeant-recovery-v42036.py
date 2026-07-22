#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REVIEWED_COMMIT = "02bebbf995984c2aa81e0c20745ae12dd52f1581"
PACKAGE_PATH = ".github/development-packages/issue353-sergeant-recovery-v42036.py"

subprocess.check_call(["git", "fetch", "--quiet", "origin", REVIEWED_COMMIT])
reviewed = subprocess.check_output(
    ["git", "show", f"{REVIEWED_COMMIT}:{PACKAGE_PATH}"],
    text=True,
)
reviewed = reviewed.replace(
    "const issue353RefreshDoc = new FakeDocument();\nissue353RefreshDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/353' } };\napi.observeDocument(issue353RefreshDoc);",
    "const issue353RefreshDoc = new FakeDocument();\nissue353RefreshDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/353' } };\nconst issue353ListenerStart = listenedEvents.length;\napi.observeDocument(issue353RefreshDoc);",
    1,
)
reviewed = reviewed.replace(
    "flushAnimationFrames();\n\n'''",
    "flushAnimationFrames();\nlistenedEvents.splice(issue353ListenerStart);\n\n'''",
    1,
)
if "issue353ListenerStart" not in reviewed or "listenedEvents.splice(issue353ListenerStart);" not in reviewed:
    raise RuntimeError("Issue #353 fixture cleanup patch was not applied")
exec(
    compile(reviewed, PACKAGE_PATH, "exec"),
    {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"},
)
