#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

PACKAGE = Path(__file__).with_name("issue-269-matrix-crew-alias-hotfix.py")
spec = importlib.util.spec_from_file_location("issue_269_package", PACKAGE)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load Issue 269 package")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def replace_first(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count < 1:
        raise RuntimeError(f"{label}: required marker not found")
    print(f"{label}: replacing first of {count} matching markers")
    return text.replace(old, new, 1)


module.replace_once = replace_first
module.main()
