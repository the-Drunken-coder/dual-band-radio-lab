# Rev A layout requirements

Rev A prioritizes probing, debugging and replaceable modules. **Do not optimize for board size.** A slightly oversized carrier is preferred. These requirements guide the next design phase; PCB layout and manufacturing output remain on hold.

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

## Required probe coverage

Provide clearly labeled test points at the following locations. These are requirements for the next schematic/layout revision, not a claim that test-point components have already been added to the current schematics.

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

Before the later layout is accepted, review probe access with all four card envelopes, antenna plugs and the Pico present. Check the power path and each switcher loop separately. Board area is expendable; accessible measurements and controlled current paths are the priorities.
