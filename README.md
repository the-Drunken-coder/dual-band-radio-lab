# Dual-Band Radio Lab

For the current evidence map, project boundaries and continuation state, see [project context](docs/project-context.md).

**Volunteer project:** Lane Araujo volunteered to take on this portable dual-band radio project. This repository documents the research and experiments.

## Vision

Explore a man-portable radio, roughly walkie-talkie-sized or slightly larger, with four persistent RF lanes:

- ~915 MHz LoRa
- ~915 MHz FLRC
- 2.4 GHz LoRa
- 2.4 GHz FLRC

The current architecture under evaluation gives each lane its own dedicated transceiver. Each radio normally listens continuously on its fixed network profile and may transmit on that same profile when commanded. The radios do not normally retune between bands or PHYs.

This removes the need for a separate fifth agile transmitter and also removes the requirement that all four lanes use the same radio family. Each lane can instead use hardware optimized for its own band, PHY, power, receiver performance, cost, and regulatory constraints.

The goal is to combine higher-bandwidth links with lower-rate, longer-range options for essential traffic, emergency communication, backup connectivity, and experimentation with automatic link selection. Relaying and automatic failover are possible future software features. This is the intended direction, not a demonstrated capability.

## Confirmed hardware requirements

- **U.S. operation:** Must be usable legally in the United States without an amateur-radio license.
- **Budget:** Up to $150 per complete node, with a stretch ceiling of $175.
- **Persistent receive coverage:** The node should normally monitor all four fixed network receive profiles at once rather than switching one receiver between bands or PHYs.
- **Fixed-role radios:** One transceiver is assigned to each band/PHY lane. A radio may switch between RX and TX, but does not normally change to another lane.
- **Transmission concurrency:** Simultaneous transmission on 915 MHz and 2.4 GHz is worth evaluating because the transmitters are independent. Same-band simultaneous TX/RX is not assumed to work and may require receiver blanking, filtering, protection, or additional isolation.
- **Portability:** Battery-powered and roughly walkie-talkie-sized or slightly larger. Exact dimensions, weight, and runtime are undecided.

Compute and USB/laptop connectivity remain undecided. An onboard single-board computer, such as a Raspberry Pi Zero, is an option rather than a requirement or an exclusion.

## Hardware direction

The architecture no longer requires every lane to use an LR2021. The earlier all-LR2021 design was attractive because one inexpensive chip could cover sub-GHz, 2.4 GHz, LoRa, and FLRC. With four fixed-role radios, that flexibility is no longer necessary.

Current candidate direction:

| Lane | Candidate hardware direction | Reason to investigate |
|---|---|---|
| ~915 MHz LoRa | high-power SX1262-based SPI module | mature sub-GHz LoRa hardware; 30 dBm / 1 W-capable modules exist |
| ~915 MHz FLRC | LR2021-based module | sub-GHz FLRC is an unusual LR2021 capability; high-power variants can also be evaluated |
| 2.4 GHz LoRa | high-power SX1280- or LR1121-based module | dedicated 2.4 GHz LoRa lane can prioritize link budget rather than multi-band flexibility |
| 2.4 GHz FLRC | high-power SX1280-based module or LR2021 | SX1280 is a mature 2.4 GHz FLRC/LoRa device and amplified modules exist |

These are candidates, not finalized purchases. Maximum module output power is a hardware capability, not an assumption that the maximum setting is legal for every LoRa or FLRC profile. Final frequencies, bandwidths, power, antenna gain, EIRP, and spectral limits must be validated for license-free U.S. operation before normal over-the-air testing.

When the four-lane prototype is justified, it may use four separate antennas, one per transceiver. This avoids the passive splitter loss and RF switching complexity of the earlier shared-antenna concept and makes each RF lane easier to characterize independently. Shared antennas, splitters, filters, LNAs, or duplexing can be reconsidered later if size or antenna count becomes more important.

See the [four-lane architecture](docs/dedicated-receiver-bank.md) for the long-term design and the [individual-radio test plan](docs/staged-rollout.md) for staged development of each radio.

## Develop one radio at a time

Each radio gets its own bring-up and characterization ladder: 2.4-LoRa, 2.4-FLRC, 915-LoRa and 915-FLRC. Test one lane in isolation with a compatible peer, progressing from a fixed-profile bench link through controlled tuning to its own operating envelope. Reuse a compatible SX1280 pair sequentially for the two 2.4 GHz PHYs if inventory confirms one. Combined-node and network work comes afterward.

The plan has explicit pass/stop and purchase gates. Board counts, exact variants and usable peers still need confirmation; candidates remain unselected. Do not order a full four-radio node or fabricate the [Rev A hardware](hardware/README.md) to characterize an individual radio. Its manufacturing hold remains in force.

## Optional LR2021 USB test carrier

The [dual-LR2021 USB test carrier](prototype/dual-lr2021-usb-carrier/README.md) is a separate development platform for laptop-driven radio experiments. It uses a USB-C ESP32-S3 controller and two socketed Core2021-HF-M modules. The archive includes editable KiCad files, pin maps, manufacturer evidence, validation reports, and a prototype fabrication package.

This carrier can test two chosen radio profiles at once. It does not provide the four persistent receive lanes or use the existing Rev A daughtercard interface. Firmware and the laptop test runner remain unimplemented. Physical fit, power, thermal behavior, and RF performance remain unverified.

Treat it as an optional design archive alongside the [individual-radio test plan](docs/staged-rollout.md). Its presence does not approve purchases or change the manufacturing hold on the existing [Rev A hardware](hardware/README.md).

## Example deployment

A person inside a house connects through a rooftop relay to a drone roughly one mile away. Every node normally keeps the four standardized receive profiles active. For outgoing traffic, the host selects the appropriate lane and that lane's transceiver temporarily changes from RX to TX.

A transmission on one band may require the other receiver on that same band to be blanked or protected from local transmitter leakage. Opposite-band receivers may be able to continue receiving during transmission, and simultaneous 915 MHz plus 2.4 GHz transmission is an experiment enabled by the independent radios rather than a guaranteed capability.

This is a scenario to test, not a confirmed range claim or a commitment to specific relaying or failover software. Terrain or obstructions could interrupt multiple links; 915 MHz is not assumed to guarantee coverage behind a hill.
