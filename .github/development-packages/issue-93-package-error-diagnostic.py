#!/usr/bin/env python3
from pathlib import Path
import shutil
import tempfile
import traceback

root = Path(__file__).resolve().parents[2]
original = root / ".github" / "development-packages" / "issue-93-mission-value.py"
text = original.read_text(encoding="utf-8")
text = text.replace("test_source = r'''#!/usr/bin/env python3", 'test_source = r"""#!/usr/bin/env python3', 1)
text = text.replace("\n'''\nTEST.write_text(test_source, encoding=\"utf-8\")", '\n"""\nTEST.write_text(test_source, encoding="utf-8")', 1)
output = root / ".github" / "diagnostics" / "issue-93-package-error.txt"
output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="issue-93-package-") as temp:
    sandbox = Path(temp) / "repo"
    shutil.copytree(root, sandbox, ignore=shutil.ignore_patterns(".git"))
    sandbox_package = sandbox / ".github" / "development-packages" / "issue-93-mission-value.py"
    sandbox_package.write_text(text, encoding="utf-8")
    try:
        namespace = {"__name__": "__main__", "__file__": str(sandbox_package)}
        exec(compile(text, str(sandbox_package), "exec"), namespace, namespace)
        report = "Package completed successfully in the isolated copy.\n"
    except BaseException:
        report = traceback.format_exc()
output.write_text(report, encoding="utf-8")
print(report)
