# Toolkit 8.2.0 full production-health audit

- **Status:** `passed-with-warnings`
- **Source SHA-256:** `865598afd3546b8a5604a223408f1618f59b11c460a0858ac9e2c45b906df91a`
- **Source:** 1,658,510 bytes · 25,335 lines
- **Managed recurring intervals:** 2
- **Managed timeouts:** 82
- **Mutation observers:** 10
- **Resize observers:** 0
- **Listener additions/removals:** 44 / 12
- **Network request sites:** 5

## Errors

- None.

## Warnings

- Raw event-listener additions materially exceed visible removals and managed ownership.

## Resource inventory

```json
{
  "abortControllerConstructions": 1,
  "audioConstructions": 0,
  "cssTemplateBytes": 2333,
  "eventListenerAdds": 44,
  "eventListenerRemoves": 12,
  "managedAnimationFrames": 11,
  "managedIntervals": 2,
  "managedListeners": 0,
  "managedObserverTracks": 14,
  "managedTimeouts": 82,
  "mutationObserverConstructions": 10,
  "networkRequestSites": 5,
  "objectUrlCreates": 0,
  "objectUrlRevokes": 1,
  "rawAnimationFrameCalls": 1,
  "rawSetIntervalCalls": 1,
  "rawSetTimeoutCalls": 3,
  "resizeObserverConstructions": 0,
  "sourceByteHeadroom": 1341490,
  "sourceBytes": 1658510,
  "sourceLineHeadroom": 38665,
  "sourceLines": 25335
}
```
