#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".github/scripts/deep_performance_audit.py"
spec = importlib.util.spec_from_file_location("deep_performance_audit", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

fixture = """// ==UserScript==
// @version 9.9.9
// ==/UserScript==
const MutationObserverCtor = window.MutationObserver;
function installFeature() {
  const observer = new MutationObserverCtor(records => { if (records.length) renderPanel(); });
  observer.observe(document.body, { childList: true, subtree: true });
  runtimeTrackObserver(observer);
  runtimeSetTimeout(() => renderPanel(), 250);
}
function renderPanel() {
  const root = document.querySelector('#root');
  const again = document.querySelector('#root');
  if (!root) return;
  root.textContent = 'ok';
  root.setAttribute('aria-live', 'polite');
}
function styles() {
  const css = `""" + ("x{display:block;}\n" * 100) + """`;
  return css;
}
"""

with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "fixture.user.js"
    source.write_text(fixture, encoding="utf-8")
    data = module.report(source)
    assert data["source"]["version"] == "9.9.9"
    assert data["summary"]["namedFunctions"] == 3
    assert data["summary"]["observerRegistrations"] == 1
    assert data["summary"]["broadSubtreeObservers"] == 1
    assert data["summary"]["schedulerCalls"] == 1
    observer = data["observerRegistrations"][0]
    assert observer["constructor"] == "MutationObserver"
    assert observer["tracked"] is True
    assert observer["disconnectSignal"] is True
    assert data["repeatedSelectors"][0]["selector"] == "#root"
    assert data["repeatedSelectors"][0]["count"] == 2
    assert data["largeTemplates"][0]["classification"] == "css"
    output = module.markdown(data)
    assert "Highest structural hotspot scores" in output
    assert "installFeature" in output

print("Deep performance audit fixtures passed")
