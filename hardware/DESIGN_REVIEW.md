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

## ERC findings and what changed

The previous carrier errors were undriven GND and undriven Pico VSYS. They reflected a genuinely unfinished power circuit. J9 now supplies the common ground and external input; U2 supplies RADIO_5V, while Q1 and the Pico onboard USB diode provide VSYS. Power-source declarations model those physical sources. They do not stand in for missing regulator/protection circuitry.

The previous warning was the one-pin `VSYS_PROTECTED_REQUIRED` label. It meant the label reached no second connected pin. The finished `PICO_VSYS` net joins Q1 source, Pico pin 39 and its socket. The warning consequently disappears. There is **no remaining ERC warning** to waive. KiCad's raw reports retain its default ignored classes; no new suppressions, exclusions or downgraded severities were introduced.

Independent exported-XML checks cover 272 specific pin assignments, 40 NC/isolation checks, all BOM MPNs, power-buffer directions and mechanical engagement arithmetic. ERC does not prove current capacity, regulator stability, RF performance, mechanical fit or absence of semiconductor leakage. Those have separate calculations and later hardware acceptance requirements.

## Boundaries that remain explicit

The schematic choices are now concrete. **E28 factory IPEX configuration still needs supplier/assembler acceptance before procurement.** C411312's listing and photo prove catalog connector population, not its as-delivered selected RF branch or an accepted rework service. Public documentation does not identify the selector's value or reference designator. The assembly requirement preserves the existing vendor component and uses the manual's physical position; replacement would require manufacturer clarification. No messages were sent and no parts were ordered.

The 4 A rating is a design target subject to the documented copper/reference-layout requirements, 0-40 C bench ambient and later thermal/load/inrush measurements. The capacitor-bias allowance and transient model are engineering bounds, not guaranteed measured performance. Full 30 dBm E22 output is not guaranteed from exactly 5 V at the carrier connector after path losses. RF coexistence and antenna separation require later testing.

Mechanical footprint dimensions and connector mapping are checked; physical fit is not yet tested because there are no boards. The alignment post and solid capture regions are binding inputs to later mechanical design. Do not replace them with unequal header lengths or silkscreen arrows.

Semtech's current product page lists LR20xx v2.2, while the saved Waveshare-linked full datasheet is v2.1. This review uses the Waveshare module schematic for connector wiring and conservative module power reserves; it does not claim a v2.2 protocol audit. Compare the current radio-command documentation before implementing firmware.

No `.kicad_pcb`, board outlines, placement files, Gerbers, drills or manufacturing archives were created. DRC is not applicable yet. The original breadboard/prototype work and pre-existing root README edits are preserved.
