# Rev A layout requirements

Rev A prioritizes probing, debugging and replaceable modules. **Do not optimize for board size.** A slightly oversized carrier is preferred. These requirements govern the routed review layouts. Manufacturing output remains on hold; implementation evidence is in DESIGN_REVIEW.md.

## Placement and access

- Spread all four radio slots across the carrier. Give particular attention to separating the two 915 MHz radios and the two 2.4 GHz radios. Do not cluster the slots to shrink the outline.
- Leave room to insert and remove each card, connect its antenna cable and attach probes while all four cards are installed. Keep antenna cables clear of the switching supplies and their current loops.
- Keep Pico USB, BOOTSEL and debug connections accessible. Preserve the alignment posts, their tool access and the solid capture areas specified in `radio-slot-v0.1.md`.
- Choose the board outline after allocating those spaces. No enclosure or compact-board target takes precedence over bench access. Physical separation still needs RF coexistence testing; it does not establish receiver protection by itself.

## Power distribution and switchers

- Give the 5-V trunk, slot branches and ground return broad copper pours. The widths in `POWER_BUDGET.md` are minimums, not targets to squeeze down to. Avoid necks at connectors, protection devices and layer transitions.
- Recalculate resistance and voltage drop using the actual, potentially longer routes. Preserve the 4-A carrier target and local bulk capacitance at each radio load.
- Keep each buck's input ceramic capacitors, IC, switching connections and return path together, following the AP63203 reference layout. Keep the bootstrap connection short and feedback away from the switch node. Spread out the radio subsystems while keeping each switcher's high-current loops compact.
- Make regulator input, output and local ground easy to probe without enlarging the switching loop. A switch-node measurement pad must sit on the existing local copper; do not run that node out to a remote header or wire loop.

## SPI source-series placement

Keep B.Cu as close as practical to a continuous GND reference. Route SPI and other fast signals on F.Cu wherever practical, avoiding reference-plane voids and long ground cuts. Where a fast signal must change layers, place a GND stitching via immediately beside its signal via. Apply this to all daughtercards, particularly E28, while preserving every mechanical capture area and antenna keepout.

After every routing change, refill zones and audit non-GND B.Cu count/length, every SPI transition and its nearest GND via, and every SPI portion without opposite-layer GND. Report residual gaps explicitly for review. A single connected ground pour and clean DRC alone do not demonstrate a good high-frequency return path. The current pass's maximum measured SPI-to-GND-via distance is recorded in DESIGN_REVIEW.md.

Fit carrier R20 immediately after U5 pin 21 for SCK and R21 after U5 pin 20 for MOSI, before fanout. Fit carrier R22 immediately at MCP23S17 U4 SO pin 14 before its MISO branch joins the bus. Fit E22/E28 R5 at each module MISO output and Core R3 beside socket J4 pin 3. Both E28 card instances need their own R5. Use short inline connections with no parallel bypass or long test-point/header stubs.

All start at 22 ohms; the same 0603 footprint accepts the documented 0-ohm alternate. Confirm values by oscilloscope/IBIS during bring-up. See DESIGN_REVIEW.md for the exact endpoint table and measurement requirements. These parts are now in the schematics; their physical placement and routed lengths are recorded in DESIGN_REVIEW.md.

## Required probe coverage

Provide clearly labeled test points at the following locations. The required pads and fitted ground clips are now present in both schematics and layouts.

| Area | Required access |
| --- | --- |
| Carrier power | External 5 V before protection, RADIO_5V after protection, and 5 V at each slot branch |
| Pico and interface power | USB VBUS, Pico VSYS, PICO_3V3 and IOREF_3V3 |
| Daughtercard power | Local slot input, each regulator output and ground at the module supply |
| Radio control, each slot | CS_N, BUSY, IRQ and RESET_N; TX_EN/RX_EN on the three Ebyte cards |
| Shared SPI | SCK, MOSI and MISO at the controller interface and accessible card-side pads, with minimal added stubs |
| Interface control | Expander CS/reset and buffer OE_N; access on both sides of isolation where useful for diagnosing missing power or signals |
| Power protection and conversion | Accessible UVLO, OVLO, DVDT and ILIM nodes; local buck enable, feedback and switch-node pads where probing will not compromise the circuit |
| Ground | Sturdy ground attachment near the power entry and each slot, plus adjacent ground pads for short oscilloscope ground springs at each regulator |

Use pads for fast or sensitive nodes and factory-fitted loop points where repeated clip attachment helps. Keep enough clearance for the intended probes and clips without touching adjacent conductors. Label rail voltages and slot identities on the board. Probe access must work with daughtercards installed; points hidden beneath modules do not meet this requirement.

Keep the existing GP26-GP28 no-connect guarantee. Do not connect those pins to daughtercards or powered diagnostic headers while adding test access. Use appropriately high-impedance probes on protection thresholds and feedback nodes.

Before manufacturing release, review probe access with all four card envelopes, antenna plugs and the Pico present. Check the power path and each switcher loop separately. Board area is expendable; accessible measurements and controlled current paths are the priorities.
