# Connector-triggered guarded Toolkit release

The existing owner issue-comment command remains supported. Routine releases may also be started without owner interaction by pushing one exact command file to `automation/releases`.

The command commit must:

- be created by `Conroy1988`;
- change only `.github/automation-commands/release-toolkit.json`;
- be a direct child of the exact expected current `main` commit;
- request an exact Toolkit version and existing tracking issue;
- include `confirmation: RELEASE` and a unique nonce.

The workflow then checks out the exact authorized `main` commit, reconfirms that `main` has not moved, rejects an existing release tag, performs fresh canonical validation, verifies JavaScript syntax and distribution parity, runs mandatory release readiness, and invokes the existing guarded production release workflow.

The command contains data only. It cannot select a workflow, branch target, shell command, repository, release implementation or validation bypass. Replay is rejected after the GitHub Release exists.
