# Pico 2 GPIO allocation

Rev A uses **18 of 26 exposed GPIOs** and leaves **eight spare**: GP18, GP19, GP20, GP21, GP22, GP26, GP27 and GP28. All eight are no-connects on both the logical Pico symbol and its physical sockets. GP23-25 and GP29 are Pico onboard functions.

| Function | GPIO | Pico physical pin |
| --- | --- | --- |
| S1 IRQ / BUSY | GP0 / GP1 | 1 / 2 |
| S2 IRQ / BUSY | GP2 / GP3 | 4 / 5 |
| Shared SPI0 MISO | GP4 | 6 |
| S1 CS_N | GP5 | 7 |
| Shared SPI0 SCK / MOSI | GP6 / GP7 | 9 / 10 |
| S3 IRQ / BUSY | GP8 / GP9 | 11 / 12 |
| S4 IRQ / BUSY | GP10 / GP11 | 14 / 15 |
| S2 / S3 / S4 CS_N | GP12 / GP13 / GP14 | 16 / 17 / 19 |
| MCP23S17 CS_N | GP15 | 20 |
| MCP23S17 RESET_N | GP16 | 21 |
| Interface OE_N | GP17 | 22 |

SPI, four CS, four BUSY and four IRQ consume 15 pins. Expander CS/reset and interface enable consume three more. U5/U6 are fixed-direction dual-supply buffers, not serialized GPIO expanders. BUSY/IRQ/CS retain direct MCU timing. U7 carries MISO in the radio-to-Pico direction. Start bring-up at 1 MHz SPI, mode 0; a higher shared-bus speed requires timing and signal-integrity qualification.

## Expander assignment

MCP23S17-E/SO shares SPI0 with the radios, with address pins A0-A2 grounded. Only one CS may be active. U4's GPB0-3, physical pins 1-4, drive S1-S4 RESET_N. GPA0-5, pins 21-26, drive S1 TX, S1 RX, S3 TX, S3 RX, S4 TX, S4 RX. Other GPIOs and interrupt pins are NC. This leaves six expander pins unused as well.

The E22 can use SX1262 DIO2-controlled TX switching, but its separate module RXEN still needs control. DIO3 is committed to its internal 2.2 V TCXO. E28's SX1281 and module TX_EN/RX_EN do not supply an equivalent documented automatic two-line control solution. Core2021 already handles its radio switch internally. A uniform host-controlled expander avoids assuming undocumented module wiring. Sources: Ebyte E22 manual pin table and software section, E28 manual sections 3/4.2, Waveshare Core schematic, Microchip DS20001952C.

Reset is infrequent. External PA/LNA selection is moved only before a radio mode command, so it does not require edge-synchronous expansion. Rev A excludes Ebyte autonomous RX duty cycling, automatic RX/TX turnaround and firmware modes that change RF state without host preparation. If those modes become requirements, this allocation must be revisited.

## Required firmware sequence

1. Keep GP17 high, CS GPIOs high, GP16 low. U5/U6 remain disabled and U4 reset is asserted through R8. Daughtercard CS pull-ups deselect radios; TX/RX pull-downs disable their external PA/LNA. Radio reset defaults released, but no host transaction can start RF.
2. With external power stable, configure SPI and all output states, then lower GP17. Release U4 reset on GP16. Initialize its output latches before changing IODIR: GPA = 0, GPB = 0. Configure only the ten assigned pins as outputs, read back configuration, then release the required radio reset bits.
3. Serialize all SPI access, including expander writes. Before switching an Ebyte card, command standby, wait for its direct BUSY to clear, write its TX/RX pair to 00, then to 10 for TX or 01 for RX. Never use 11. Preserve the other cards' bits in the shadow register.
4. Read back OLAT and allow at least 10 us engineering settling time before issuing SetTx/SetRx. One 24-bit expander write takes 24 us at 1 MHz, so budget roughly 100 us for clear/set/readback plus settling. This is an explicit scheduling cost, not an interrupt-path delay. Return to 00 after standby or completion.
5. After Pico reset or external-power interruption, reinitialize the expander and all radios. Do not transmit during the 100 ms startup holdoff. On loss of communication or invalid readback, disable U5/U6 and stop RF commands.

## ADC back-power guarantee

Pico 2 datasheet section 5.2 warns that ADC-capable GPIO26-29 have a diode to IOVDD. **GP26-28 have no carrier traces to daughtercard outputs, pull-ups, test points or expander signals.** Exported-netlist checks verify NC at Pico physical pins 31, 32 and 34 and socket J11 pins 11, 12 and 14. GP29 remains onboard and is not brought to this interface.

Every used signal crosses U5/U6/U7 between PICO_3V3 and externally powered IOREF_3V3. Their documented VCC isolation and Ioff prevent USB-only signal drive into the radio domain and radio-domain drive into an unpowered Pico. U5/U6 OE defaults disabled. No firmware sequencing claim substitutes for the ADC-pin NC guarantee. See TI SCES584D and SCES515N and the power-state table in POWER_BUDGET.md.

## SPI source termination

GPIO allocation is unchanged. U5's radio-side SCK/MOSI outputs now reach the shared bus through carrier R20/R21. Each radio MISO output reaches slot A7 through its own card resistor, and MCP23S17 SO reaches the bus through carrier R22. All initially use 22 ohms with a same-footprint 0-ohm option. Verify values and supported SPI speed by oscilloscope/IBIS during bring-up; see DESIGN_REVIEW.md.
