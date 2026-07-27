#!/usr/bin/env python3
"""Make the generated isolated DOM integration test advance tasks and append real nodes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / ".github/scripts/test_ui_mount_integration.mjs"
text = TEST.read_text(encoding="utf-8")
old_flush = '''async function flush(rounds = 80) {
  for (let index = 0; index < rounds; index += 1) await Promise.resolve();
}
'''
new_flush = '''async function flush(rounds = 20) {
  for (let index = 0; index < rounds; index += 1) {
    await Promise.resolve();
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}

function appendMemberBody(document, html) {
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html;
  while (wrapper.firstChild) document.body.appendChild(wrapper.firstChild);
}
'''
if text.count(old_flush) != 1:
    raise RuntimeError("Unable to patch integration queue flush")
text = text.replace(old_flush, new_flush, 1)
old_delayed = 'delayed.window.document.body.insertAdjacentHTML("beforeend", memberBody);\n'
new_delayed = 'appendMemberBody(delayed.window.document, memberBody);\n'
if text.count(old_delayed) != 1:
    raise RuntimeError("Unable to patch delayed fixture insertion")
text = text.replace(old_delayed, new_delayed, 1)
old_rerender = 'delayed.window.document.body.insertAdjacentHTML("beforeend", memberBody.replaceAll("/profile/10", "/profile/20").replaceAll("/profile/11", "/profile/21"));\n'
new_rerender = 'appendMemberBody(delayed.window.document, memberBody.replaceAll("/profile/10", "/profile/20").replaceAll("/profile/11", "/profile/21"));\n'
if text.count(old_rerender) != 1:
    raise RuntimeError("Unable to patch rerender fixture insertion")
text = text.replace(old_rerender, new_rerender, 1)
TEST.write_text(text, encoding="utf-8")
print("UI mount integration now advances task queues and appends browser-equivalent nodes.")
