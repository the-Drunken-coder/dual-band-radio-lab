# Electrical and placement review

Reviewed 2026-10-24. No confirmed electrical pinout, assigned-net, socket-orientation, or placement defect found in the inspected snapshot. No design-file repair is justified by these checks. This is not fabrication approval.

## Scope and evidence

Read the actual `boards/dual-radio-carrier/dual-radio-carrier.kicad_sch`, `.kicad_pcb`, `design.json`, `gpio-map.csv`, and `radio-socket-map.csv`. Independently parsed the schematic symbols, wires, labels and no-connect markers, and PCB footprint pads. Compared all 108 schematic pins and 113 PCB pads, including mounting holes and the duplicated U1 output land, against the design data. No mismatches. All 32 radio CSV contacts and 11 GPIO CSV assignments agree. No duplicate label positions or wires touching no-connect markers were found.

Cross-checked the archived manufacturer schematics and dimensional drawings, radio top/underside photos, controller pinout image, TI TLV1117LV datasheet, KEMET capacitor datasheet, and Samtec footprint/catalog/assembly print. All entries in both reference directories' `SHA256SUMS` passed. Reference notes were used for navigation, not as substitutes for the manufacturer files.

## Confirmed static checks

- **Radio mapping:** `extra/references/radio/Core2021-HF-Schematics.pdf`, U2, and `core2021-hf-m-1.jpg` / `core2021-hf-m-3.jpg` establish the top view. Upper contacts are module pins 8 through 1 left to right; lower contacts are 9 through 16. J3/J5 therefore run `3V3,GND,NC,DIO7,DIO8,DIO11,GND,2.4G_ANT`; J4/J6 run `BUSY,RESET,MISO,MOSI,SCK,NSS,GND,LoRa_ANT`. Actual KiCad pad assignments agree. RF pins, NC, DIO7 and DIO8 have no assigned carrier net.
- **Controller orientation:** manufacturer `extra/references/controller-power/sources/controller-schematic.pdf`, header image and dimension drawing agree with the rotated placement. USB faces the carrier top; after the +3 mm X shift, J1/P1 is right at x32, J2/P2 left at x9.14. Pin 1 is y60 and pin 22 is y6.66. Row spacing is 22.86 mm and pitch is 2.54 mm.
- **GPIOs and USB recovery:** assigned GPIOs are 4,5,6,7,9,10,11,12,13,15,16. Controller 3V3 pins J1.1/.2 and EN J1.3 are unconnected. Boot straps, UART43/44, native USB19/20, PSRAM35/36/37, RGB38, reserve48 and JTAG39 through 42 have no carrier load. The onboard CH343P DTR/RTS automatic BOOT/EN circuit remains independent of application firmware at the carrier interface.
- **Power:** J1.21 supplies `USB_5V` to U1.3. The controller schematic places P1.21 downstream of D1 B5819WS. U1.1 is GND; U1.2 and its tab land are `+3V3_RADIO`, matching TI datasheet page 3 and the archived SOT-223 footprint. The radio rail has no assigned-net tie to controller 3V3. C1 is across IN/GND; C2 across OUT/GND; C3/C5 are local 10uF, 25V, X7R parts and C4/C6 local 100nF parts. Both CS and RESET lines have separate 10k pullups to the radio rail. The 33-ohm SCK/MOSI resistors correctly join their host and radio net names.
- **XY fit:** PCB edges are 100 by 75 mm. Radio A module pin 8 is at 45,20; B at 75,48. Both have 17.78 mm contact span and 15.24 mm row separation, matching the vendor drawing. The module envelopes at `[42.39,18,65.4,38]` and `[72.39,46,95.4,66]` include the conflicting vendor body dimensions with margin. They and the shifted controller envelope `[7.86,1.61,33.26,64.91]` remain inside the carrier without mutual overlap. R5/R6 are now at x36; each courtyard is 0.94 mm from the controller envelope. Actual footprint courtyards do not overlap. The controller antenna keepout also moved +3 mm X to `[11.2,53,29.9,74.4]`. Actual PCB placement and all 113 pad assignments were rechecked against the updated design data without mismatches. Screw-head fit remains dependent on the selected hardware; no screw-head diameter was supplied.
- **Socket lands:** J1 through J6 use 1.80 mm copper pads and 1.04 mm drills. Samtec's single-row drawing specifies 1.04 mm holes. Nominal annular ring is 0.38 mm. This establishes the PCB pattern, not physical mating qualification.

## Outstanding holds, not confirmed defects

| Severity/status | Path or part | Required action |
| --- | --- | --- |
| Release hold, already documented | J1.21 and controller D1; `extra/references/controller-power/power-recommendation.md` | Measure the actual laptop/cable allowance, total current, header voltage, radio voltage, D1 and U1 temperatures under the intended simultaneous workload. Manufacturer material does not specify allowable external header load or fitted D1 thermal margin. Retain the bench hold; a separate LDO does not bypass D1. Change the upstream power arrangement only if measurements fail the required voltage/current/temperature limits. |
| Release hold, already documented | SSW-108-01-G-S and SSW-122-01-G-S | Check actual male-post cross-section, exposed length, insertion depth, seating and retention with samples. Samtec specifies 0.635 mm square mating posts and 3.68 to 6.35 mm insertion. Vendor photos and XY drawings do not qualify the supplied male headers as exact mates. Confirm USB plug and button access on the assembled stack. |

## Limits and snapshot

Parent reports the first routed board passed actual-geometry 0.25 mm clearance, continuity of all 16 nets, and schematic/PCB equivalence. Those are parent-reported checks on the earlier placement, not independent results from this review or validation of the subsequent shift/fill changes. The updated PCB contains cached filled polygons for `GND_FRONT`, `GND_BACK`, and `RADIO_3V3_HEAT_SPREAD`. Their presence was inspected; this review does not establish their clearance, connectivity, thermal performance or validity in native KiCad. Re-run the parent's geometry and continuity checks after the placement and fill changes.

PCB routing is being generated concurrently. This review does not assess trace completion, copper shorts/clearances, RF-pad copper isolation after routing/fill, regulator return paths or heat-spreading effectiveness. Assigned-net correctness does not prove routed continuity. Initial testing keeps Wi-Fi/Bluetooth disabled and uses USB as the sole power source, with no external power inputs. This narrows the initial workload but does not establish D1 capacity. Native KiCad ERC/DRC, assembled fit, USB enumeration, flashing, automatic reset, rail transients, thermal behavior and RF performance were not tested. KiCad was unavailable and `kicad-cli` was not run. Backplane KiCad can be installed from Settings.

SHA256 values identify the reviewed files. Recheck static results if placements or pin assignments change.

```text
design.json                       f57ab0beb1ac37d45e7854ed87417cd974d52c9b1a738f340c2d8c2fba39fddb
dual-radio-carrier.kicad_sch       07bef985a39ec78f3d2483284c58a58685464284a3e9440e2507b3baad2031ae
dual-radio-carrier.kicad_pcb       4303fc7c3b4a744f0626a5ca1776a200890e5349af6ef2b0ce67bc014ffc8614
gpio-map.csv                      78c6bf55b4ac61e4b91bb8350d21ae85ac4fd7999a4aee9a551a865138398843
radio-socket-map.csv              89643a7ffddfa2beb1d6a56f3558286c0b7d081a270b403ffdcd4249f36d2bd8
```

Only `extra/reviews/electrical-review.md` was written by this reviewer.
