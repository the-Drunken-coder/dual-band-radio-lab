# Develop Each Radio Independently

**Status:** Proposed test plan; no measured performance or purchase approval.

The unit of work is **one radio lane**, characterized in isolation with a compatible peer. Complete its small bring-up ladder, record what it can do, then move to the next radio. This is not a staged deployment of the entire network. The [four fixed-role architecture](dedicated-receiver-bank.md) remains the eventual integration option.

## Hardware order and purchase gates

| Order | Radio to characterize | Minimum starting hardware | Spend only when |
| --- | --- | --- | --- |
| 1 | 2.4 GHz LoRa | Owned LILYGO T3-S3 SX1280 PA / “ranging2.4G” boards, after inventory | A compatible peer or safe fixture is missing |
| 2 | 2.4 GHz FLRC | Reuse the same SX1280 boards, reconfigured between isolated tests | Existing boards/driver cannot answer a documented FLRC question |
| 3 | ~915 MHz LoRa | Available Heltec V4 915-LoRa boards, if inventory confirms them | A missing peer or measured limitation justifies a specific part |
| 4 | ~915 MHz FLRC | A suitable 915-FLRC evaluation setup; LR2021 is a candidate | Its distinct test question, driver support, RF path and total peer/fixture cost are understood |

Counts, condition and board revisions are unverified. One board permits non-transmitting bring-up; link testing needs a compatible peer. A 2.4 GHz board cannot be a 915 MHz peer. Borrow/reuse first. A ready 915-LoRa pair can move ahead if it avoids spending; another owned radio can be characterized even if the first succeeds.

Use one pair at a time, with other radios and host Wi-Fi/Bluetooth off. Reuse fixtures/software but keep results separate per radio/profile. Sequential SX1280 reuse avoids duplication; it does **not** demonstrate simultaneous LoRa/FLRC reception or change the final fixed-role design.

Budget: **$150 per complete node / $175 stretch**. Track owned parts, new spend, bench equipment and projected complete-node cost. No four-radio order, power upgrade or custom PCB is needed to begin. The [Rev A manufacturing hold](../hardware/README.md) remains. Candidates are unselected; purchases require approval.

## Shared procedure, used by each radio

1. **Identify without TX.** Record board/revision, RF part/FEM, supply/current capability, logic levels, pinout and firmware/driver commit. Verify reset, SPI/identity, IRQ/busy and RF-path controls. Start with the board MCU and serial logger.
2. **Clear the gates below.** Freeze the complete supported profile, low validated connector output and safe geometry. Match channel, synchronization, packet and PHY settings at both endpoints. Generic chip examples do not establish amplified-board safety.
3. **Establish a known-good pair.** Fixed payload/interval, no retries; A-to-B then B-to-A separately. Check TX completion, reception, TX-to-RX return and cold restart. Preserve working firmware/profile.
4. **Validate logging.** Offline fixtures cover missing, duplicate, reordered/corrupt records, rollover and reboot/session boundaries. Reconcile offered, TX-completed and received IDs; detect logger gaps/overflow and verify elapsed time. Repeat at intended load. Logging failure blocks performance conclusions.
5. **Change one factor.** Declare packet count/duration, service limits and repeatability tolerance first. Run baseline/variant/baseline; fix hardware, firmware, output, antenna/cable, geometry, payload, interval and retries except the named factor. Label coupled changes as a profile comparison. Avoid exhaustive combinations.

Measure delivery (unique valid received payloads / transmitted payloads), application goodput over the whole run, timeouts and reset/recovery. Report offered-packet/TX/logger drops, sample counts and run-to-run spread. A separate echo test measures RTT on one clock; do not infer one-way latency from unsynchronized clocks. RSSI/SNR across unlike PHYs/chips is not a calibrated comparison. Measure current/temperature/energy where possible; mark unavailable quantities.

Each step requires its declared limits and repeatable baseline. Save raw logs and a pass/hold/stop note. On failure, restore the known-good profile and isolate the fault before adding capability.

### Electrical, RF and U.S. transmission gates

- Verify matching band/connector/antenna and the exact board's PA/FEM controls. Never transmit into an open RF port. **Chip drive is not module output:** the SX1280 PA's minimum software power does not establish safe antenna-port power. Respect board-specific drive limits; measure or conservatively bound output, including startup/default states. Do not assume PA bypass exists.
- Never connect TX directly to RX or a test instrument. Use a verified loss budget and correctly rated attenuators/loads, impedance and any required DC blocking. Bound input below damage and compression limits with margin using the **board/front-end** and instrument limits, not just the bare chip. Software blanking or an unpowered receiver is not proven RF protection. If the safe arrangement cannot be established, stay with non-transmitting work.
- Before radiating, document the exact hardware's U.S. rule and equipment-authorization/integration basis, antenna type/gain, frequency, modulation/bandwidth, output/EIRP, spectral density, unwanted emissions, applicable hopping/dwell conditions and RF exposure. ISM-band labels, a nominal power cap or another variant's FCC marking are insufficient. A shielded/conducted test also needs a justified containment/safety basis. Keep TX disabled when evidence is missing; do not infer that every profile may use 1 W.
- Reopen these gates for a changed profile, board, PA setting, antenna or installation. Stop for unsafe heating, supply faults, unexplained overload or harmful interference. These experiments do not certify compliance or establish a legal maximum.

## Radio A — 2.4 GHz LoRa

**Question:** What reliable payload/airtime/range envelope can the owned SX1280 PA hardware deliver in LoRa mode?

**Hardware gate:** use a compatible SX1280 pair if inventory confirms one; otherwise resolve only the missing peer/fixture. Keep ranging disabled despite the “ranging2.4G” label. LR1121 or another module remains a later candidate.

| Step | Test and single changed factor | Evidence to advance / stop |
| --- | --- | --- |
| A1. Identify and link | Run the shared procedure in LoRa mode with one fixed spreading factor, bandwidth, coding and packet format; reverse direction as a separate run | Save a repeatable bidirectional baseline with correct TX-to-RX/restart behavior; hold on PA control, supply, sync/header or logger faults |
| A2. LoRa profile | At fixed path loss and offered load, change spreading factor only; test bandwidth separately only if a useful question remains | Record delivery, airtime, goodput and echo RTT against the declared limits; retain a small set of useful profiles rather than all combinations |
| A3. Load and power | First change offered load at a fixed profile; then, only if needed and safely characterized, test output settings with load fixed | Separate airtime saturation from RF loss; record current/temperature where measured. Hold on overflow, resets or unexplained output behavior; more PA drive is not a default fix |
| A4. Single-link range | With one qualified profile/output, change stationary distance; return to a near reference. Test obstruction or orientation separately | Produce a route/setup-specific operating envelope and recovery result. Reject a sweep if the reference drifts; do not claim universal range |

**Deliverable / next spend:** one LoRa capability card with working configuration, logs, limits and unresolved issues. Consider another 2.4-LoRa module only for a named deficit that tuning or the fixture cannot explain; requalify the replacement independently.

## Radio B — 2.4 GHz FLRC

**Question:** What sustainable application goodput and latency can FLRC provide on those same SX1280 boards?

**Hardware gate:** reuse the compatible SX1280 pair qualified for Radio A; preserve its known-good state and confirm FLRC driver support. No second 2.4 GHz radio per node is needed. LR2021 or alternate SX1280 modules remain optional candidates.

| Step | Test and single changed factor | Evidence to advance / stop |
| --- | --- | --- |
| B1. Independent FLRC link | Apply the shared procedure to one supported FLRC profile: bitrate/bandwidth combination, coding, sync word and packet/CRC settings | Save a repeatable FLRC link and TX-to-RX/restart result. If the driver cannot configure it correctly, record the blocker; do not assume LoRa success proves FLRC support |
| B2. Feed the radio | At the fixed profile, raise offered load only; log queued, TX-completed and received IDs plus host/serial drops | Establish sustainable application goodput and queue/timeout behavior. Fix a host/logger bottleneck before attributing the ceiling to RF |
| B3. FLRC profile | Compare one supported bitrate profile at a time; hold bandwidth fixed where supported, otherwise record the coupled profile change. Evaluate coding separately if needed | Carry forward a useful delivery/goodput/RTT tradeoff. Revalidate power/authorization assumptions for each profile; PHY bitrate alone is not a result |
| B4. Link margin | At fixed profile/load/output, change attenuation or stationary distance in separate sweeps; check recovery after returning to baseline | Save the usable operating envelope and failure/recovery behavior. An optional comparison with Radio A uses the same hardware/route and records differing PHY settings; it is not a pure modulation-only experiment |

**Deliverable / next spend:** a FLRC capability card distinct from Radio A's. Buy alternate hardware only after identifying a radio/driver limitation that the existing pair cannot resolve, rather than a logging or host-load limit.

## Radio C — ~915 MHz LoRa

**Question:** What low-rate delivery, airtime, power and range tradeoffs does the available 915-LoRa radio provide by itself?

**Hardware gate:** inventory any available Heltec V4 915 MHz boards and verify their revision and FEM/output variant. Use a compatible peer with a matched profile; borrow or propose only the missing peer/fixture. High-power SX1262 modules remain candidates, not required starting parts. SX1262 does not provide FLRC.

| Step | Test and single changed factor | Evidence to advance / stop |
| --- | --- | --- |
| C1. Identify and link | Run the shared procedure with 915 hardware/antennas and a single legal-to-test LoRa profile; leave the 2.4 GHz pair off | Save a stable link, reset/TX-to-RX behavior and correct FEM/supply setup. Do not copy SX1280 registers, output assumptions or profile numbers blindly |
| C2. LoRa profile | At fixed path loss/output/load, change spreading factor only; examine bandwidth or coding in separate follow-on tests | Record delivery versus airtime, goodput and RTT. Advance only useful profiles; hold if timing, occupied-bandwidth eligibility or baseline repeatability is unresolved |
| C3. Power and duty | Hold the profile and packet schedule fixed while testing one validated output setting at a time; separately vary send interval for the intended traffic | Characterize measured current, heating, supply droop and delivered service. Stop before exceeding electrical/RF limits; a 1 W-capable module is not permission or a reason to use 1 W |
| C4. Single-link range | Freeze profile/output/mounting and repeat stationary distance points, with near-reference checks; test obstructions separately | Produce this radio's own route-specific envelope and recovery record. Cross-band results include antenna/hardware/profile differences and cannot isolate frequency alone |

**Deliverable / next spend:** a 915-LoRa capability card and an evidence-backed decision on whether more output or a different SX1262 module is useful within the node budget. Do not purchase that upgrade before the baseline identifies its purpose.

## Radio D — ~915 MHz FLRC

**Question:** Does a suitable sub-GHz FLRC radio provide a useful intermediate rate/range option worth its additional hardware and driver effort?

**Hardware gate:** this is a separate capability investigation. SX1280 is a 2.4 GHz radio; neither SX1262 nor LR1121 substitutes for 915-FLRC. LR2021 is a candidate, not a selected purchase. Before acquiring anything, verify the exact module's 915 RF path, antenna/PA arrangement, usable FLRC driver/example, supply/interface needs and transmission basis. Cost the **complete compatible test link**, including a peer and fixtures; approve the smallest evaluation setup, not four modules or a carrier.

| Step | Test and single changed factor | Evidence to advance / stop |
| --- | --- | --- |
| D1. No-TX bring-up | On one selected evaluation board, verify identity/reset/SPI/busy/IRQ and 915 RF-path/FEM control; validate that firmware exposes the intended sub-GHz FLRC configuration | Advance only with documented board/driver/profile support. Hold or defer the lane if the implementation or safe output cannot be verified; a chip feature list is not a working module |
| D2. One FLRC link | Add a compatible peer and run the shared procedure at one fixed supported FLRC profile and characterized low output | Save repeatable packets, TX-to-RX and cold-restart behavior. Keep other radios off; solve pinout, clock, packet-format or driver faults before any rate/range tuning |
| D3. Rate and load | Compare supported bitrate profiles one at a time with coupled bandwidth changes identified; test offered-load saturation separately | Record actual goodput, delivery, RTT, host drops and measured power. Carry forward a small usable profile set, or defer if the added rate does not serve the test goal |
| D4. Margin and value | At one qualified profile, sweep stationary distance/path loss; compare to Radio C's reference route only after this radio passes independently | Record its own operating envelope and recovery. Evaluate service gain against incremental cost/power/driver complexity; do not attribute all cross-radio differences to the PHY |

**Deliverable / next spend:** a 915-FLRC capability card with proceed/defer/reject evidence. If the minimal evaluation cannot be justified, document the gap and leave this lane unbuilt; the other three radios can still be characterized. Higher-power LR2021 hardware requires a separate measured need and renewed gates.

## One capability card per radio

Keep this compact record with the raw logs:

```text
Radio / board IDs + revision / peer / firmware + driver commit:
Working complete profile / output setting and characterization:
RF-safety + transmission eligibility evidence / supply / antenna / fixture:
Question / one changed factor / fixed controls / unavoidable confounds:
Predeclared packet count + duration / acceptance + repeatability limits:
Baseline–variant–baseline logs / delivery / goodput / RTT + timeouts:
Measured current + temperature / unmeasured quantities / failure + recovery:
Decision: pass / hold / defer; known limitations / specific next test or spend:
```

## Only afterward: combined-node work

Select independently qualified radios whose capability cards justify a useful role within budget. Integrate two first, re-running each isolated baseline after each host/SPI, supply or mounting change. Establish hardware protection and safe coupled-input levels before local TX; start serialized, measure desense/blackout/recovery, and add simultaneous or same-band operation only if justified. Count the wanted-signal peers and aggressor radios needed for those tests rather than assuming the individual test pair covers every role.

Four-lane receive coverage, antenna sharing, higher power, failover/routing, relays, Wi-Fi/Bluetooth coexistence and person/drone/UGV/camera deployment are later integration questions. They are outside these individual-radio ladders and do not hold up a useful isolated-radio result. Custom Rev A fabrication remains subject to its existing release gates.

## References

- [LILYGO SX1280 PA board guide](https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series/blob/master/docs/en/t3_s3_sx1280pa/t3_s3_sx1280pa.md) and [factory board configuration](https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series/blob/master/examples/Factory/utilities.h): verify exact-revision PA limits and control wiring; pin the source revision in the test record.
- [Semtech LoRa Connect portfolio](https://www.semtech.com/products/wireless-rf/lora-connect): verify band/PHY support against the selected part's datasheet; chip capability does not establish board compatibility or authorization.
- [Heltec WiFi LoRa 32 V4 documentation](https://wiki.heltec.org/docs/devices/open-source-hardware/esp32-series/lora-32/wifi-lora-32-v4/): verify band, revision and FEM/output variant.
- [FCC Part 15](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15): resolve applicable operating, equipment/antenna and transmission requirements before radiating.
