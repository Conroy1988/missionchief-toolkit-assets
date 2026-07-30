# Issue #595 — Discord Finance Report Complexity

## Outcome

Finance → Discord Reporting has three audience contracts:

| Complexity | Audience | Discord delivery |
|---|---|---|
| **Simple** | Anyone who needs the result immediately | One embed with period, money in, money out, net change, balances, activity and a plain data check |
| **Informative** | Players who want useful context without an audit dump | One embed adding running costs, investment, result before investment, leading categories, comparison and important alerts |
| **The Wolf** | Finance enthusiasts and operators | Two embeds retaining scorecard, risk, forecast, drawdown, classifications, highest payouts and archive/audit evidence |

The default for a new installation is **Informative**.

## Shared information hierarchy

Every complexity presents these facts first:

1. reporting period;
2. money in;
3. money out;
4. net balance change;
5. opening and closing balance;
6. the result in plain English.

Green, red and amber represent positive, negative and unchanged net movement respectively.

## Saved-state migration

The previous `reportMode` values remain readable during state normalisation:

| Previous value | New complexity |
|---|---|
| `executive` | `informative` |
| `fullAudit` | `wolf` |
| missing or invalid | `informative` |

An explicit valid `complexity` value always wins. The retired `reportMode` property is removed from the normalised state.

## Settings behaviour

- Simple hides breakdown, comparison, alert and forecast controls.
- Informative exposes breakdown, comparison and important-alert controls.
- The Wolf also exposes forecast intelligence.
- Chart attachment remains independently selectable for every complexity.
- The action remains one manual **Generate & Post Report** button.

## Graphic contract

The 1200 × 675 PNG uses the same first-line hierarchy at every level:

- Money In
- Money Out
- Net Change
- Closing Balance

The badge shows **AHEAD**, **BEHIND** or **EVEN** for Simple and Informative. The Wolf retains the financial grade and score. The supporting snapshot changes by complexity, while the net-movement chart and period remain consistent.

## Privacy and delivery

- The webhook remains in Tampermonkey storage.
- Discord delivery continues to use `wait=true`.
- Mentions remain disabled.
- Webhook content never enters the payload, image or tests.
- Attachment rejection continues to fall back to the text-only payload.

## Executable evidence

- `.github/scripts/test_financial_discord_complexity_contract.py`
- `.github/fixtures/financial-discord-complexity-contract.json`
- `.github/scripts/test_financial_discord_image_layout_contract.py`
- `.github/fixtures/financial-discord-image-layout-contract.json`

These contracts exercise legacy migration, each payload shape, embed and field limits, attachment ownership, result colours, privacy boundaries and non-overlapping image snapshot rows.
