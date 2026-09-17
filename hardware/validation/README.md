# Schematic verification

KiCad 10.0.6, 2026-09-17. All four PDF exports, XML netlist exports and unfiltered ERC commands returned exit code 0.

| Project | ERC errors | ERC warnings | Exclusions |
| --- | ---: | ---: | ---: |
| Carrier | 0 | 0 | 0 |
| E22 | 0 | 0 | 0 |
| Core2021 | 0 | 0 | 0 |
| E28 | 0 | 0 | 0 |

The carrier's former GND/VSYS errors and isolated VSYS-label warning disappeared after implementing the physical supply. See DESIGN_REVIEW.md. Raw `erc.json` files preserve the actual default ignored classes. No severity overrides or ERC exclusions were introduced.

`connectivity-check.json` checks exported nets, not generator dictionaries: radio pad numbers, GPIO/socket mappings, eight spare GPIOs including all three ADC-capable pins, expander control connections, translator direction and supply domains, Q1 orientation and source isolation, slot power pins and NCs. Mechanical arithmetic verifies offset/reversal rejection and post lead distance for the specified interface, not a nonexistent PCB. `footprint-geometry.json` was extracted by KiCad's native footprint loader; FOOTPRINT_REVIEW.md compares the geometry to source drawings.

Reproduce from the repository root:

```sh
python3 hardware/tools/build_footprints.py
python3 hardware/tools/build_studies.py
python3 hardware/tools/validate_schematics.py
python3 hardware/tools/check_studies.py
```

The validation script currently uses this host's installed KiCad path. No PCB command runs. DRC, power measurements, physical fit, RF testing and manufacturing-preview checks have not been performed. PDF/fontconfig diagnostic messages, if any, are retained in per-project logs and are distinct from schematic ERC.

## Source-series connectivity checks

The updated checks verify carrier U5 SCK/MOSI and MCP23S17 SO source segments, and MISO source segments on all three card designs. Exact net membership must put the 22-ohm resistor between each source and its shared bus. Core's logical module and real socket are checked together. The checks also compare native XML component values/footprints and BOM initial/alternate population metadata. The E28 design is used twice, yielding five MISO source resistors and two clock/data resistors in the complete system. ERC and netlists were regenerated after adding these parts. Physical placement, oscilloscope measurements and IBIS analysis have not been performed.
