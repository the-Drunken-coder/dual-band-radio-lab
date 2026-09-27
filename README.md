# Dual-Band Radio Lab

**Volunteer project:** Lane Araujo volunteered to take on this portable dual-band radio project. This repository documents the research and experiments.

## Vision

Explore a man-portable radio, roughly walkie-talkie-sized or slightly larger, with two or more antennas and independent 915 MHz and 2.4 GHz radios operating simultaneously.

The goal is a higher-bandwidth 2.4 GHz link alongside a lower-rate 915 MHz LoRa network for essential traffic, emergency communication, and backup connectivity. FLRC is of interest for the faster link, but its hardware and firmware are undecided.

Relaying and automatic failover are possible future software features, not current hardware requirements. All software choices remain open. This is the intended direction, not a demonstrated capability.

## Confirmed hardware requirements

- **U.S. operation:** Must be usable legally in the United States without an amateur-radio license.
- **Budget:** Up to $150 per radio, with a stretch ceiling of $175. The total budget for a complete dual-radio unit is not yet set.
- **Concurrent operation:** Independent 915 MHz and 2.4 GHz radios capable of operating simultaneously, not a single transceiver switching between bands.
- **Portability:** Battery-powered and roughly walkie-talkie-sized or slightly larger. Exact dimensions, weight, and runtime are undecided.

Compute and USB/laptop connectivity remain undecided. An onboard single-board computer, such as a Raspberry Pi Zero, is an option rather than a requirement or an exclusion.

## Hardware shortlist

- **915 MHz — planned choice:** High-power Heltec V4 LoRa radio.
- **2.4 GHz — undecided:** Candidates discussed include the LILYGO T3-S3 SX1280 with PA and LR2021-based development hardware. No selection has been made.

## Example deployment

A person inside a house connects through a rooftop relay to a drone roughly one mile away. The relay uses the higher-bandwidth 2.4 GHz link when the path supports it, while the independent 915 MHz link remains available for essential communication if the faster link degrades or drops.

This is a scenario to test, not a confirmed range claim or a commitment to specific relaying or failover software. Terrain or obstructions could interrupt both links; 915 MHz is not assumed to guarantee coverage behind a hill.
