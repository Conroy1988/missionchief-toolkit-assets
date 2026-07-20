#!/usr/bin/env python3
from pathlib import Path
source = (Path(__file__).resolve().parents[2] / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
for value in [
    "// @version      4.20.9",
    "version: '4.20.9',",
    "guideVersion: '4.20.9',",
    '"training":["Railway Police Officer","Railway Police"]',
    "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name'] :",
]:
    assert source.count(value) == 1
print("Railway Police metadata anchors passed")
