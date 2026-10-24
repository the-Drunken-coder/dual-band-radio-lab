# How the USB test carrier works

The carrier supports repeatable radio experiments without rewiring breadboards. It gives the laptop one USB connection and gives the ESP32 two independently controlled LR2021 modules.

## Responsibilities

| Part | Responsibility |
| --- | --- |
| Laptop | Build and flash firmware, select experiments, collect results, and compare runs. |
| ESP32-S3 | Run radio drivers, serialize SPI transactions, respond to interrupts, and execute timed tests. |
| LR2021 modules | Generate and receive RF packets using their selected band, PHY, and packet configuration. |
| Carrier PCB | Connect sockets, distribute power, provide local decoupling, and expose measurement points. |

The laptop does not control SPI directly through USB. It sends commands to firmware running on the ESP32. Radio timing and interrupt handling belong on the ESP32 so laptop scheduling does not control time-sensitive radio operations.

## What is implemented

The hardware design includes one Waveshare ESP32-S3-DEV-KIT-N8R8-M and two Core2021-HF-M sockets. The two radios share SPI clock, MOSI, and MISO. Each radio has its own chip-select, DIO11 interrupt, BUSY, and reset connections. Source resistors are fitted on clock and MOSI, and each select and reset line has a pullup.

| Signal | ESP32 GPIO |
| --- | ---: |
| Shared SCK | 12 |
| Shared MOSI | 11 |
| Shared MISO | 13 |
| Radio A CS, IRQ, BUSY, RESET | 10, 4, 5, 6 |
| Radio B CS, IRQ, BUSY, RESET | 9, 7, 15, 16 |

DIO11 is the radio pin name. It does not mean ESP32 GPIO11.

USB-C supplies both data and power through the controller board. The controller's downstream USB supply feeds the carrier's TLV1117LV33 regulator. That regulator powers the radio modules at 3.3 V. Its output is separate from the controller's own 3.3 V regulator output, with a common ground.

The controller's USB-to-UART bridge supports automatic BOOT and reset independently of the application firmware. This gives command-line flashing tools a recovery path when a radio experiment crashes. A controller reset is not a full power cycle. Removing all board power still requires unplugging USB or adding external test equipment.

The carrier includes no firmware, radio driver integration, laptop CLI, battery system, or automatic radio power switch.

## Intended experiment flow

This is the proposed workflow for the software, not a tested implementation:

1. The laptop identifies each controller and flashes a known firmware build through the CH343 serial interface.
2. Firmware keeps both chip-selects high, initializes the GPIOs, resets each radio, and confirms basic SPI, BUSY, and interrupt behavior.
3. The laptop selects one radio and a complete test profile. Firmware applies the profile and reports the actual settings and status.
4. A compatible peer sends or receives a fixed packet workload. Start with one radio active per node.
5. Firmware records packet events, counters, timing, and available link-quality information. The laptop saves those results with device identity, build revision, profile, and test conditions.
6. After isolated baselines pass, the laptop can compare configurations or request controlled tests involving both radios.

One complete profile includes more than a band and PHY. It also needs a frequency, bandwidth or bitrate, coding and synchronization parameters, packet format, and an appropriate transmit-power setting. Compatible peers must agree on the relevant settings.

Only one SPI device can be selected at a time. Firmware must coordinate access, wait for the selected radio's BUSY signal as required, and keep each radio's state separate. Sharing SPI does not require both radios to have the same RF role.

## Software still needed

- ESP32 build configuration and LR2021 driver integration using the included GPIO map.
- Independent radio initialization, interrupt handling, packet queues, and fault reporting.
- A serial command and event format with bounded operations and machine-readable errors.
- A laptop runner that owns each serial port, flashes builds, enforces timeouts, and writes reproducible test records.
- A hardware bring-up procedure that checks power and fit before progressing to radio experiments.

An AI coding agent can invoke that runner once it exists. The PCB itself does not supply an agent API or implement automatic link selection, relaying, failover, or a network stack.

## Relationship to the four-lane node

The project's target has dedicated listeners for 915 LoRa, 915 FLRC, 2.4 LoRa, and 2.4 FLRC. Each listener normally stays on its fixed network profile. Two LR2021s can cover two selected profiles at once, even though each chip supports multiple configurations across separate experiments.

This carrier can produce useful LR2021 characterization results, especially for the proposed 915 FLRC lane. Those results can inform whether LR2021 belongs in the final mixed-radio design. They do not characterize an SX1262, SX1280, amplified module, or the larger carrier by substitution.

The existing Rev A design uses a Pico 2, a different GPIO allocation, external radio power, and a standard daughtercard interface. Its daughtercards are not mechanically or electrically interchangeable with this carrier's direct Core2021 sockets. The only plug-in radio variant specified here is Core2021-HF-M.

The [staged rollout](../../docs/staged-rollout.md) prioritizes separate radio tests using suitable evaluation hardware. This optional design does not make a custom PCB necessary for those tests or replace that plan.

## Hardware limits that affect experiments

The design allows 300 mA for the radio rail, subject to measurement of the complete USB power path. The controller, bridge, hub, and LEDs also consume USB power. Waveshare does not specify the external current allowance through the chosen header and onboard diode. Validate both supply rails, transients, total current, and diode and regulator temperatures under the intended workload.

The initial test configuration keeps ESP32 Wi-Fi and Bluetooth disabled. Their power and 2.4 GHz RF activity would add variables to the radio measurements.

The sockets are not keyed. Verify module direction, contact alignment, seating, and USB access before power is applied. Manufacturer drawings establish nominal pitch and row spacing, but supplied male-post fit still needs physical samples.

The two module antennas can couple strongly. There are no carrier filters or receiver-protection parts. Simultaneous local transmit and receive operation remains a separate measurement and protection problem. Follow the project's profile qualification and RF test requirements before transmitting.

Native KiCad checks establish a set of CAD properties. They do not establish any of these physical or RF results. Use the included reports and hashes to identify the checked design, then record hardware evidence from the actual assembled units.
