# Issue #260 clean-package diagnostic

- Return code: `1`

## Standard output

```text

```

## Standard error

```text
node:internal/assert/utils:77
    throw err;
    ^

AssertionError [ERR_ASSERTION]: unmapped role capacity remains safely uncertain
    at Object.<anonymous> (/tmp/issue-260-clean-tjhnmivx/repo/.github/scripts/test_mission_requirements_runtime.js:971:1)
    at Module._compile (node:internal/modules/cjs/loader:1781:14)
    at Object..js (node:internal/modules/cjs/loader:1913:10)
    at Module.load (node:internal/modules/cjs/loader:1505:32)
    at Function._load (node:internal/modules/cjs/loader:1309:12)
    at wrapModuleLoad (node:internal/modules/cjs/loader:254:19)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:171:5)
    at node:internal/main/run_main_module:36:49 {
  generatedMessage: false,
  code: 'ERR_ASSERTION',
  actual: false,
  expected: true,
  operator: '==',
  diff: 'simple'
}

Node.js v22.23.1
Traceback (most recent call last):
  File "/tmp/issue-260-clean-tjhnmivx/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 222, in <module>
    main()
  File "/tmp/issue-260-clean-tjhnmivx/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 218, in main
    run_checks()
  File "/tmp/issue-260-clean-tjhnmivx/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 205, in run_checks
    subprocess.run(command, cwd=ROOT, check=True)
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['node', '/tmp/issue-260-clean-tjhnmivx/repo/.github/scripts/test_mission_requirements_runtime.js']' returned non-zero exit status 1.

```
