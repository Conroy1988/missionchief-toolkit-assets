#!/usr/bin/env python3
from pathlib import Path
import subprocess
import traceback

package = Path('.github/development-packages/issue-70-financial-image-layout-fix.py')
text = package.read_text(encoding='utf-8')
opening = "TEST.write_text(r'''#!/usr/bin/env python3"
closing = "if __name__ == \"__main__\":\n    raise SystemExit(main())\n''', encoding=\"utf-8\")"
fixed = text.replace(opening, 'TEST.write_text(r"""#!/usr/bin/env python3', 1)
fixed = fixed.replace(closing, 'if __name__ == "__main__":\n    raise SystemExit(main())\n""", encoding="utf-8")', 1)
try:
    exec(compile(fixed, str(package), 'exec'))
except BaseException:
    details = traceback.format_exc()
    subprocess.run(['git', 'reset', '--hard', 'HEAD'], check=True)
    for path in [
        package,
        Path('.github/development-packages/issue-70-financial-image-layout-fix-loader.py'),
        Path('.github/development-packages/issue-70-financial-image-layout-fix-loader-v2.py'),
        Path('.github/audits/issue-70-financial-renderer-context.md'),
        Path('.github/audits/issue-70-financial-reconciliation-context.md'),
    ]:
        path.unlink(missing_ok=True)
    report = Path('.github/audits/issue-70-package-failure.md')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('# Issue #70 package failure\n\n```text\n' + details + '\n```\n', encoding='utf-8')
    print(details)
