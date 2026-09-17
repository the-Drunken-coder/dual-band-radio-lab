# Rev A schematic package

**Schematic review complete; stopped before PCB layout. No fabrication release.**

Four native KiCad projects cover the Pico 2 carrier, E22 915 MHz LoRa card, Core2021-HF-M socket adapter and common E28 2.4 GHz card, used twice. All four pass ERC with zero errors/warnings. The carrier uses 18 GPIOs, leaves eight spare and has a protected 5 V / 4 A external supply target with USB-isolated radio power.

Rev A favors a larger, easy-to-debug board: spread-out radio slots, generous 5-V copper, accessible test points and compact local switcher loops. [LAYOUT_REQUIREMENTS.md](LAYOUT_REQUIREMENTS.md) makes these constraints explicit for the next phase. Layout remains on hold.

Start with [DESIGN_REVIEW.md](DESIGN_REVIEW.md) and the [combined schematic PDF](Rev-A-electrical-studies.pdf). [GPIO_MAP.md](GPIO_MAP.md), [POWER_BUDGET.md](POWER_BUDGET.md), [radio-slot-v0.1.md](radio-slot-v0.1.md), [FOOTPRINT_REVIEW.md](FOOTPRINT_REVIEW.md) and [ASSEMBLY_NOTES.md](ASSEMBLY_NOTES.md) document the implemented choices and acceptance requirements. E28 IPEX configuration requires factory acceptance before procurement; no user rework is permitted.

Each project directory contains its editable `.kicad_pro` / `.kicad_sch`, selected BOM, connectivity data and PDF. `libraries/` contains project-local symbols and ten reviewed footprint patterns. `validation/` contains raw ERC reports, exported netlists and independent checks. `sources/` records manufacturer evidence and the exact JLC module photographs.

`tools/build_studies.py` and `tools/build_footprints.py` are deterministic generators. Do not rerun after manual KiCad changes without reconciling them. `tools/validate_schematics.py` runs only schematic exports/ERC; `tools/check_studies.py` checks their exported connectivity. Nothing invokes PCB creation or fabrication export.

Configurable source-series resistors are included on buffered SCK/MOSI and every independent MISO source, including the expander. Initial population is 22 ohms with a 0-ohm option; values require oscilloscope/IBIS verification during bring-up. See DESIGN_REVIEW.md.

No files are ready for ordering. Later PCB layout, thermal/fit testing, factory process acceptance and manufacturing release are separate work. Existing prototype work is unchanged.
