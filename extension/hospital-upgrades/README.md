# Hospital upgrades — 1.1.0 test

Independent hospital-level feature in Operations. Does not alter alliance sharing,
tax, medical extensions or Coins. No live game requests were made for this work.
The earlier blocked sharing/tax task is not implemented or resumed by this module.

Targets 1–30 use the UK range observed earlier in the native game: a level-30
hospital exposed no further Expand control. The older public help result describes
level 20 and is not used as an authoritative current cap. Native upgrade discovery
is authoritative for purchase availability; missing or ambiguous actions pause.
If game rules change, update the target range after verification.

Uses existing Expansion Planner discovery and purchase validation, filters to
owned type-4 buildings, permits only the native immediate Credit level action,
and freshly verifies the resulting level. Reuses native price checks. Estimates
multiply the currently offered per-level price by remaining levels; this estimate
is also the confirmed spending ceiling, not a promise that later prices are fixed.
Higher prices pause. Completed/above-target hospitals are skipped.

Account-scoped site-local checkpoints are saved before each request. An uncertain
purchase can recover only after the expected next level is observed. Unchanged
or unexpected state remains paused without repeating a purchase. A browser Web
Lock serializes all hospital tool work across tabs. Existing administration busy
checks prevent conflicting Operations runs. Unsupported locks block this tool.

Build: `python3 extension/build-hospital-test.py`
Tests: `node --test extension/hospital-upgrades/*.test.mjs extension/home-response/*.test.mjs`

72 automated checks pass, including the panel/preview/confirmation flow and queue
failure paths. Live hospital purchase acceptance remains untested. No Chrome Store
submission was changed. The recovered baseline and stable 1.0.0 ZIP are preserved.

## 1.1.1 — Credit balance correction

Hospital purchases now read `credits_user_current`, matching the existing native
account adapter, instead of the nonexistent `credits` field. Numeric and numeric-string
balances are accepted; absent or invalid balances report a read error, not insufficient
funds. Confirmations show the account balance separately from the authorised plan limit.
74 automated checks pass. No live account actions or store submission changes.

## 1.1.2
Native target-level Credit action replaces intermediate purchases. Preview shares one owned catalogue; hospitals at target skip page discovery. Purchase-time revalidation remains fresh. Old uncertain single-level intents retain their original expected result. New target intents verify the exact destination. No live purchases performed during validation.

## 1.1.3
Post-purchase target verification reads the authoritative hospital record and checks ownership and exact target level. It does not reopen an expansion page that may redirect at maximum level. Read failures retain their underlying cause and saved intents remain resumable without replay. Status text has explicit light foreground. 82 automated checks pass, including the packaged purchase function with an unavailable post-upgrade page, failed record read, wrong level and ownership change. Live account result remains unverified.
