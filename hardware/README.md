# Rev A hardware review package

**Four routed PCBs and four schematics are ready for review. DRC/ERC: zero findings. Manufacturing release remains on hold.**

The 250 x 210 mm carrier and three 84 x 80 mm daughtercard designs use two layers with 2 oz copper per side. The E28 design is installed twice. Radio slots are spread apart, test points remain accessible with all cards installed, and switcher loops stay local.

Start with [DESIGN_REVIEW.md](DESIGN_REVIEW.md), the [assembled 3D view](renders/rev-a-assembled-3d.png) and the [combined schematic PDF](Rev-A-electrical-studies.pdf).

| Native layout | 3D review |
| --- | --- |
| [Carrier](carrier-rev-a/carrier-rev-a.kicad_pcb) | [Carrier render](renders/carrier-rev-a-3d.png) |
| [E22](adapters/e22-900m30s-rev-a/e22-900m30s-rev-a.kicad_pcb) | [E22 render](renders/e22-900m30s-rev-a-3d.png) |
| [Core2021](adapters/core2021-hf-m-rev-a/core2021-hf-m-rev-a.kicad_pcb) | [Core render](renders/core2021-hf-m-rev-a-3d.png) |
| [E28, used twice](adapters/e28-2g4m27s-rev-a/e28-2g4m27s-rev-a.kicad_pcb) | [E28 render](renders/e28-2g4m27s-rev-a-3d.png) |

[GPIO_MAP.md](GPIO_MAP.md), [POWER_BUDGET.md](POWER_BUDGET.md), [radio-slot-v0.1.md](radio-slot-v0.1.md), [FOOTPRINT_REVIEW.md](FOOTPRINT_REVIEW.md), [ASSEMBLY_NOTES.md](ASSEMBLY_NOTES.md) and [LAYOUT_REQUIREMENTS.md](LAYOUT_REQUIREMENTS.md) define the review constraints. The carrier uses 18 GPIOs, leaves eight spare and isolates the radio supply from USB-only operation. GP26–28 remain NC. Source resistors start at 22 ohms, with 0-ohm options and later oscilloscope/IBIS verification.

Each project includes editable KiCad files, selected BOM, connectivity data and schematic PDF. `validation/` contains raw DRC/ERC, netlists and independent geometry/power/connectivity measurements. `renders/` contains non-manufacturing review images. `sources/` records manufacturer evidence. Custom 3D models are dimensioned envelopes, not physical fit certification.

**The final native PCB files are authoritative.** Placement generators and intermediate `layout/` DSN/SES files predate manual routing corrections; do not regenerate/import them over the final boards. See [validation/README.md](validation/README.md) for read-only checks.

No Gerbers, drill files, CPL, ordering archive, quotation or order has been generated. Factory acceptance of the E28 IPEX variant, human layout review, physical fit and electrical/thermal/RF qualification remain separate release gates. Existing prototype work is unchanged.
