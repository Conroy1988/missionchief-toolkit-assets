# Issue #70 package failure

```text
Traceback (most recent call last):
  File "/home/runner/work/missionchief-toolkit-assets/missionchief-toolkit-assets/.github/development-packages/issue-70-package-diagnostic.py", line 13, in <module>
    exec(compile(fixed, str(package), 'exec'))
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".github/development-packages/issue-70-financial-image-layout-fix.py", line 192
    TEST.write_text(r'''#!/usr/bin/env python3
                    ^
SyntaxError: invalid syntax. Perhaps you forgot a comma?

```
