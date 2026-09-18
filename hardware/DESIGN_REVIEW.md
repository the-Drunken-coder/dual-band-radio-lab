# Rev A schematic and PCB review

2026-09-17. **Four routed native PCBs pass KiCad 10.0.6 DRC with zero findings, zero unconnected items and zero schematic-parity findings. All four schematics also pass ERC with zero errors/warnings.** Stopped for board review. No Gerbers, drills, placement/order packages or orders were produced. One E28 design is instantiated twice.

| Requested blocker | Implemented disposition |
| --- | --- |
| Pico GPIO headroom | 18/26 used, eight spare. SPI/CS/BUSY/IRQ remain direct through fixed-direction isolation. MCP23S17 handles reset and pre-command PA/LNA state. See GPIO_MAP.md for the explicit restriction on autonomous RF state changes |
| USB/external power separation | TPS259470L protected external radio bus; DMG2305UX P-channel ORing matches Pico figure 9. USB powers Pico but not the radio supply. Onboard Pico D1 prevents USB backfeed |
| ADC GPIO back-power | GP26-28 are NC at the Pico and physical sockets. U5-U7 additionally isolate the used digital interface across independent supplies |
| At least 5 V / 4 A | 12 A input connector, 4.66 A nominal electronic-fuse limit, controlled ramp, 4 A copper/plane constraints. Conservative 3.225 A continuous allocation and 3.865 A inrush stress case |
| Carrier ERC errors and warning | Real power input, ground source and VSYS ORing now exist. The old isolated VSYS label is part of the completed supply. No excluded findings |
| Mechanical anti-misinsertion | Retained ordinary 1x10 + 1x8 headers and added a mandatory captive asymmetric M3 x 25 alignment post. Calculated >=5.35 mm lead before electrical engagement, plus defined solid capture regions. Blocks one-pitch offset and reversal during straight insertion |
| E28 antenna network | Current manual section 9.2 checked. Mandatory IPEX selector position and open PCB branch encoded in schematic/BOM/assembly notes. Manual does not publish its component designator/value; none invented |
| Exact JLC module connectors | C411294/C411312 listings and model-matched photos show populated IPEX receptacles. Evidence archived. E28 selected RF path is a separate assembly requirement |
| MPNs and footprints | Physical connector/passive MPNs selected; ten custom library patterns and standard patterns checked against manufacturer dimensions. See FOOTPRINT_REVIEW.md and extracted geometry |
| Updated review package | This file, GPIO_MAP.md, POWER_BUDGET.md, interface/assembly/footprint notes and Rev-A-electrical-studies.pdf updated |

## Rev A physical priorities

Do not optimize Rev A for size. Keep the four radio slots physically spread out, give the 5-V distribution generous copper, provide useful test points throughout the carrier and cards, and keep each switcher's high-current loops compact. A larger board that is easy to probe and debug is preferred. [LAYOUT_REQUIREMENTS.md](LAYOUT_REQUIREMENTS.md) records the required probe coverage and access checks. These priorities are implemented in the layouts described below.

## Configurable SPI source termination

All six schematic resistor positions start at **22 ohms**, using Yageo **RC0603FR-0722RL**, 1%, 0.1 W, with `Resistor_SMD:R_0603_1608Metric`. The E28 design is installed twice, giving **seven physical resistors**: SCK, MOSI and five independent MISO sources. Each BOM and schematic Assembly property permits **RC0603JR-070RL, 0 ohms**, in the same footprint. Fit one selected value; DNP opens the signal. No parallel bypass trace or separate jumper is permitted.

| Design / resistor | Source side, pad 1 | Bus side, pad 2 | Implemented source placement |
| --- | --- | --- | --- |
| Carrier R20 | U5 B1 pin 21, SPI_SCK_SRC | SPI_SCK to all slots and U4 SCK | Immediately after the carrier output buffer, before fanout |
| Carrier R21 | U5 B2 pin 20, SPI_MOSI_SRC | SPI_MOSI to all slots and U4 SI | Immediately after the carrier output buffer, before fanout |
| Carrier R22 | U4 SO pin 14, EXP_MISO_SRC | Shared SPI_MISO | Immediately at MCP23S17 SO, before joining the shared bus |
| E22 R5 | U1 MISO pad 16, SPI_MISO_SRC | SPI_MISO to slot A7 | Immediately at the module's MISO output |
| Core2021 R3 | U1 MISO pin 11 through J4 pin 3, SPI_MISO_SRC | SPI_MISO to slot A7 | Immediately beside J4 pin 3, the nearest accessible source point on the adapter |
| E28 R5, on each of two cards | U1 MISO pad 3, SPI_MISO_SRC | SPI_MISO to slot A7 | Immediately at each module's MISO output |

The SRC nets are local to their respective schematics. Each contains only its driver and resistor pad 1; Core additionally contains its physical socket contact. Radio slot pin assignments remain unchanged. U7 still receives the shared MISO bus and drives the separate Pico-side net; it is not another independent source driving the shared bus.

Keep every driver-to-resistor connection short and inline. Do not route a signal away from its source just to reach the resistor, a test header or a convenient probe location. Keep test pads on the existing path, without long stub traces. On the plug-in Core, the module's internal trace and header precede the adapter resistor; their length must be included in measurement/modeling. Resistor footprints do not replace shared-bus topology and fanout review.

**22 ohms is an initial population value, not a validated impedance match.** During bring-up, verify and tune each path with an oscilloscope and IBIS analysis where models are available. Model the actual buffer/driver and receiver loading, connectors and routed interconnect; do not treat a bare-chip model as a complete radio-module model. Probe source and relevant receiver ends with short ground connections, check overshoot/undershoot, ringing, edge settling and setup/hold margin against the actual device limits, and exercise each MISO driver separately. Check intended SPI speeds, supply corners and supported card populations, including all four installed. Record the chosen values, clock rate, loading and waveforms/model results. Retain the 0-ohm option for those comparisons.

Exported-netlist checks verify each split net and its exact members, resistor endpoints, initial value, footprint and alternate-population metadata. They reject direct source-to-bus bypasses and accidental extra connections on source segments. Native-board measurements below independently check source proximity and the routed interconnect. No source net contains a test point or a pre-resistor branch.

## ERC findings and what changed

The previous carrier errors were undriven GND and undriven Pico VSYS. They reflected a genuinely unfinished power circuit. J9 now supplies the common ground and external input; U2 supplies RADIO_5V, while Q1 and the Pico onboard USB diode provide VSYS. Power-source declarations model those physical sources. They do not stand in for missing regulator/protection circuitry.

The previous warning was the one-pin `VSYS_PROTECTED_REQUIRED` label. It meant the label reached no second connected pin. The finished `PICO_VSYS` net joins Q1 source, Pico pin 39 and its socket. The warning consequently disappears. There is **no remaining ERC warning** to waive. KiCad's raw reports retain its default ignored classes; no new suppressions, exclusions or downgraded severities were introduced.

Independent exported-XML checks cover 272 specific pin assignments, 40 NC/isolation checks, all BOM MPNs, power-buffer directions and mechanical engagement arithmetic, plus six source-series topology/population checks. ERC does not prove current capacity, regulator stability, RF performance, mechanical fit or absence of semiconductor leakage. Those have separate calculations and later hardware acceptance requirements.

## Boundaries that remain explicit

The schematic choices are now concrete. **E28 factory IPEX configuration still needs supplier/assembler acceptance before procurement.** C411312's listing and photo prove catalog connector population, not its as-delivered selected RF branch or an accepted rework service. Public documentation does not identify the selector's value or reference designator. The assembly requirement preserves the existing vendor component and uses the manual's physical position; replacement would require manufacturer clarification. No messages were sent and no parts were ordered.

The 4 A rating is a design target subject to the documented copper/reference-layout requirements, 0-40 C bench ambient and later thermal/load/inrush measurements. The capacitor-bias allowance and transient model are engineering bounds, not guaranteed measured performance. Full 30 dBm E22 output is not guaranteed from exactly 5 V at the carrier connector after path losses. RF coexistence and antenna separation require later testing.

Mechanical footprint dimensions and connector mapping are checked; physical fit is not yet tested because there are no boards. The alignment post and solid capture regions are preserved in all four layouts. Do not replace them with unequal header lengths or silkscreen arrows.

Semtech's current product page lists LR20xx v2.2, while the saved Waveshare-linked full datasheet is v2.1. This review uses the Waveshare module schematic for connector wiring and conservative module power reserves; it does not claim a v2.2 protocol audit. Compare the current radio-command documentation before implementing firmware.

The four `.kicad_pcb` files are the authoritative routed designs. No fabrication or ordering outputs were created. The original breadboard/prototype work and pre-existing root README edits are preserved.

## Board geometry, access and validation

Carrier: **250 x 210 mm**, two layers, **70 um (2 oz) copper per side**, 1.6 mm board. Each daughtercard is **84 x 80 mm**. S1 (915 LORA) is upper left, S2 (915 FLRC) lower right, S3 (2.4 LORA) lower left and S4 (2.4 FLRC) upper right. Same-band A1 locations are 168.0 mm apart. Card outlines have a 51 mm horizontal gap and 20 mm vertical gap. This is physical separation for bench work, not an RF coexistence qualification.

Installed-view slot coordinates, in carrier millimetres:

| Slot | A1 | B1 | Post H |
| --- | --- | --- | --- |
| S1 | 20,25 | 50.48,25 | 27.62,30.08 |
| S2 | 155,125 | 185.48,125 | 162.62,130.08 |
| S3 | 20,125 | 50.48,125 | 27.62,130.08 |
| S4 | 155,25 | 185.48,25 | 162.62,30.08 |

`audit_layouts.py` checks every header pad against the exact interface geometry. `audit_mechanics.py` checks the installed card envelopes, actual footprint bodies, both mandatory solid-capture rectangles and every drilled pad/via. The post uses a 3.4 mm NPTH and 7 mm exclusion diameter. The capture areas contain no added holes, vias or components. Correctly installed cards sit 11.05 mm above the carrier; the post protrudes nominally 10.75 mm above the card top. The 5.35 mm worst-case pre-contact engagement margin remains unchanged. Under each card, the carrier has only its intended sockets and alignment post. No card has underside components beyond its two mating headers.

The Pico occupies the central top corridor, USB facing the top edge. Its USB approach, BOOTSEL top access and lower debug access remain open. Carrier probes are at x=97 or 138, outside the installed card rectangles; ground clips have 3.4 mm body clearance from card edges. Card-edge gaps provide independent removal access. Use a nonconductive bench support that clears the four screw heads; they remain accessible from below.

All radio IPEX receptacles have vertical access. The E22 cable exits along local x=39..46 beyond y=38.5; E28 exits along x=52..59 beyond y=26.5. Core cables leave over low passives, below its >=8.51 mm socket clearance. Keep flexible antenna leads above the boards and directed outward; do not drape them across the buck or probe banks. The E28 antenna-end keepout is present on both card and carrier copper layers, including under the two installed modules. RF remains entirely inside the modules; no carrier RF trace exists.

The four individual 3D views, [assembled four-card view](renders/rev-a-assembled-3d.png) and [low-angle mating view](renders/rev-a-assembled-side.png) are in renders/. Custom radio, Pico, header, post and capacitor models are dimensioned clearance envelopes, not manufacturer production CAD. Core/Pico plug-in models use nominal header standoff for visualization; the access check uses the lower socket-height bound. These checks establish geometric clearance. Physical insertion, cable strain, socket tolerances and the specified unpowered misinsertion tests remain assembly acceptance work.

## Routed SPI measurements

Lengths below are routed pad-centre distances, including 1.6 mm per via transition, rounded to 0.1 mm. They exclude module-internal traces and connector contact length. The independent graph splits trace junctions and checks exact source-net membership. Source-side copper has no branches, vias or test stubs.

| Source | Resistor | Source-to-pad-1 length |
| --- | --- | ---: |
| carrier-rev-a: U5.21 | R20 | 2.31 mm |
| carrier-rev-a: U5.20 | R21 | 4.46 mm |
| carrier-rev-a: U4.14 | R22 | 2.23 mm |
| e22-900m30s-rev-a: U1.16 | R5 | 2.58 mm |
| core2021-hf-m-rev-a: J4.3 | R3 | 3.73 mm |
| e28-2g4m27s-rev-a: U1.3 | R5 | 2.58 mm |

These are pad-centre lengths; the exposed inter-pad trace is shorter. R20/R21 are beside the U5 output side, R22 beside U4 SO, and each radio source resistor beside its module/socket source pad. Core R3 is next to J4.3. Initial population remains 22 ohms with the documented 0-ohm option.

The carrier uses a shared branched tree with two slot columns, not four isolated SPI links. Routes share copper before diverging; the following path lengths must not be added as independent branches. The left-hand MOSI continuation is the longest path. No serpentine length matching or redundant test header was added. The slot-to-module wiring is another load branch once a card is inserted.

| Carrier path from resistor pad 2 | S1 | S2 | S3 | S4 | Local endpoint |
| --- | ---: | ---: | ---: | ---: | ---: |
| SPI_SCK (R20) | 228.1 mm | 82.4 mm | 170.7 mm | 84.8 mm | 60.3 mm (U4.12) |
| SPI_MOSI (R21) | 372.7 mm | 102.9 mm | 260.7 mm | 96.5 mm | 164.4 mm (U4.13) |
| SPI_MISO (R22) | 172.0 mm | 62.4 mm | 104.3 mm | 122.1 mm | 62.6 mm (U7.4) |

For MISO the reference above is the expander's bus-side resistor. Each card has its own source resistor; only the selected source may drive the shared bus. U7 is the receiving buffer.

| Card: slot to module/socket (MISO to resistor pad 2) | SCK | MOSI | MISO |
| --- | ---: | ---: | ---: |
| e22-900m30s-rev-a | 55.3 mm | 40.8 mm | 47.5 mm |
| core2021-hf-m-rev-a | 59.5 mm | 59.5 mm | 66.0 mm |
| e28-2g4m27s-rev-a | 48.9 mm | 52.1 mm | 44.5 mm |

Every card SPI probe is now only **2.0 mm from its header contact**, on the existing path or a short local branch. Longer probe detours found during review were removed. Bare pads are used instead of wire-loop SPI probes. The long shared interconnect is intentional for separated bench slots and is not impedance-qualified: use the actual tree and connector loading for IBIS/oscilloscope work. No maximum SPI rate or successful simultaneous-radio operation is claimed from DRC.

## Power and AP63203 copper review

The carrier has 6 mm horizontal protected-power runs, an **8 mm right-hand trunk**, 4 mm entry/main fanout copper and 2 mm slot drops, with both A2/A3 power contacts joined by >=1.5 mm copper. Power traces are reinforced by solid-connection pours. High-current power never changes layers through a single via. Bottom ground retains verified 10 mm main return corridors and >=4 mm branch corridors; the local signal routing does not cut those corridors. Ground stitching ties remaining top/bottom regions, and native DRC finds no isolated ground connection.

The tiny eFuse package necessarily has a local fanout exception: its 0.30 mm power strips continue about 1 mm beyond the land, then expand through short 1.5 mm fanouts into >=4 mm copper. The longest 1.5 mm entry fanout is 3.7 mm; the output fanout is about 4.0 mm before widening. No thermal spokes are used. This exception is included in the extracted resistance and requires the documented full-load thermal check; it is not represented as 4 mm copper through a 0.30 mm land. Broad board copper surrounds the device, and 4 A remains a design target pending hardware thermal qualification.

[POWER_BUDGET.md](POWER_BUDGET.md) records extracted route lengths, the shared-current voltage-drop estimate and explicit ground/contact assumptions. At 4.75 V at J9, the modeled E28 inputs are 4.47 V at the running allocation and **4.41 / 4.40 V** in the 4 A common-trunk stress calculation. The latter is an engineering estimate with little remaining modeled margin, not a measured supply guarantee. Verify at the slot/regulator probes under startup and load steps. E22's 30 dBm requirement still cannot be guaranteed from exactly 5 V at J9.

The E28 buck was compared with AP63203 datasheet **DS41326 Rev 3-2, Figure 25** and the manufacturer's evaluation-board layout. VIN-to-C1 is 3.30 mm pad-centre; SW-to-L1 is 2.77 mm. C1/C8, U2, L1 and C2/C3/C7 form one local cluster. Bootstrap C4 is above U2: BST is 3.76 mm and its SW branch 7.29 mm. SW is confined to this cluster, has no plane pour and never enters the SPI/control field. Its 0.6 mm probe pad adds less than 0.9 mm of local trace. TP20 provides an exposed ground-spring pad 4.2 mm away, so SW probing does not require a long ground lead. Eighteen ground vias within x=0..20, y=35..57 stitch the IC/capacitor returns to bottom ground. Feedback senses the output capacitor bank on B.Cu, routed around the input/SW cluster, with a 43.7 mm pad-to-pad sense path. It is a quiet sense route, not part of the load-current path. This follows the reference's short VIN/hot-loop, small SW, grounded underside and separated feedback principles; it is not claimed to be an exact copied evaluation board.

References: [AP63203 datasheet](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf), [AP63203 evaluation-board guide](https://www.diodes.com/assets/Evaluation-Boards/AP63203-EVB-User-Guide.pdf). Thermal rise, ripple, startup and loop stability still require powered measurements.

## Final checks and stop point

- Native KiCad DRC: all four boards, all severities, zones refilled, schematic parity enabled; zero findings. No DRC exclusions or severity downgrades.
- Native ERC and exported connectivity: all four schematics pass; 18 GPIOs used, eight spare; GP26/27/28 remain physically unconnected.
- Source-series membership, actual slot geometry, mechanical capture, installed probe access and power-route measurements: recorded in `validation/layout-audit.json`, `mechanical-access.json` and `power-route-audit.json`.
- Schematics, selected BOMs, test-point symbols and combined schematic PDF are synchronized. Bare probe pads are PCB features; fitted ground clips have explicit MPNs.

The final native PCBs are authoritative. Initial placement/router scripts and DSN/SES files are intermediate aids and must not be rerun over the final copper. Stop here for human layout review. No manufacturing export, supplier message, quotation request or order is authorized by this package.
