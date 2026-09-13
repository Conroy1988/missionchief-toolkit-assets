# Extension source recovery

The `recovered-0.22.3` directory is an exact extraction of the user-approved
0.22.3 release ZIP. It is the readable packaged runtime, not a claim that the
lost compiler, original module sources or test suite have been recovered.

Do not edit this baseline. New extension modules and a reproducible packaging
step must overlay it. The canonical userscript is independent and unchanged.

0.22.3 was submitted to Chrome Web Store with automatic publication enabled.
BUILD.json inside the archive predates submission; its status is historical.


## 0.23.2 Home Response test build

- Row-by-row polygon intersection planning removes the previous boundary-detail rejection while retaining exclusions and minimum spacing.
- Up to 1,000 new buildings per plan; estimates replace the separate spending cap. Native account balance and purchase verification remain active.
- City shortlist complements the existing UK area search. Selected search results still supply the boundary.
- Optional owned-building image source uses the existing verified image copier, with source digest checkpoints and image-only resume after purchase completion.
- Validation: 29 automated tests, including a 24,000-vertex region with 1,000 placements, source/target image validation and purchase recovery; packaged JavaScript syntax checked. Live Orion construction and image copying still require acceptance testing. Not submitted to the Chrome Web Store.

## 0.23.3 water exclusion test build

The former planner tested administrative boundaries only; it had no independent water mask. Bundled GSHHG 2.3.7 full-resolution shoreline and lake data now constrain previews and marker movement, and native pre-construction checks skip water locations in older saved plans. No network lookup is required for the land check. The derived UK mask, reconstruction script, provenance and LGPL notices are in home-response/geodata and land-data.mjs. A small inward shoreline margin excludes uncertain coast-edge placements. Historical map data cannot identify every small waterway or prove road access.

Validation: 32 automated tests pass, including Northern Ireland offshore and Lough Neagh checks, inland control points, regional preview filtering and legacy-plan pre-request rejection. Packaged syntax verified. Phone acceptance testing pending; not submitted to the store.
