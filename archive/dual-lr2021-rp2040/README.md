# Historical RP2040 dual-LR2021 carrier

This is the **100 × 70 mm, four-layer RP2040-Plus-M** carrier, preserved for design history. It is not the [100 × 75 mm, two-layer ESP32-S3 carrier](../../prototype/dual-lr2021-usb-carrier/README.md), and its parts, sockets, pin map and reports are not interchangeable with that design.

[Download the original review package](Dual_LR2021_Carrier_RevA_REVIEW_PACKAGE.zip).

## Provenance

The ZIP is the unchanged `original_archive/Dual_LR2021_Carrier_RevA_REVIEW_PACKAGE.zip` member recovered from `Dual_LR2021_AI_AGENT_HANDOFF.zip`. It is 1,006,372 bytes with SHA-256:

```text
fd3cf81a0f237c9d0dd5d47b819551a4084b31651b4e19fbfb4382be8c0431d4
```

[provenance.json](provenance.json) records the outer handoff hash and the inventory of every contained file. Archive CRC and the original embedded SHA-256 manifest were checked during recovery. Those integrity checks are not CAD, electrical or manufacturing validation.

The package contains editable KiCad files, local symbols and footprints, the model/generators, source requirements, assembly BOM and placements, drawings, Gerber/drill outputs, a firmware pin map and verification/release-gate notes. There is no implemented radio application firmware.

## Engineering status retained from the source

The board uses two Core2021-HF-M modules, an RP2040-Plus-M controller, separate SPI buses and two load-switched radio supplies. It takes 3.3 V from the controller; its available current, USB policy, regulator revision and thermal margin remain unresolved.

The original custom geometry and export-readback checks passed against generated data. Native KiCad import/ERC/DRC, independent radio socket mapping, mating dimensions, physical power/thermal tests, firmware bring-up and RF coexistence were still open. Do not transfer the ESP32 design's saved KiCad results to this archive.

All fabrication outputs are **unreleased historical review files**. The archived RFQ and manufacturing instructions do not authorize ordering or supplier contact. The outer handoff's website/cart instructions and personal operator guidance were intentionally not copied into this repository. The engineering package is retained intact, including its original limitations.

For current project direction and all three hardware snapshots, use [project context](../../docs/project-context.md).
