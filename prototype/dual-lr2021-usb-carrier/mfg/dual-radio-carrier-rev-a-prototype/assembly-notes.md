# Dual-radio carrier, revision A

100 × 75 mm, two copper layers, 1.6 mm PCB. One design supports two identical test nodes. Each carrier takes one USB-C controller and two interchangeable LR2021 radio modules.

## Included

- `dual-radio-carrier.kicad_pro`: canonical KiCad project.
- `dual-radio-carrier.kicad_sch`: schematic with each socket contact and its signal labeled.
- `dual-radio-carrier.kicad_pcb`: routed PCB with ground zones and regulator heat-spreading copper.
- `dual-radio-carrier.kicad_sym`, `dual-radio-carrier.pretty/`, and library tables: local symbols and footprints.
- `bom.csv`: components for one carrier, including the three plug-in modules. Double quantities for two nodes. Antennas and USB cables depend on the intended test configuration and are not included.
- `gpio-map.csv`, `radio-socket-map.csv`: firmware and socket mappings.
- `build/carrier-top.png`: inspection image generated from the saved PCB.
- `build/verification.json`: current file-based check results and CAD file hashes.
- `build/native-summary.json`, `build/native-erc.json`, `build/native-drc.json`: native KiCad results for the exact saved files.
- `design.json`, `tools/`: reproducible design inputs, generator, routing, copper fill, rendering, and verification.

## Assembly orientation

All sockets and components fit on the front side.

| Carrier references | Part | Orientation |
| --- | --- | --- |
| J1 and J2 | Two Samtec SSW-122-01-G-S female strips | J1 is vendor P1 at the right. J2 is vendor P2 at the left. Socket pin 1 is at the lower, antenna end. |
| Controller | Waveshare ESP32-S3-DEV-KIT-N8R8-M, SKU 24243 | Components up, USB-C toward the carrier's top edge and USB-C label. |
| J3 and J4 | Two Samtec SSW-108-01-G-S female strips | Radio A upper and lower rows. Carrier pad 1 is left in each row. |
| J5 and J6 | Two Samtec SSW-108-01-G-S female strips | Radio B upper and lower rows. Carrier pad 1 is left in each row. |
| Both radios | Waveshare Core2021-HF-M, SKU 34523 | Shield up, shield text upright, IPEX4 antenna connectors at the right. |
| U1 | TI TLV1117LV33DCYR | Pin 1 GND, pin 2 OUT, pin 3 IN. Large tab is OUT. |

The upper radio row maps to module pins 8 through 1 from left to right. The lower row maps to module pins 9 through 16. The manufacturer's pinout photo is an underside view; follow this top-view assembly map. Unkeyed headers can be inserted backward or offset, so check alignment before powering.

Samtec specifies 1.04 mm finished holes and 0.635 mm square mating posts. The 2.54 mm pitch and row spacing are verified from vendor drawings. Waveshare does not fully specify the supplied male posts, so sample-check insertion depth, seating and retention before committing to these exact sockets. Use mounting hardware with clearance from the sockets; the four carrier holes are 3.2 mm non-plated.

## Power and test access

USB-C on the controller is the only power input. Controller P1.21 supplies U1 through the controller's existing D1 diode. The carrier radio rail is 3.3 V and remains separate from the controller regulator output. There is no battery input or radio power switch. Firmware can reset each radio independently; a USB hardware reset restarts the controller. A full power cycle requires removing USB power.

| Test point | Signal |
| --- | --- |
| TP1 | USB-derived supply, downstream of controller D1 |
| TP2 | Radio 3.3 V |
| TP3 | GND |
| TP4 | Radio A DIO11 interrupt |
| TP5 | Radio B DIO11 interrupt |

The radio supply has a 300 mA design allowance. This is an allowance, not a guaranteed measured maximum. The complete USB budget includes the controller, bridge, hub, LEDs, and radios. Waveshare does not specify permissible external current at P1.21. Check the actual laptop, cable, D1 temperature, U1 temperature and both rails under the intended maximum workload. A regulator's 1 A rating does not establish the USB or controller diode rating.

Keep Wi-Fi and Bluetooth disabled during initial radio tests. Do not connect another supply to either 3.3 V rail. Use the module's antenna jacks. Radio RF header contacts remain isolated, with no carrier RF traces.

## Firmware connections

The radios share SCK GPIO12, MOSI GPIO11 and MISO GPIO13. SCK and MOSI have 33 ohm source resistors. Each radio has separate CS, DIO11 interrupt, BUSY, and reset pins. The four CS/reset lines each have a 10k pullup to the radio rail.

| Radio | CS | DIO11 interrupt | BUSY | RESET |
| --- | ---: | ---: | ---: | ---: |
| A | 10 | 4 | 5 | 6 |
| B | 9 | 7 | 15 | 16 |

Set both CS outputs high before SPI activity. Reset and initialize both radios after every controller boot. Wait for the selected radio's BUSY to go low, and serialize SPI transactions so only one CS is active. Start at 2 MHz SPI during bring-up before validating higher rates. DIO11 names the radio's interrupt pin; it is not ESP32 GPIO11.

Use the controller's CH343 serial interface for command-line flashing and automatic BOOT/reset. Preserve UART43/44, USB19/20, boot straps, internal PSRAM pins, and the onboard RGB pin. They have no carrier loads in this design. The test firmware and laptop CLI remain a separate implementation task.

## Rebuild and check

Run from the project root. Python dependencies are isolated by `uv`. The native check requires the installed `kicad-cli`.

```sh
uv run --with sexpdata --with shapely python boards/dual-radio-carrier/tools/generate.py --placement-only
uv run --with numpy --with shapely --with sexpdata python boards/dual-radio-carrier/tools/route.py
uv run --with shapely --with sexpdata python boards/dual-radio-carrier/tools/copper.py
python3 boards/dual-radio-carrier/tools/native_check.py
uv run --with kiutils --with shapely --with sexpdata python boards/dual-radio-carrier/tools/verify.py
uv run --with pillow --with shapely --with sexpdata python boards/dual-radio-carrier/tools/render.py
```

Generation writes the canonical files named by the root `.backplane.json`. Before a changed PCB replaces the canonical file, its previous contents are backed up under `build/backups/`. Running `generate.py` without `--placement-only` reuses `build/routes.json`; reroute after changing component placements or nets. Regeneration replaces manual PCB edits, so preserve edits in the generator or save a separate backup first.

The checker reads the saved PCB and schematic. It verifies all 16 routed nets, schematic-to-PCB pin agreement, copper clearance including cached zone fills, drill/annular limits, board-edge and mounting-hole gaps, and the antenna keepout. An independent review checked pinouts, orientations, assigned nets, power wiring, and documented vendor dimensions against archived manufacturer evidence.

Native KiCad 10.99.0 ERC, zone refill and DRC now pass with all severities enabled: zero electrical violations, zero DRC violations, zero unconnected items and zero schematic/PCB parity issues. The final native refill replaces the fallback copper cache and saves the canonical board. The separate geometry checker also checks the saved native board. Touching a keepout boundary is permitted; copper entering its interior is rejected.

Native checks identified and prompted fixes for two adjacent via holes, a starved ground thermal, small/overlapping silkscreen labels, a missing mounting-hole library footprint, local-net naming, intentional no-connect net names, and part-number/datasheet field parity. The generation scripts include those fixes. J3 ground contact 2 uses a solid pour connection to avoid the isolated thermal spokes; the other socket contacts retain their normal zone settings.

These CAD checks do not establish USB compliance, thermal behavior, RF performance or physical mating fit. Check the selected sockets against actual module samples. Validate the power path, USB flashing/reset and radio operation on the first assembled units. The prototype fabrication export preserves these remaining limits.

Manufacturer evidence and source hashes are under `extra/references/`. The independent static review is `extra/reviews/electrical-review.md`; its historical KiCad-unavailable statement predates the native checks. No physical boards have been manufactured.

After the native checks pass on the current files, generate the prototype package with:

```sh
python3 boards/dual-radio-carrier/tools/export_prototype.py
```

This writes Gerbers, separate PTH/NPTH drill files, a BOM, placement data, source hashes, and a prototype-status note into `mfg/dual-radio-carrier-rev-a-prototype/` and a ZIP beside it. It does not order or submit anything.
