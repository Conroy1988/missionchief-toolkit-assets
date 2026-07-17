#!/usr/bin/env python3
from pathlib import Path

package = Path('.github/development-packages/issue-70-financial-image-layout-fix.py')
text = package.read_text(encoding='utf-8')
opening = "TEST.write_text(r'''#!/usr/bin/env python3"
closing = "if __name__ == \"__main__\":\n    raise SystemExit(main())\n''', encoding=\"utf-8\")"
replacement_opening = 'TEST.write_text(r"""#!/usr/bin/env python3'
replacement_closing = 'if __name__ == "__main__":\n    raise SystemExit(main())\n""", encoding="utf-8")'
if text.count(opening) != 1:
    raise RuntimeError(f'Expected one generated-test opening delimiter, found {text.count(opening)}')
if text.count(closing) != 1:
    raise RuntimeError(f'Expected one generated-test closing delimiter, found {text.count(closing)}')
fixed = text.replace(opening, replacement_opening, 1).replace(closing, replacement_closing, 1)
package.unlink()
Path('.github/development-packages/issue-70-financial-image-layout-fix-loader.py').unlink(missing_ok=True)
exec(compile(fixed, str(package), 'exec'))
