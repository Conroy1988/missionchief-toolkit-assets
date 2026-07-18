# Issue #162 — Mission Report Label Handling

## Objective

Ensure every report created by the Toolkit's Report Mission button receives the `Mission Info Missing` label, including reports submitted by contributors.

## Required behaviour

- Report Mission opens `.github/ISSUE_TEMPLATE/mission-info-missing.yml`.
- The issue URL selects that form and prefills the sanitised report into the `diagnostic` field.
- The form assigns `Mission Info Missing` through its repository configuration.
- The userscript stores no GitHub credential.
- Existing report redaction and URL-length limits remain unchanged.

## Validation

The v4.15.5 candidate must pass Mission Requirements runtime fixtures, issue-form structure checks, report URL assertions, sanitisation tests, JavaScript syntax validation, canonical source validation, distribution parity, code-integrity, performance, documentation and full userscript audits.
