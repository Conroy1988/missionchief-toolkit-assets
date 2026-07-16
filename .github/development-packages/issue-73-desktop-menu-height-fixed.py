from pathlib import Path

original = Path('.github/development-packages/issue-73-desktop-menu-height.py')
text = original.read_text(encoding='utf-8')
start_old = "TEST.write_text(r'''#!/usr/bin/env python3"
start_new = 'TEST.write_text(r\"\"\"#!/usr/bin/env python3'
end_old = '''if __name__ == "__main__":
    raise SystemExit(main())
''', encoding='utf-8')'''
end_new = '''if __name__ == "__main__":
    raise SystemExit(main())
\"\"\", encoding='utf-8')'''
if text.count(start_old) != 1:
    raise RuntimeError(f'Expected one embedded-test opening delimiter, found {text.count(start_old)}')
if text.count(end_old) != 1:
    raise RuntimeError(f'Expected one embedded-test closing delimiter, found {text.count(end_old)}')
text = text.replace(start_old, start_new, 1).replace(end_old, end_new, 1)
exec(compile(text, str(original), 'exec'), {'__name__': '__main__', '__file__': str(original)})
original.unlink()
