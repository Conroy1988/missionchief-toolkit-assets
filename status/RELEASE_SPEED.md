# Release Speed Control

> Machine-generated release telemetry for Pipeline v4.

## Headline

- **Historical normal-hotfix median:** 32m 13s
- **Pipeline v4 target median:** 4m 00s
- **Expected reduction:** 87.6%
- **Expected throughput:** 8.1×
- **Measured Pipeline v4 median:** 20m 31s

## Statistics

| Metric | v3 baseline | v4 measured | v4 target |
|---|---:|---:|---:|
| PR → verified median | 32m 13s | 20m 31s | 4m 00s |
| PR → verified P90 | 33m 24s | 20m 31s | 7m 00s |
| Merge → verified median | 1m 40s | 58s | 1m 00s |

## Release history

| Version | Pipeline | Class | PR → verified | Merge → GitHub | Merge → verified | Greasy Fork | Backup |
|---|---:|---|---:|---:|---:|---:|---:|
| 8.1.2 | v4 | normal | — | — | — | 11s | 6s |
| 8.1.1 | v4 | normal | — | — | — | 17s | 4s |
| 8.1.0 | v4 | normal | — | — | — | 11s | 5s |
| 8.0.4 | v4 | normal | 20m 31s | 50s | 58s | 8s | 6s |
| 8.0.3 | v3 | normal | 31m 02s | — | 1m 53s | — | — |
| 8.0.2 | v3 | binary-transfer-exception | 213m 16s | — | 1m 25s | — | — |
| 8.0.1 | v3 | normal | 33m 24s | — | 1m 26s | — | — |

The v8.0.2 binary-transfer exception is retained for transparency but excluded from the normal-hotfix baseline. GitHub Pages is asynchronous and does not block userscript delivery.
