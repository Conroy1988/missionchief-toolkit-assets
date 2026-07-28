# Review-branch recovery writer note

`recover-development-package.yml` is an owner-dispatched, package-only review-branch writer. It is recorded in `.github/branch-write-inventory.json`, uses `DEVELOPMENT_PR_TOKEN`, validates exact `main` and pull-request heads, and cannot target public `main`.
