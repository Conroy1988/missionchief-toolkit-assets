# Reviewed development-package workflow

The reviewed development-package workflow has two explicit phases. Both commands must be posted by `Conroy1988` on the same GitHub issue and must identify an allowed branch, a Python package under `.github/development-packages/`, and the branch's exact 40-character head SHA.

## 1. Neutral preflight

```text
/preflight-development-package <branch> <package.py> <expected-head-sha>
```

Preflight checks the exact authorized branch commit against the current `main`, runs the package in a disposable Actions workspace, and executes canonical userscript validation, JavaScript syntax validation, and distribution parity validation.

Preflight never commits, pushes, opens a pull request, or changes `main`. Package exceptions, rebase conflicts, and validation stops are reported on the issue as neutral outcomes, so expected diagnostic work does not create a red failure-notification flood.

A successful preflight records a hidden fingerprint containing the branch, package, expected branch SHA, and current `main` SHA. A publish-capable command is accepted only when that exact fingerprint passed preflight.

## 2. Publish-capable application

```text
/apply-development-package <branch> <package.py> <expected-head-sha>
```

The apply phase repeats the same package against the same branch and `main` commits, reruns every mandatory validation, removes the package payload, commits the validated result, pushes with an explicit SHA lease, and opens or updates the pull request.

Genuine publish failures remain red and blocking. A failed package cannot commit, push, create a pull request, or mutate `main` unless all earlier gates completed successfully.

## Notification semantics

- Malformed, missing, stale, duplicate, or superseded commands finish neutrally with a concise issue comment.
- Repeated commands for an already completed fingerprint are skipped.
- Newer commands for the same target branch cancel older in-progress commands.
- Preflight failures are neutral because they are expected diagnostic outcomes.
- Genuine publish failures remain red and include the exact failed stage and Actions run link.
- Each accepted command produces one terminal issue outcome: skipped, preflight passed/stopped, apply succeeded, or apply failed.

## Safety invariants

- Only `feature/`, `fix/`, and `chore/` branches are accepted.
- Packages must remain under `.github/development-packages/` and cannot be symbolic links.
- Every command is locked to an exact branch SHA.
- Apply requires a successful preflight against the current `main` SHA.
- Canonical validation, JavaScript syntax, source/distribution parity, force-with-lease protection, and pull-request review remain mandatory.
