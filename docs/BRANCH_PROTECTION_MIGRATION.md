# Branch Protection Migration Plan

The repository currently permits controlled automation commits to `main` because release validation, dashboard reconciliation, Greasy Fork tracking and recovery workflows update verified state directly.

## Current safe controls

- deletion protection;
- force-push protection;
- reviewed pull requests for normal development;
- code-integrity, performance, asset, recovery and documentation validation;
- immutable GitHub Action pins and permission auditing.

## Why strict PR-only enforcement is deferred

A strict requirement that every `main` update arrive through a pull request would block the current release architecture unless automation is moved to a bypass-capable GitHub App identity or generated state is stored outside the protected branch.

## Migration stages

1. Inventory every workflow that writes to `main`.
2. Separate immutable release source from generated operational state.
3. Move dashboard, announcement and tracker state to a dedicated state branch, release asset or external store.
4. Give production release automation a narrowly scoped GitHub App identity.
5. Require pull requests, required checks and resolved conversations for human changes.
6. Verify normal release, Greasy Fork retry, private-backup retry, Discord retry and rollback preparation under the new identity.
7. Enable strict protection only after a full non-production rehearsal.

## Exit criteria

Strict protection is ready when no workflow depends on unrestricted human-token pushes to `main`, every bypass actor is explicit and auditable, recovery procedures still work, and a failed publication stage cannot leave release state split across systems.
