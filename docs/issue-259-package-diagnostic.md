# Issue #259 final-package diagnostic

The reviewed v4.20.13 package was executed in an isolated temporary copy. No production or real branch runtime file was changed by this diagnostic.

- Return code: `1`

## Standard output

```text

```

## Standard error

```text
node:assert:150
  throw new AssertionError(obj);
  ^

AssertionError [ERR_ASSERTION]: Railway Police badge and current crew contribute selected trained personnel

0 !== 2

    at Object.<anonymous> (/tmp/issue-259-hmie82ql/repo/.github/scripts/test_mission_requirements_runtime.js:1251:8)
    at Module._compile (node:internal/modules/cjs/loader:1781:14)
    at Object..js (node:internal/modules/cjs/loader:1913:10)
    at Module.load (node:internal/modules/cjs/loader:1505:32)
    at Function._load (node:internal/modules/cjs/loader:1309:12)
    at wrapModuleLoad (node:internal/modules/cjs/loader:254:19)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:171:5)
    at node:internal/main/run_main_module:36:49 {
  generatedMessage: false,
  code: 'ERR_ASSERTION',
  actual: 0,
  expected: 2,
  operator: 'strictEqual',
  diff: 'simple'
}

Node.js v22.23.1
Traceback (most recent call last):
  File "/tmp/issue-259-hmie82ql/repo/.github/development-packages/finalise-issue-259-v4.20.13-corrected.py", line 13, in <module>
    runpy.run_path(str(PACKAGE), run_name="__main__")
  File "<frozen runpy>", line 286, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "/tmp/issue-259-hmie82ql/repo/.github/development-packages/finalise-issue-259-v4.20.13.py", line 494, in <module>
    main()
  File "/tmp/issue-259-hmie82ql/repo/.github/development-packages/finalise-issue-259-v4.20.13.py", line 490, in main
    run_checks()
  File "/tmp/issue-259-hmie82ql/repo/.github/development-packages/finalise-issue-259-v4.20.13.py", line 476, in run_checks
    subprocess.run(command, cwd=ROOT, check=True)
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['node', '/tmp/issue-259-hmie82ql/repo/.github/scripts/test_mission_requirements_runtime.js']' returned non-zero exit status 1.

```
