# Release Planning Workflow

`Prepare Release Plan` is a read-only operator aid. It never creates a tag, GitHub Release, Greasy Fork update, private backup or Discord announcement.

## Inputs

- **Release level:** automatic, patch, minor or major
- **Proposed version:** optional exact semantic version
- **Since:** optional ISO-8601 lower bound for merged pull requests

## Output

The workflow produces a Markdown operator brief and machine-readable JSON containing:

- current, recommended and proposed versions;
- merged pull requests since the current release;
- categorised draft release notes;
- changelog-section readiness;
- canonical and distribution SHA-256 values;
- a final operator-gate checklist.

## Recommended operation

1. Run the planner before editing the final changelog.
2. Review the suggested semantic version and categorisation.
3. Update the canonical changelog and any user-facing documentation.
4. Run Release Readiness Check.
5. Confirm the exact source hash, distribution targets and release notes.
6. Publish only through `Release Toolkit`.

The planner is advisory. Release Readiness and the production release workflow remain authoritative.
