# Issue #260 final-wrapper diagnostic

- Return code: `1`

## Standard output

```text
Mission requirements runtime fixtures passed
Mission requirements runtime fixtures passed
Custom Vehicle Badges runtime fixtures passed
Custom Vehicle Badges contract passed
LSSM compatibility audit passed against 4f731e1d6d009cbf2129530fb31d10177b21a52a

```

## Standard error

```text
Traceback (most recent call last):
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/scripts/test_mission_requirements_contract.py", line 236, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/scripts/test_mission_requirements_contract.py", line 171, in main
    assert entry["aliases"] and entry["types"]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
Traceback (most recent call last):
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/development-packages/fix-issue-260-v4.20.14-final.py", line 21, in <module>
    runpy.run_path(str(PACKAGE), run_name="__main__")
  File "<frozen runpy>", line 286, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 223, in <module>
    main()
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 219, in main
    run_checks()
  File "/tmp/issue-260-wrapper-6sbtnll8/repo/.github/development-packages/fix-issue-260-v4.20.14.py", line 206, in run_checks
    subprocess.run(command, cwd=ROOT, check=True)
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['python3', '/tmp/issue-260-wrapper-6sbtnll8/repo/.github/scripts/test_mission_requirements_contract.py']' returned non-zero exit status 1.

```
