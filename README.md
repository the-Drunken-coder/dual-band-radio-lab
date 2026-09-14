# Dual-Band Radio Lab

Notes and experiments for a portable dual-band radio system.

## Vision

Explore a man-portable radio, roughly walkie-talkie-sized or slightly larger, with two or more antennas and independent 915 MHz and 2.4 GHz radios operating simultaneously.

The goal is a higher-bandwidth 2.4 GHz link alongside a lower-rate 915 MHz LoRa network for essential traffic, emergency communication, and backup connectivity. FLRC is of interest for the faster link, but its hardware and firmware are undecided.

Nodes would relay traffic and automatically shift essential communication onto the available links as conditions change. This is the intended direction, not a demonstrated capability.

## Hardware shortlist

- **915 MHz — planned choice:** High-power Heltec V4 LoRa radio.
- **2.4 GHz — undecided:** Candidates discussed include the LILYGO T3-S3 SX1280 with PA and LR2021-based development hardware. No selection has been made.

## Example deployment

A person inside a house connects through a rooftop relay to a drone roughly one mile away. The relay uses the higher-bandwidth 2.4 GHz link when the path supports it, while the independent 915 MHz link remains available for essential communication if the faster link degrades or drops.

This is a scenario to test, not a confirmed range claim. Terrain or obstructions could interrupt both links; 915 MHz is not assumed to guarantee coverage behind a hill.
