# Repository and dependency audit — legacy snapshot

> This committed report is retained only as historical migration evidence. It is **not** the current repository audit.

The last committed snapshot described Toolkit **v4.13.1** and was generated before the repository audit became read-only, artifact-only evidence.

## Current authority

Current repository audits are produced by:

```text
.github/workflows/repository-audit.yml
```

Each run:

- checks out `main` without write credentials;
- audits repository files, workflows, public raw paths, Greasy Fork references and duplicate media;
- writes `repository-audit.json` and `repository-audit.md` under `repository-audit-output/`;
- uploads the reports as the immutable `missionchief-repository-audit-<commit>` Actions artifact for 90 days;
- does **not** change public `main` or `status/release-dashboard.json`.

Use the latest successful **Repository and Dependency Audit** workflow artifact for current evidence.
