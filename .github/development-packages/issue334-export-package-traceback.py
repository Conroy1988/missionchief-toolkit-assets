#!/usr/bin/env python3
from pathlib import Path
import shutil
import tempfile
import traceback

root = Path(__file__).resolve().parents[2]
package_name = 'issue332-mission-monitoring-toggles-v42032.py'
package = Path(__file__).with_name(package_name)
diagnostic = root / '.github' / 'diagnostics' / 'issue334-package-traceback.txt'
diagnostic.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(root, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    temp_package = work / '.github' / 'development-packages' / package_name
    try:
        namespace = {'__file__': str(temp_package), '__name__': '__main__'}
        code = temp_package.read_text(encoding='utf-8')
        exec(compile(code, str(temp_package), 'exec'), namespace)
    except BaseException:
        result = traceback.format_exc()
    else:
        result = 'Package completed successfully in the isolated repository copy.\n'
diagnostic.write_text(result, encoding='utf-8')
package.unlink(missing_ok=True)
print('Exported isolated Issue #334 package diagnostic')
