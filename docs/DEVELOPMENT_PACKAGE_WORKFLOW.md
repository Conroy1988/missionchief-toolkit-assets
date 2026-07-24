# Reviewed development-package workflow

The reviewed development-package workflow operates only inside an **existing open pull request** owned by `Conroy1988`, hosted in this repository, and targeting `main`.

The development branch and pull request must be created directly before either command is used. The workflow never creates an issue, branch, or pull request. This prevents diagnostic issue proliferation, duplicate pull requests, and GitHub Actions runs becoming stuck behind maintainer approval because they were created by `github-actions[bot]`.

Both commands must be posted by `Conroy1988` on the same pull request and must identify:

- the pull request's exact head branch;
- a Python package under `.github/development-packages/`;
- the branch's exact 40-character head SHA.

The workflow rejects closed or merged pull requests, fork pull requests, branches that do not match the pull request head, pull requests not targeting `main`, and pull requests not owned by `Conroy1988`.

## 1. Neutral preflight

```text
/preflight-development-package <branch> <package.py> <expected-head-sha>
```

Preflight checks the exact authorized pull-request commit against the current `main`, runs the package in a disposable Actions workspace, and executes canonical userscript validation, JavaScript syntax validation, and distribution parity validation.

Preflight never commits, pushes, creates repository records, or changes `main`. Package exceptions, rebase conflicts, and validation stops are reported on the existing pull request as neutral outcomes, so expected diagnostic work does not create a red failure-notification flood.

A successful preflight records a hidden fingerprint containing the branch, package, expected branch SHA, and current `main` SHA. A publish-capable command is accepted only when that exact fingerprint passed preflight.

## 2. Publish-capable application

```text
/apply-development-package <branch> <package.py> <expected-head-sha>
```

The apply phase repeats the same package against the same pull-request and `main` commits, reruns every mandatory validation, removes the package payload, commits the validated result, and pushes it back to the **existing pull request only** with an explicit SHA lease.

Apply requires the repository secret `DEVELOPMENT_PR_TOKEN`. The token is used for an owner-authenticated checkout and push, and commits are authored as `Conroy1988`. The workflow does not fall back to `github.token` for branch publication and does not author product commits as `github-actions[bot]`.

Genuine publish failures remain red and blocking. A failed package cannot commit or push unless every earlier gate completed successfully.

## Notification semantics

- All responses are posted to the existing pull request conversation.
- Malformed, missing, stale, duplicate, superseded, or mismatched commands finish neutrally with a concise pull-request comment.
- Repeated commands for an already completed fingerprint are skipped.
- Newer commands for the same pull request cancel older in-progress commands.
- Preflight failures are neutral because they are expected diagnostic outcomes.
- Genuine publish failures remain red and include the exact failed stage and Actions run link.
- Each accepted command produces one terminal pull-request outcome: skipped, preflight passed/stopped, apply succeeded, or apply failed.

## Safety invariants

- Commands are accepted only on an existing open same-repository pull request owned by `Conroy1988` and targeting `main`.
- Only `feature/`, `fix/`, and `chore/` branches are accepted.
- The command branch must exactly match the pull request's head branch.
- Fork pull requests are rejected.
- Packages must remain under `.github/development-packages/` and cannot be symbolic links.
- Every command is locked to an exact pull-request head SHA.
- Apply requires a successful preflight against the current `main` SHA.
- Apply requires `DEVELOPMENT_PR_TOKEN`; no GitHub Actions token fallback is allowed for branch writes.
- The workflow never creates an issue, branch, or pull request.
- Canonical validation, JavaScript syntax, source/distribution parity, force-with-lease protection, and pull-request review remain mandatory.
