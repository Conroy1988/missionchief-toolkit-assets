#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
package = root / ".github/development-packages/repository-documentation-accuracy-audit.py"
text = package.read_text(encoding="utf-8")
old = '    "5. Enforces output file-count and size limits.\\n6. Retains a complete preview artifact for 14 days.",\n    "5. Enforces output file-count and size limits.\\n6. Cross-checks the README, Help Centre, Pages catalogue and Greasy Fork description for current version, theme, feature and privacy claims.\\n7. Retains a complete preview artifact for 14 days.",'
new = '    "6. Enforces output file-count and size limits.\\n7. Retains a complete preview artifact for 14 days.",\n    "6. Enforces output file-count and size limits.\\n7. Cross-checks the README, Help Centre, Pages catalogue and Greasy Fork description for current version, theme, feature and privacy claims.\\n8. Retains a complete preview artifact for 14 days.",'
if text.count(old) != 1:
    raise RuntimeError(f"SITE package anchor count: {text.count(old)}")
package.write_text(text.replace(old, new, 1), encoding="utf-8")
subprocess.run(["python3", str(package)], cwd=root, check=True)
package.unlink()
