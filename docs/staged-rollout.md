# Staged Radio Rollout

**Status:** Proposed experiments, not measured results or purchasing approval.

Keep the [four fixed-role transceiver architecture](dedicated-receiver-bank.md) as the long-term option. Start with the smallest experiment that can disprove the next assumption. A useful one- or two-lane system is a valid stopping point; four lanes must earn their cost, power and integration burden.

## Sequence and spending gates

| Level | Question | Smallest setup / spending gate |
| --- | --- | --- |
| 0. Inventory and safety | What can we safely test now? | Existing boards and documentation; verify counts and variants |
| 1. One working link | Can two nodes exchange packets reliably? | One compatible pair, one fixed profile, existing host/USB power |
| 2. Trust the measurements | Do the logs measure the link correctly? | Same pair plus offline log fixtures; no new radios |
| 3. Controlled PHY comparison | What does LoRa versus FLRC buy on the same platform? | Reuse one SX1280 pair sequentially; no four-radio build |
| 4. Stationary range | Where does the chosen profile become inadequate? | Same pair and a repeatable ground-level route |
| 5. Add one capability | Does another band or module solve that gap? | Borrow/reuse first; approve only the missing compatible peer(s) and safe fixture |
| 6. Co-location and coexistence | Can individually proven lanes share a node? | Two proven lanes per endpoint, integrated incrementally; four lanes only if justified |
| 7. Two-node failover | Does selection improve service over a fixed lane? | Existing dual-lane pair; no mesh or flight |
| 8. Deployment expansion | Does the result survive another node or motion? | Add one relay, mounting change or mobile platform per experiment |

The budget remains **$150 per complete node, $175 stretch**, not per RF module. Track sunk/owned hardware separately from new spend and projected complete-node cost (radios, host, antennas, power, battery and enclosure). Record reusable bench equipment separately without hiding it from total project spend. A gate opens a decision to approve a specific purchase, never an automatic order.

**Immediate scope:** inventory, one fixed-profile link and a trustworthy logger. No custom PCB fabrication, four-lane shopping list, high-power upgrade, shared antenna network or drone integration is needed for those answers. The [Rev A package](../hardware/README.md) remains a later integration candidate under its existing manufacturing hold; clean DRC/ERC is not RF or field qualification.

## Rules for every level

- Write one question and the acceptance limits **before** each run: packet count/duration, offered load, delivery/latency needs, allowable current/temperature and baseline repeatability. Limits are test requirements, not claimed measurements; leave no blank gate at execution time.
- Change one independent factor per comparison. Repeat A/B/A at a fixed setup and retain all runs, including failures. A drifted A invalidates the comparison; fix the setup before attributing an effect to B.
- Freeze board IDs/revisions, firmware/driver commit, complete profile, payload, send interval, retry/ACK policy, configured power, supply, antenna/cable, geometry and logger. Record unavoidable changes. A band/module swap is a **system comparison** with multiple coupled changes, not proof of a pure frequency effect.
- Start with one payload size, one offered load and no retries; test each direction separately. Add ACKs/retries, payload sweeps or load sweeps as their own follow-on factors. Do not run the Cartesian product of every setting. Expand only around a measured failure or useful tradeoff.
- Use an existing laptop/serial logger and board MCU first. Disable host Wi-Fi/Bluetooth for the baseline. No SBC, GUI, routing protocol, ranging mode or camera stream is needed to prove the packet path.
- End each level with one run folder: configuration, raw logs, small summary, pass/hold/stop decision and the next question. A failed gate means repair/repeat or narrow the goal; it does not authorize buying more capability.

### Electrical, RF and U.S. transmission gate

Apply this before the **first transmission**, including the bench, and repeat it whenever a profile, board, antenna, power path or installation changes:

1. Verify exact board revision, supply/current capability, logic levels, pinout, driver and PA/FEM controls against manufacturer documents. A library's generic radio example is not proof that an amplified board is configured safely. Check antenna frequency, connector/polarity and cable losses; never transmit into an open RF port.
2. Distinguish chip-drive setting from module connector output. On an amplified SX1280 board, a low software power number does not establish low radiated power. Respect the exact board's drive limits and measure or conservatively bound output before selecting attenuation or separation. Do not assume a switchable PA bypass exists.
3. Never cable TX directly into RX. A conducted fixture needs a verified loss budget, suitably rated attenuators/loads, correct impedance and any required DC blocking. Include startup/default output in the worst case; bound radio and instrument input against their damage and compression limits with margin. Use **board/front-end** limits, not just the bare chip's limit. If this cannot be established, stop RF testing and continue only non-transmitting bring-up/log work. Software packet blanking or an unpowered receiver is not proven front-end protection.
4. Before radiating, document the applicable U.S. rule basis and equipment authorization/integration basis for the exact hardware and use. Check permitted antenna type/gain, frequency, modulation/bandwidth, conducted output, EIRP, spectral density, unwanted emissions, applicable hopping/dwell requirements and RF exposure. A vendor's maximum-power claim, an ISM-band label or FCC marking on a different variant is insufficient. The default is TX disabled when this evidence is missing; a shielded/conducted setup also needs a justified containment/safety basis, not an assumed exemption.
5. Do not infer that all profiles can use 1 W. Keep only validated profiles/power limits available to the experiment and later selector. Bench success is not certification, and no legal maximum or guaranteed range is selected here. Stop for unsafe heating, supply faults, unexplained RF overload or harmful interference.

Manufacturer and FCC starting points are listed under [References](#references). Missing equipment/authorization evidence is a gate to resolve, not a reason to relax it.

## Level 0 — Inventory and a testable question

- **Hypothesis:** existing hardware can support one safe, compatible link without assembling a full node.
- **Minimum / cost trigger:** inventory the owned LILYGO T3-S3 SX1280 PA / “ranging2.4G” boards first. Count working units; record exact variant, antennas, cables and power sources. Do the same for any available Heltec V4 915 MHz LoRa boards. Neither an owned model nor a product listing proves that two matching units are available. With one board, do identification, non-transmitting driver checks and logger work; borrow or seek approval for only the missing compatible peer/fixture if needed.
- **Controls / changed factor:** no RF matrix yet. Select one practical traffic question, such as small telemetry packets, and one provisional fixed profile with documented driver support. The SX1280 pair is the first choice if verified; an already usable 915-LoRa pair is an acceptable fallback when it avoids a purchase. Record that choice before testing.
- **Matrix / metrics:** inventory each unit as identified / power-on checked / RF-ready / blocked; document costs and the first run's delivery, latency and power requirements. Resolve the electrical/RF and transmission gate above.
- **Exit / stop / deliverable:** exit with an inventory, one chosen pair/profile and a short wiring/safety/run card. Stop at non-transmitting work if a peer, safe setup or authorization basis is missing. Do not buy both bands merely to start.

## Level 1 — One fixed-profile two-node link

- **Hypothesis:** the selected pair can exchange known packets and return from TX to RX without resets or manual recovery.
- **Minimum / cost trigger:** the Level 0 pair, existing host/USB supplies and the validated RF arrangement. Buy only a proven missing cable, load or protection item after approval; no carrier PCB, enclosure or extra radio family.
- **Controls / changed factor:** freeze one profile, low validated module output, payload, interval and stationary geometry. Run A-to-B first, then B-to-A as the single direction change. Keep all other radios off. No automatic PHY changes, retries, routing or ranging.
- **Matrix / metrics:** repeat fixed-length runs in both directions; then test restart and TX-to-RX recovery separately. Capture sequence IDs, send/TX-done/receive events, CRC status where exposed, timeouts, reset count and supply/current observations. Label unmeasured electrical quantities rather than guessing.
- **Exit / stop / deliverable:** both directions meet the predeclared basic delivery/recovery limits on repeated runs; a cold restart reproduces the link. Keep the firmware/profile as the known-good baseline. Hold for mismatched settings, unstable supply, unexplained loss or unsafe input power; do not respond by increasing PA power.

## Level 2 — Validate measurement and logging

- **Hypothesis:** packet loss, throughput and latency reports reflect the experiment rather than counter, clock or serial-buffer errors.
- **Minimum / cost trigger:** same hardware; offline synthetic logs and existing host storage. Defer dedicated instrumentation unless a specific unmeasurable gate requires borrowing/renting it.
- **Controls / changed factor:** preserve the Level 1 link. Change only the injected log condition or offered load in separate runs. Test parser cases offline before intentionally dropping a packet in the live test.
- **Matrix / metrics:** fixtures cover missing, duplicate, reordered and corrupted records, sequence rollover, reboot/session boundaries and logger gaps. Reconcile queued, TX-completed, received and dropped counts. Check timestamp monotonicity and a known elapsed interval; run idle logging then the intended traffic rate to detect buffering/overflow.
- **Exit / stop / deliverable:** fixtures produce the exact expected counts, raw logs can recreate the summary, and repeated baseline results agree within the predeclared tolerance. Save the fixtures, log schema and analysis command. Hold if logs drop events or clocks are unexplained; no PHY/range conclusion is valid yet.

Use these definitions consistently from here onward:

- **Delivery:** unique valid payload IDs received / payload IDs transmitted, with the observation window and count shown. Separately report offered/queued packets, TX failures and host/logger drops so delivery cannot hide them. With retries, report attempt count separately and deduplicate payload IDs.
- **Goodput:** unique application payload bytes delivered per whole measurement interval, including time spent retrying or waiting. PHY bitrate is not goodput.
- **Latency:** RTT measured on one clock for a separately enabled echo/ACK test; report median, tail and timeout counts. Do not subtract unsynchronized node timestamps to claim one-way latency.
- **Energy and link quality:** report average/peak current and energy per delivered byte only where measured; otherwise mark unavailable. Log RSSI/SNR when supported, but do not compare unlike radio/PHY reports as calibrated signal measurements. Include run-to-run spread and sample count; short zero-loss runs do not prove a reliability target.

## Level 3 — Controlled LoRa / FLRC comparison

- **Hypothesis:** a different PHY/profile improves a specific throughput/latency/reliability tradeoff on the same 2.4 GHz platform.
- **Minimum / cost trigger:** reuse a verified SX1280 pair and its antennas sequentially. If Level 1 used 915-LoRa because no SX1280 pair is ready, defer this level until the minimal peer gap is justified; it is not a reason to purchase four lanes. SX1262 and LR1121 are not sub-GHz FLRC substitutes.
- **Controls / changed factor:** hold endpoints, geometry/path loss, payload, offered load, retries, firmware and characterized output fixed. Compare one explicit LoRa profile with one explicit FLRC profile as A/B/A. The profile is the factor: PHY-specific bandwidth/coding settings cannot all be identical, so list them and do not claim modulation alone caused the outcome. If legal/output limits differ, label that confound and compare feasible systems instead.
- **Matrix / metrics:** one short-path baseline per profile in each direction, then a separate attenuation or offered-load sweep only if needed. Report delivery, goodput, RTT in its separate echo test, airtime, timeouts and measured energy. Change LoRa SF, FLRC bitrate or any other tuning parameter one at a time only around a useful result.
- **Exit / stop / deliverable:** repeatable profiles and a small tradeoff table identify which to carry into the next experiment, or show no useful gain. Hold if the baseline drifts or the logger saturates. Unsupported FLRC firmware means a recorded blocker, not an unplanned driver/board migration mid-comparison. Sequential retuning here is a lab method, not a redesign of persistent receive lanes.

## Level 4 — Stationary single-link range

- **Hypothesis:** the selected fixed profile meets the chosen traffic need over a defined stationary path, or exposes a specific coverage gap.
- **Minimum / cost trigger:** same pair, repeatable ground-level sites and existing safe supplies. Use suitable stands/mounts if available; no drone, rooftop relay, camera or new band. Move to batteries in a separate near-range A/B/A check before relying on them outdoors.
- **Controls / changed factor:** use one profile per sweep. Change distance while keeping antenna height/orientation, power, mounting, traffic and endpoint roles fixed. Test an obstruction or body placement later as its own factor at a fixed location. Log site, time, weather and observed interference as uncontrolled context.
- **Matrix / metrics:** establish a near reference, increase distance through recorded stationary points, then return to the reference. Repeat questionable points and the route in a second pass; stop expansion once the predeclared delivery/latency limit fails. Capture packet counts, goodput, timeouts, current if measured and recovery after returning near.
- **Exit / stop / deliverable:** a route/setup-specific operating envelope and failure description, not a universal range promise. If one profile already meets the goal, stop expansion or test another goal. If references drift, batteries sag or conditions change, rerun; do not “fix” an unexplained result with a power/module upgrade.

## Level 5 — Add one band or hardware capability

- **Hypothesis:** one added capability solves the measured Level 3/4 gap enough to justify its incremental cost and integration burden.
- **Minimum / cost trigger:** first reuse an available compatible Heltec V4 pair for a separate 915-LoRa baseline. If incomplete, approve only the missing peer(s), matching antennas and necessary fixture. Qualify any new hardware through Levels 0–2, then repeat the relevant Level 4 route. Do not buy all four roles together.
- **Controls / changed factor:** compare the old complete link with the new complete link sequentially, with other radios off. Preserve traffic, endpoints, route and methodology; record unavoidable board, antenna, bandwidth and legal-power differences. This tests the value of the added system, not frequency in isolation. Never change band, driver, power, antenna height and routing policy silently in one run.
- **Matrix / metrics:** known-good old link / new link / old link on the reference setup, then the previously failing case. Compare delivered service, measured power, complete-node cost projection and integration effort. Investigate 915-FLRC/LR2021 or alternate 2.4 GHz modules only when the existing LoRa/FLRC options leave a named gap; repeat this level for each candidate.
- **Exit / stop / deliverable:** a short adopt/defer/reject decision with evidence, incremental parts cost and revised node budget. Hold if neither useful service nor measurement quality improves, compatibility/legal evidence is missing, or the complete-node projection exceeds the budget without a new decision. An unsupported lane can remain deferred while the useful link proceeds.

## Level 6 — Co-location and coexistence

- **Hypothesis:** separately proven lanes remain usable when co-located, without unsafe RF coupling, supply droop or host contention.
- **Minimum / cost trigger:** start with two proven opposite-band lanes per endpoint and separate antennas. A wanted-signal peer plus a safely controlled local aggressor is needed to measure desense; count those roles before assuming two bare radios suffice. Borrow fixtures/instruments or approve specific protection parts if coupling cannot otherwise be bounded. Do not populate four lanes yet.
- **Controls / changed factor:** first repeat each lane alone, then add the second board powered but RF-idle, then receiving, then serialized TX, as separate states. Freeze geometry, supply, driver version and wanted signal; vary only aggressor activity in each comparison. Shared power/host/SPI changes get their own regressions. Safety protection must be established before local TX, not discovered through overload.
- **Matrix / metrics:** wanted-link baseline versus local TX, in both band directions. Measure/bound coupled power, delivery loss, RX recovery/blackout time, supply/current and host errors. Only after safe serialized operation, separately test opposite-band simultaneous TX if it addresses a real requirement. Same-band TX/RX stays protected/blanked unless safe input levels and useful reception are demonstrated.
- **Exit / stop / deliverable:** a per-lane TX/RX/protection table with allowed power/geometry, measured blackout and a repeatable no-reset baseline. Freeze serialized TX if concurrency adds no useful benefit. Stop unsafe coupling or unexplained failures; add one mitigation at a time. The third/fourth fixed-role radio is purchased/populated only for an evidence-backed role within budget, passes Levels 0–2, and repeats these coexistence checks before four-lane RX coverage is claimed. Full radio count at both ends is not assumed.

## Level 7 — Two-node selection and failover

- **Hypothesis:** a simple selector improves delivery of the chosen traffic over the best fixed-lane baseline without oscillation or hidden loss.
- **Minimum / cost trigger:** the validated dual-lane setup and logger; no additional node or new RF hardware. Use fixed persistent profiles at the listeners. Automatic selection must obey Level 6's protection/scheduling table and validated TX limits.
- **Controls / changed factor:** replay deterministic logged/synthetic link states offline first. On the stationary bench, compare forced lane A, forced lane B and automatic policy against the same impairment schedule. Change only the policy; freeze thresholds before evaluating it. Introduce loss with controlled attenuation or software fault injection, not uncontrolled interference.
- **Matrix / metrics:** healthy links; active-link loss/recovery; both links unavailable; flapping; node restart, one case at a time. Report delivery, duplicates/order, queue drops, failover outage, tail RTT, recovery, switch count and energy if measured. Test essential traffic first; later add bulk bursts as a separate load factor so their backpressure is visible.
- **Exit / stop / deliverable:** a minimal policy/state diagram and traces showing bounded failure/recovery under the declared acceptance limits. Hold if the policy flaps, hides a dead link or performs worse than a fixed lane without a justified tradeoff. Keep manual selection as the usable fallback. Relay routing remains out of this two-node gate.

## Level 8 — Multi-node, mobile and field expansion

- **Hypothesis:** the qualified link/policy remains useful under one additional deployment constraint at a time.
- **Minimum / cost trigger:** add one node only for a justified stationary relay test, or reuse the proven pair for mobility. Approve a third node, battery/mount or platform integration only when that subtest needs it. Do not combine a new relay, enclosure, PHY and moving vehicle in the first field run.
- **Controls / changed factor:** separate subtests: (a) stationary three-node routing, (b) battery/enclosure/body mounting at fixed geometry, (c) person walking, (d) grounded UGV/drone/camera integration with platform electronics off then on, (e) controlled motion. Re-establish the reference after each accepted change. Defer Wi-Fi/Bluetooth coexistence to a separate off/on test after the radio-only baseline.
- **Matrix / metrics:** for routing, direct versus one fixed relay, then relay loss/restart: measure end-to-end goodput, latency, duplicates, hop count and queue/loop behavior. For mounting/motion, repeat a known route and log speed/orientation, outage, recovery, energy/runtime and temperature. For cameras, test representative traffic demand before promising usable video. Flight adds separate operational permission and safety gates; keep independent proven vehicle control/failsafe and do not rely on this experimental link for safety-critical control.
- **Exit / stop / deliverable:** a scoped field report for each accepted configuration and remaining limitations. Stop for uncontrolled changes, unsafe platform behavior, excessive thermal/power load or unmet service needs; fall back to the last validated setup. Only measured portability/isolation needs justify custom Rev A fabrication, shared antennas, filters/LNAs, higher-power hardware or a fifth TX, each as a new controlled experiment under existing release gates.

## Minimal run card

Keep this next to the raw log; one file per experiment is enough:

```text
Question / level / date / run IDs:
Hardware IDs and revisions / firmware + driver commit:
Complete RF profile / authorization and RF-safety record:
Supply / antenna + cable / geometry + site:
Fixed controls / single changed factor / unavoidable confounds:
Payload / offered load / ACK + retry policy / packet count + duration:
Predeclared service, safety and repeatability limits:
Baseline A / variant B / repeated A: raw log paths and metrics:
Failures, logger drops, measurement uncertainty and unmeasured items:
Decision: pass / hold / stop; next question and any proposed spend:
```

## References

- [LILYGO SX1280 PA board guide](https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series/blob/master/docs/en/t3_s3_sx1280pa/t3_s3_sx1280pa.md) and [factory board configuration](https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series/blob/master/examples/Factory/utilities.h): use the exact board/revision's PA limits and control wiring; pin the source revision in the Level 0 record.
- [Semtech LoRa Connect portfolio](https://www.semtech.com/products/wireless-rf/lora-connect): check supported bands/PHYs against the selected part's datasheet. A chip family does not establish board-level compatibility or authorization.
- [Heltec WiFi LoRa 32 V4 documentation](https://wiki.heltec.org/docs/devices/open-source-hardware/esp32-series/lora-32/wifi-lora-32-v4/): verify band, board revision and FEM/power variant independently before reusing its firmware or output assumptions.
- [FCC Part 15](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15): applicable operating conditions, equipment/antenna requirements and the specific transmission rule must all be resolved before radiating.
