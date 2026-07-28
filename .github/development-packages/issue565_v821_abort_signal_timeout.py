#!/usr/bin/env python3
"""Remove the extra managed timer from the v8.2.1 release request path."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
STATIC_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")
old = '''    async function requestTransportSweepOptionalRelease(release) {
        const ownerWindow = release?.control?.ownerDocument?.defaultView || pageWindow;
        const fetcher = ownerWindow?.fetch || pageWindow?.fetch;
        if (typeof fetcher !== 'function') throw new Error('same-origin request API is unavailable');
        const Controller = ownerWindow?.AbortController || pageWindow?.AbortController;
        const controller = typeof Controller === 'function' ? new Controller() : null;
        const timeoutHandle = controller
            ? runtimeSetTimeout(() => controller.abort(), TRANSPORT_SWEEP_OPTIONAL_RELEASE_REQUEST_TIMEOUT_MS)
            : null;
        try {
            const response = await fetcher.call(ownerWindow, release.href, {
                method: 'GET',
                credentials: 'same-origin',
                redirect: 'follow',
                cache: 'no-store',
                signal: controller?.signal,
            });
            if (!response?.ok) throw new Error(`request returned HTTP ${response?.status || 'unknown'}`);
            await response.text();
            return { status: response.status, url: String(response.url || release.href) };
        } finally {
            if (timeoutHandle !== null) runtimeClearTimeout(timeoutHandle);
        }
    }
'''
new = '''    async function requestTransportSweepOptionalRelease(release) {
        const ownerWindow = release?.control?.ownerDocument?.defaultView || pageWindow;
        const fetcher = ownerWindow?.fetch || pageWindow?.fetch;
        if (typeof fetcher !== 'function') throw new Error('same-origin request API is unavailable');
        const AbortSignalCtor = ownerWindow?.AbortSignal || pageWindow?.AbortSignal;
        const timeoutSignal = typeof AbortSignalCtor?.timeout === 'function'
            ? AbortSignalCtor.timeout(TRANSPORT_SWEEP_OPTIONAL_RELEASE_REQUEST_TIMEOUT_MS)
            : undefined;
        const response = await fetcher.call(ownerWindow, release.href, {
            method: 'GET',
            credentials: 'same-origin',
            redirect: 'follow',
            cache: 'no-store',
            signal: timeoutSignal,
        });
        if (!response?.ok) throw new Error(`request returned HTTP ${response?.status || 'unknown'}`);
        await response.text();
        return { status: response.status, url: String(response.url || release.href) };
    }
'''
if source.count(old) != 1:
    raise RuntimeError(f"Expected one managed-timeout release request helper, found {source.count(old)}")
source = source.replace(old, new, 1)
SOURCE.write_text(source, encoding="utf-8")

test = STATIC_TEST.read_text(encoding="utf-8")
old_test = '    assert "runtimeSetTimeout(" in helper and "runtimeClearTimeout(" in helper\n'
new_test = '''    assert "AbortSignalCtor.timeout" in helper
    assert "runtimeSetTimeout(" not in helper
    assert "runtimeClearTimeout(" not in helper
'''
if test.count(old_test) != 1:
    raise RuntimeError("Issue #565 timeout assertion changed")
STATIC_TEST.write_text(test.replace(old_test, new_test, 1), encoding="utf-8")

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
source_sha = hashlib.sha256(source_bytes).hexdigest()
source_lines = len(source_text.splitlines())
manifest_lines = source_text.count("\n") + 1
for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{source_sha}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{source_sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({
    "version": "8.2.1",
    "sha256": source_sha,
    "bytes": len(source_bytes),
    "lines": manifest_lines,
})
manifest["metadata"]["runtimeVersion"] = "8.2.1"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate["sourceBytes"] = len(source_bytes)
candidate["sourceLines"] = source_lines
candidate["sourceSha256"] = source_sha
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), source_lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + source_lines - old_lines
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"v8.2.1 zero-timer request timeout applied: {source_sha}, {len(source_bytes)} bytes, {source_lines} lines")
