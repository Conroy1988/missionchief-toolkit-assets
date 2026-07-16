#!/usr/bin/env python3
from pathlib import Path

package = Path(__file__).with_name("issue-93-mission-value.py")
text = package.read_text(encoding="utf-8")
old_open = "test_source = r'''#!/usr/bin/env python3"
new_open = 'test_source = r"""#!/usr/bin/env python3'
old_close = "\n'''\nTEST.write_text(test_source, encoding=\"utf-8\")"
new_close = '\n"""\nTEST.write_text(test_source, encoding="utf-8")'
if text.count(old_open) != 1:
    raise AssertionError("Expected one generated-test opening delimiter")
if text.count(old_close) != 1:
    raise AssertionError("Expected one generated-test closing delimiter")
corrected = text.replace(old_open, new_open, 1).replace(old_close, new_close, 1)
try:
    namespace = {"__name__": "__main__", "__file__": str(package)}
    exec(compile(corrected, str(package), "exec"), namespace, namespace)
finally:
    package.unlink(missing_ok=True)
