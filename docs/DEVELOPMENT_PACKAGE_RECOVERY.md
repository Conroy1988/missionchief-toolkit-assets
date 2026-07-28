# Reviewed development-package recovery

The normal two-stage `issue_comment` development-package workflow remains the primary path.

When GitHub does not deliver its owner comment event, the owner may manually dispatch **Recover Reviewed Development Package** with the number of an existing pull request. The recovery lane is deliberately narrower than the normal path:

- the pull request must be open, owned by `Conroy1988`, hosted in this repository and target `main`;
- the head branch must use the reviewed `feature/`, `fix/` or `chore/` namespaces;
- the pull request must contain exactly one changed file under `.github/development-packages/`;
- the exact pull-request head and current `main` head are captured and revalidated before execution;
- the package is rebased onto that exact `main`, applied once and removed;
- canonical userscript validation, JavaScript syntax and distribution parity must pass before publication;
- publication uses `DEVELOPMENT_PR_TOKEN` and an exact force-with-lease against the captured pull-request head;
- the workflow cannot push to public `main` and cannot create a branch, issue or pull request.

This is a manually owner-dispatched recovery transport, not an alternate validation standard. A resulting product candidate must still pass the normal pull-request Hotfix Gate before merge and the normal guarded release process before publication.
