# Rev A schematic review

2026-09-17. **All four schematics pass ERC with zero errors and zero warnings. Stopped before PCB layout, as requested.** The native schematics, BOMs, footprint selections, exported netlists and combined PDF have been updated. These are review artifacts, not a fabrication release.

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

Do not optimize Rev A for size. Keep the four radio slots physically spread out, give the 5-V distribution generous copper, provide useful test points throughout the carrier and cards, and keep each switcher's high-current loops compact. A larger board that is easy to probe and debug is preferred. [LAYOUT_REQUIREMENTS.md](LAYOUT_REQUIREMENTS.md) records the required probe coverage and access checks. This is a documentation update; the current schematic validation remains unchanged and PCB layout remains on hold.

## Configurable SPI source termination

All six schematic resistor positions start at **22 ohms**, using Yageo **RC0603FR-0722RL**, 1%, 0.1 W, with `Resistor_SMD:R_0603_1608Metric`. The E28 design is installed twice, giving **seven physical resistors**: SCK, MOSI and five independent MISO sources. Each BOM and schematic Assembly property permits **RC0603JR-070RL, 0 ohms**, in the same footprint. Fit one selected value; DNP opens the signal. No parallel bypass trace or separate jumper is permitted.

| Design / resistor | Source side, pad 1 | Bus side, pad 2 | Required later placement |
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

Exported-netlist checks verify each split net and its exact members, resistor endpoints, initial value, footprint and alternate-population metadata. They reject direct source-to-bus bypasses and accidental extra connections on source segments. Physical source proximity and stub lengths remain layout-review requirements because no PCB is being created.

## ERC findings and what changed

The previous carrier errors were undriven GND and undriven Pico VSYS. They reflected a genuinely unfinished power circuit. J9 now supplies the common ground and external input; U2 supplies RADIO_5V, while Q1 and the Pico onboard USB diode provide VSYS. Power-source declarations model those physical sources. They do not stand in for missing regulator/protection circuitry.

The previous warning was the one-pin `VSYS_PROTECTED_REQUIRED` label. It meant the label reached no second connected pin. The finished `PICO_VSYS` net joins Q1 source, Pico pin 39 and its socket. The warning consequently disappears. There is **no remaining ERC warning** to waive. KiCad's raw reports retain its default ignored classes; no new suppressions, exclusions or downgraded severities were introduced.

Independent exported-XML checks cover 272 specific pin assignments, 40 NC/isolation checks, all BOM MPNs, power-buffer directions and mechanical engagement arithmetic, plus six source-series topology/population checks. ERC does not prove current capacity, regulator stability, RF performance, mechanical fit or absence of semiconductor leakage. Those have separate calculations and later hardware acceptance requirements.

## Boundaries that remain explicit

The schematic choices are now concrete. **E28 factory IPEX configuration still needs supplier/assembler acceptance before procurement.** C411312's listing and photo prove catalog connector population, not its as-delivered selected RF branch or an accepted rework service. Public documentation does not identify the selector's value or reference designator. The assembly requirement preserves the existing vendor component and uses the manual's physical position; replacement would require manufacturer clarification. No messages were sent and no parts were ordered.

The 4 A rating is a design target subject to the documented copper/reference-layout requirements, 0-40 C bench ambient and later thermal/load/inrush measurements. The capacitor-bias allowance and transient model are engineering bounds, not guaranteed measured performance. Full 30 dBm E22 output is not guaranteed from exactly 5 V at the carrier connector after path losses. RF coexistence and antenna separation require later testing.

Mechanical footprint dimensions and connector mapping are checked; physical fit is not yet tested because there are no boards. The alignment post and solid capture regions are binding inputs to later mechanical design. Do not replace them with unequal header lengths or silkscreen arrows.

Semtech's current product page lists LR20xx v2.2, while the saved Waveshare-linked full datasheet is v2.1. This review uses the Waveshare module schematic for connector wiring and conservative module power reserves; it does not claim a v2.2 protocol audit. Compare the current radio-command documentation before implementing firmware.

No `.kicad_pcb`, board outlines, placement files, Gerbers, drills or manufacturing archives were created. DRC is not applicable yet. The original breadboard/prototype work and pre-existing root README edits are preserved.
