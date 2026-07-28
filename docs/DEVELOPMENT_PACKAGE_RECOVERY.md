# Reviewed development-package recovery

The normal two-stage `issue_comment` development-package workflow remains supported.

When GitHub does not deliver its owner comment event, **Recover Reviewed Development Package** accepts either:

- an owner `workflow_dispatch`; or
- a connector-authenticated push that changes only `.github/automation-commands/recover-development-package.json` on `automation/development-packages`.

The push command must identify the pull request, exact current `main` SHA, exact package pull-request head SHA and a unique nonce. The recovery lane remains deliberately narrow:

- the command actor must be `Conroy1988`;
- a push command commit may change only the exact command file;
- the pull request must be open, owned by `Conroy1988`, hosted in this repository and target `main`;
- the head branch must use the reviewed `feature/`, `fix/` or `chore/` namespaces;
- the pull request must contain exactly one changed file under `.github/development-packages/`;
- the exact pull-request head and current `main` head are captured and revalidated before execution;
- the package is rebased onto that exact `main`, applied once and removed;
- canonical userscript validation, JavaScript syntax and distribution parity must pass before publication;
- publication uses `DEVELOPMENT_PR_TOKEN` and an exact force-with-lease against the captured pull-request head;
- the workflow cannot push to public `main` and cannot create a branch, issue or pull request.

This is a connector-triggerable recovery transport, not an alternate validation standard. A resulting product candidate must still pass the normal pull-request Hotfix Gate before merge. Release-candidate pull requests continue through the existing automatic post-merge guarded release pipeline.
