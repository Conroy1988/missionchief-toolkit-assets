# Issue #70 source transformation failure

## Standard output

```text

```

## Standard error

```text
/tmp/mcms-financial-image-xxttvzdk/financial-image-layout-contract.js:19
function financialSnapshotRows(report) {
^^^^^^^^

SyntaxError: Unexpected token 'function'
    at wrapSafe (node:internal/modules/cjs/loader:1713:18)
    at Module._compile (node:internal/modules/cjs/loader:1755:20)
    at Object..js (node:internal/modules/cjs/loader:1913:10)
    at Module.load (node:internal/modules/cjs/loader:1505:32)
    at Function._load (node:internal/modules/cjs/loader:1309:12)
    at wrapModuleLoad (node:internal/modules/cjs/loader:254:19)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:171:5)
    at node:internal/main/run_main_module:36:49

Node.js v22.23.1
Traceback (most recent call last):
  File "/home/runner/work/missionchief-toolkit-assets/missionchief-toolkit-assets/.github/scripts/test_financial_discord_image_layout_contract.py", line 120, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/runner/work/missionchief-toolkit-assets/missionchief-toolkit-assets/.github/scripts/test_financial_discord_image_layout_contract.py", line 115, in main
    subprocess.run(["node", str(harness_path)], cwd=ROOT, check=True)
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['node', '/tmp/mcms-financial-image-xxttvzdk/financial-image-layout-contract.js']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/home/runner/work/missionchief-toolkit-assets/missionchief-toolkit-assets/.github/development-packages/issue-70-source-transform.py", line 173, in <module>
    subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '/home/runner/work/missionchief-toolkit-assets/missionchief-toolkit-assets/.github/scripts/test_financial_discord_image_layout_contract.py']' returned non-zero exit status 1.

```
