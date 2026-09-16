# Dual-Band Radio Lab

Notes and experiments for a portable dual-band radio system.

## Vision

Explore a man-portable radio, roughly walkie-talkie-sized or slightly larger, with two or more antennas and simultaneous receive coverage across 915 MHz and 2.4 GHz.

The current architecture under evaluation uses dedicated receive paths for LoRa and FLRC rendezvous profiles on both bands, plus one separate agile transmitter that switches band/PHY as commanded. The receiver side is intended to remain aware of both bands at once; simultaneous 915 MHz and 2.4 GHz transmission is not currently required.

The goal is to combine higher-bandwidth links with lower-rate, longer-range options for essential traffic, emergency communication, backup connectivity, and experimentation with automatic link selection. Relaying and automatic failover are possible future software features. This is the intended direction, not a demonstrated capability.

## Confirmed hardware requirements

- **U.S. operation:** Must be usable legally in the United States without an amateur-radio license.
- **Budget:** Up to $150 per radio, with a stretch ceiling of $175.
- **Concurrent reception:** The node should be able to monitor the required 915 MHz and 2.4 GHz rendezvous paths simultaneously rather than relying on one receiver to switch between bands or PHYs.
- **Current TX architecture:** One independent agile transmitter may switch between 915 MHz and 2.4 GHz and between LoRa/FLRC profiles. Transmissions are serialized; simultaneous dual-band TX is not a current requirement.
- **Portability:** Battery-powered and roughly walkie-talkie-sized or slightly larger. Exact dimensions, weight, and runtime are undecided.

Compute and USB/laptop connectivity remain undecided. An onboard single-board computer, such as a Raspberry Pi Zero, is an option rather than a requirement or an exclusion.

## Hardware direction

The dedicated receiver-bank architecture currently under evaluation uses low-cost Waveshare Core2021-HF-M (LR2021) modules because the same module can cover the intended 850-930 MHz region and 2.4 GHz and can operate with LoRa or FLRC. The baseline proposal is four fixed receive paths plus one agile TX. See `docs/dedicated-receiver-bank.md` for the architecture and prototype plan.

Other radio hardware remains useful for comparison and experimentation, but replacing the inexpensive receiver bank with substantially more expensive SDR or RF hardware would conflict with the current cost target.

## Example deployment

A person inside a house connects through a rooftop relay to a drone roughly one mile away. The node can keep standardized 915 MHz and 2.4 GHz rendezvous receive paths available at the same time, while its single transmitter selects the appropriate band/PHY/profile for each outgoing transmission.

This is a scenario to test, not a confirmed range claim or a commitment to specific relaying or failover software. Terrain or obstructions could interrupt both links; 915 MHz is not assumed to guarantee coverage behind a hill.
