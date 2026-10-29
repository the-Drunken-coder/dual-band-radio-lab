# Radio projects: context and continuation

Context reconciled on 2026-10-29 against main `e4d71d111b056971375157939a487d1ea16e754f` and the recovered October 28 planning artifacts. This is a documentation and artifact recovery update. It adds no hardware qualification.

## Where this repository fits

This repository owns the four-lane hardware investigation, its individual-radio development plan, and optional carrier designs. The wider communications question is how to carry essential commands, telemetry, state, occasional images, and possibly video across links with different service and airtime costs.

The most recent planning direction is to define the hardware and traffic before selecting a new routing implementation. Research has widened beyond a single radio family, fixed band, small antenna arrangement, or USB-first product. Larger nodes and custom RF work remain options. That broader investigation is recorded here as research; it does not turn an untested carrier into an accepted complete-node design.

The existing four-lane study retains a $150 complete-node target and $175 stretch ceiling. Those are design targets, not current supplier quotations or demonstrated assembled costs. Its four independent transceivers correspond to 915 MHz LoRa, 915 MHz FLRC, 2.4 GHz LoRa, and 2.4 GHz FLRC. A transceiver that supports both modulations still handles one selected profile at a time.

## Three hardware snapshots that must remain distinct

| Snapshot                                     | Controller and board                                                                       | Evidence and status                                                                                                                                                  | Start here                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Four-slot Rev A review platform              | Pico 2 carrier, 250 × 210 mm, three daughtercard designs including the E28 card used twice | Editable CAD and saved checks exist. Manufacturing hold remains. No fabrication package or physical qualification for this platform.                                 | [Hardware README](../hardware/README.md)                                     |
| Optional dual-LR2021 USB carrier             | ESP32-S3, 100 × 75 mm, two layers, direct Core2021-HF-M sockets, separate radio regulator  | Saved native KiCad checks and a prototype manufacturing ZIP exist. Firmware and laptop runner are unfinished. No fabricated or tested unit.                          | [Current optional carrier](../prototype/dual-lr2021-usb-carrier/README.md)   |
| Historical dual-LR2021 RP2040 review package | RP2040-Plus-M, 100 × 70 mm, four layers, separate SPI buses and switched radio supplies    | Generated CAD and manufacturing exports exist. Native KiCad import/ERC/DRC, socket mapping, power and physical checks were still open. This is not the ESP32 design. | [Historical archive and provenance](../archive/dual-lr2021-rp2040/README.md) |

The recovered `Dual_LR2021_AI_AGENT_HANDOFF.zip` referred to the **historical RP2040** board. It must not be used as the manufacturing package, GPIO map, or validation evidence for the ESP32 carrier. The immutable inner review package is now preserved in the historical archive directory. Original ordering instructions are historical context, not current procurement authorization.

No listed design establishes four simultaneous receive lanes during local transmission. Same-band receiver blanking, protection, isolation and desensitization still require evidence. Opposite-band concurrent operation also remains an experiment.

## Multiband analysis and Signal

[Signal](https://signal-radio-lab.drunken.chatgpt.site) is the interactive planning workspace. Its profile comparison and mesh sandbox are calculations, not recorded operation of a finished radio system. The October 28 analysis compared selected 915 MHz packet-radio/HaLow, 2.4 GHz packet-radio/Wi-Fi, and 5 GHz Wi-Fi profiles.

The [recovered analysis directory](../research/multiband/2026-10-28/README.md) contains the actual input JSON, derivation script, CSV, notes, assumptions, summary and PNG. Their original bytes are recorded in a SHA-256 manifest. The plot uses a frequency-normalized link-budget proxy and nominal rates. It excludes terrain, coexistence, receiver desensitization and many installation losses. It cannot establish a ten-kilometre brush link, application goodput, or a field handoff distance.

The historical notes propose a three-band starting architecture and example handoff thresholds. These are candidates and modeling assumptions. They are not a selected BOM, implemented protocol or test acceptance result. In particular, the note to build three nodes is a later validation idea; it does not replace the accepted [one-radio-at-a-time plan](staged-rollout.md).

The useful next traffic specification should state payload sizes, offered rates, deadlines, delivery requirements, burst sizes and loss/reconnect behavior. Measure delivered goodput, delay, retries, queue load, airtime and power for each candidate. A radio selection alone does not implement discovery, loop prevention, routing repair, priority or congestion control.

## Boundaries with the other radio work

- [Atlas Mesh](https://github.com/the-Drunken-coder/Atlas-Mesh) is the transport/routing experiment lab. Its measured Heltec timing and deterministic protocol comparisons do not qualify LR2021 or W12 hardware.
- [Atlas FieldLink](https://github.com/the-Drunken-coder/Atlas-FieldLink) implements application-message delivery over MeshCore. It does not supply the autonomous W12 firmware.
- [Meshtastic Lab](https://github.com/the-Drunken-coder/meshtastic-lab) runs native Meshtastic firmware in a controlled connectivity fixture. It does not predict field range.
- [Meshtastic workspace](https://github.com/the-Drunken-coder/meshtastic-workspace) preserves the earlier coordinated FLRC fork. The later standalone W12 Task 10C experiment is separate from that fork and is not imported into this hardware repository.

The fresh W12 continuation package remains separate. Its latest focused witness established topology-control forwarding without application offers; it did not pass the original application cold-start pair. Do not use that control witness as evidence of a deployable mesh.

## Resume from evidence

1. Confirm exact board revisions, condition, compatible peer counts and usable existing radios.
2. Use the isolated bring-up and logging gates in [staged rollout](staged-rollout.md).
3. Keep nominal specifications, saved software/CAD checks, conducted measurements and field measurements separately labeled.
4. Record the profile and firmware commit, packet accounting, test geometry, uncertainty and failed attempts with each result.
5. Revisit a custom carrier or combined node only when the measurements justify that specific integration step.

Current repository files remain authoritative for their respective designs. Source archives preserve their original limitations; importing a file or opening a PR does not close any engineering gate.
