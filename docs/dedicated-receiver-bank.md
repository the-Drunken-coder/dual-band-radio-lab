# Four Fixed-Role Transceiver Architecture

**Status:** Proposed architecture for prototyping and evaluation

## Motivation

The radio needs to support four persistent network lanes:

- ~915 MHz LoRa
- ~915 MHz FLRC
- 2.4 GHz LoRa
- 2.4 GHz FLRC

A design based on one or two agile radios creates a receive-coordination problem: a node can be physically in range but fail to hear a packet because its radio is configured for the wrong band or PHY at that moment.

The earlier proposal solved this with four dedicated receivers plus a separate agile transmitter. A simpler alternative is now the baseline under evaluation: use four independent transceivers, one permanently assigned to each lane. Each radio normally receives and temporarily switches to transmit only when the host needs to send on that same lane.

This preserves continuous receive coverage while removing the fifth radio and the need for an agile transmitter that switches between bands and PHYs.

## Proposed Architecture

```text
                           Host MCU / SBC
                                |
             +------------------+------------------+
             |                  |                  |
             |                  |                  |
             v                  v                  v
       915 MHz lanes        2.4 GHz lanes      control/software

     +---------------+     +---------------+
     |               |     |               |
     v               v     v               v
  915 LoRa        915 FLRC 2.4 LoRa      2.4 FLRC
  RX <-> TX        RX <-> TX RX <-> TX     RX <-> TX
     |               |        |               |
  antenna         antenna   antenna         antenna
```

Normal idle state:

```text
915 LoRa   = RX
915 FLRC   = RX
2.4 LoRa   = RX
2.4 FLRC   = RX
```

Example transmission on 915 MHz FLRC:

```text
915 LoRa   = RX or protected/blanked if required by local-TX coupling
915 FLRC   = TX
2.4 LoRa   = RX
2.4 FLRC   = RX
```

The important distinction is that a transceiver changes between **RX and TX**, not between network roles. The 915-LoRa radio remains the 915-LoRa radio; it does not retune to become the 2.4-FLRC radio later.

## Persistent Network Profile Contract

Band and PHY alone are not enough to define a decodable link. Each lane must use a standardized network profile so every node knows exactly what its dedicated listener is monitoring.

The exact numeric profiles are intentionally not finalized yet, but each profile must define at least:

- center frequency / channel
- packet and synchronization settings
- expected bandwidth
- PHY-specific coding parameters
- LoRa spreading-factor behavior and any supported multi-SF behavior
- LoRa sync word / header-mode assumptions as applicable
- FLRC bitrate, coding, sync-word, and packet-format assumptions as applicable

These are persistent network receive planes, not temporary discovery channels used to negotiate a later move. A sender chooses one of the four profiles and transmits into a receiver that is already listening there.

No listener negotiation or receiver retuning is required for normal communication.

## Why a Fifth Dedicated Transmitter May Be Unnecessary

The earlier architecture used four dedicated receivers plus one agile transmitter. That provided a clean conceptual split between ears and mouth, but it also duplicated hardware that the four receiver modules already contain.

If each lane uses a transceiver rather than a receiver-only device, the node already has four possible transmitters. A fifth radio is therefore not required unless testing finds a specific benefit such as:

- preserving same-lane reception while another radio transmits the same profile
- providing a specialized high-power or highly filtered transmit path that is difficult to integrate into the lane radios
- simplifying RF protection enough to justify the extra radio
- another measured performance advantage that outweighs cost, power, size, and control complexity

For the baseline prototype, none of those benefits is assumed.

## Role-Specific Hardware Instead of Four Identical LR2021s

The earlier design used Waveshare Core2021-HF-M / LR2021 modules for every receive path because one inexpensive radio could cover sub-GHz, 2.4 GHz, LoRa, and FLRC.

Once each radio is permanently assigned to one lane, that flexibility is no longer a first-order requirement. The hardware can instead be selected independently for each lane.

### Candidate direction

| Lane | Candidate hardware direction | Why it is interesting |
|---|---|---|
| ~915 MHz LoRa | high-power SX1262-based SPI module | mature sub-GHz LoRa ecosystem; 30 dBm / 1 W-capable modules exist; no need to pay for unused 2.4 GHz or FLRC support |
| ~915 MHz FLRC | LR2021-based module | sub-GHz FLRC is a distinctive LR2021 capability; standard and amplified/high-power module options can be evaluated |
| 2.4 GHz LoRa | high-power SX1280- or LR1121-based module | dedicated 2.4 GHz LoRa lane can prioritize sensitivity, output power, cost, and implementation simplicity |
| 2.4 GHz FLRC | high-power SX1280-based module or LR2021 | SX1280 is a mature 2.4 GHz FLRC/LoRa platform and amplified modules exist |

Specific examples worth evaluating include 30 dBm-class SX1262 modules for 915-LoRa and amplified SX1280 modules for the 2.4 GHz lanes. These examples are candidates, not commitments.

### Why the asymmetric design may be better

The four lanes do not have identical jobs:

- **915 LoRa** is likely to prioritize range, weak-signal performance, and reliability over raw throughput.
- **915 FLRC** is likely to prioritize a useful middle ground between sub-GHz propagation and much higher bitrate.
- **2.4 LoRa** can provide another robust lane with different propagation/interference behavior.
- **2.4 FLRC** is likely to prioritize high-rate short- or medium-range bursts.

There is therefore no requirement for equal output power, identical receiver sensitivity, identical module cost, or even the same transceiver family across all four lanes.

## Four-Antenna Baseline

The simplest first prototype may use one antenna per transceiver:

```text
915 LoRa radio  <-> 915 antenna A
915 FLRC radio  <-> 915 antenna B
2.4 LoRa radio  <-> 2.4 antenna C
2.4 FLRC radio  <-> 2.4 antenna D
```

This is physically less elegant than sharing one antenna per band, but it has major prototype advantages:

- no approximately 3 dB ideal passive splitter penalty
- no need to decide immediately how TX is routed through a shared receive splitter
- no RF combiner required just to make the prototype function
- each lane can be tested independently
- antenna-to-antenna coupling can be directly measured
- failures are easier to isolate during bring-up

The earlier shared-antenna approach remains a later optimization. Proper splitters, RF switches, duplexers, filters, LNAs, or other RF networks can be reconsidered after the four independent RF chains work.

## Transmission Concurrency

Four independent transceivers create more transmit possibilities than the earlier single-TX design.

### Opposite-band simultaneous TX

The architecture can potentially transmit on one 915 MHz lane and one 2.4 GHz lane at the same time because the RF chains are independent.

Example:

```text
915 LoRa   = TX
915 FLRC   = protected/blanked if necessary
2.4 LoRa   = RX or TX independently
2.4 FLRC   = RX or TX independently
```

This is a capability to test, not a guaranteed requirement.

### Same-band TX/RX

Same-band simultaneous TX/RX is much harder. A nearby transmitter can be enormously stronger than a desired remote packet and may desensitize or overload the other receiver on that band even when the two lanes use different PHYs or channels.

The baseline assumption should therefore be conservative:

> **When one lane transmits, the other receiver on the same band may need to be protected and temporarily blanked. Opposite-band receivers should remain active if measurements show sufficient isolation.**

True same-band simultaneous reception during local transmission is an optional later experiment, not a requirement for the architecture to succeed.

## Transmit/Receive Isolation

Local TX leakage is still the main RF risk, and using higher-power role-specific modules can make it worse.

Software blanking prevents packet processing but does **not** protect a receiver front end from excessive RF power. Before full-power local transmission, the prototype must use a safe test arrangement and characterize coupled power.

Mitigations to investigate include:

- physical antenna separation and orientation
- per-band filtering
- RF limiters or protection components
- hardware receiver blanking or shutdown during same-band TX
- shielding and careful board layout
- frequency separation between the LoRa and FLRC lane within a band
- reduced TX power when full output is unnecessary

Initial tests should begin at low output power or through a safely attenuated/conducted arrangement and increase power only after receiver-input coupling is understood.

## High-Power Hardware Is a Capability, Not a Regulatory Assumption

Role-specific radios make high-output-power modules attractive, especially for the long-range 915-LoRa lane. Modules capable of approximately 30 dBm / 1 W exist for several candidate chip families.

That does **not** mean every network profile may legally use 1 W.

The project requires license-free U.S. operation. Each actual transmit profile must be validated against the applicable FCC Part 15 rule basis before normal over-the-air use.

At minimum, the validation record should capture:

- intended frequency/channel
- occupied bandwidth and modulation configuration
- configured transmitter output power
- antenna type and gain
- resulting EIRP where relevant
- applicable spectral-density limits
- out-of-band/spurious-emission requirements
- any hopping, dwell-time, or other operating requirements that apply to the chosen rule basis

Firmware should treat the legal power limit as a property of the validated profile rather than automatically using the module's maximum hardware setting.

## Host Interface and Software Architecture

The move away from four identical LR2021s means software should not assume one common radio driver.

A better abstraction is:

```text
                  host routing/link-selection layer
                              |
                 common radio-lane interface
                              |
        +----------+----------+----------+----------+
        |          |          |          |          |
     SX126x     LR2021      SX128x      SX128x/
      driver     driver      driver       other
```

Each lane should expose common operations such as:

- enter RX for its configured profile
- transmit packet
- report RX/TX state
- report RSSI/SNR or equivalent quality information
- report receive timestamp
- report packet metadata
- set validated TX power for that profile
- report faults or busy state

SPI can still be shared where electrical requirements and device timing permit, with independent chip-select and interrupt/busy/control lines. Mixed radio families simply require separate low-level drivers behind the common lane abstraction.

## Prototype Plan

### Phase 1 - Four independent receive lanes

- select one candidate module for each of the four lanes
- use one antenna per radio initially
- define one temporary canonical network profile per lane
- verify all four receivers can remain active simultaneously
- verify shared host/SPI/control wiring is reliable with the mixed radio set
- log receive quality and packet metadata independently per lane

### Phase 2 - Per-lane transmission

- enable TX on each lane at minimum power first
- verify that each transceiver can switch RX -> TX -> RX reliably without changing network role
- measure local-TX coupling into the other three receivers
- determine which receivers must be protected or blanked for each transmission case
- increase TX power only after safe coupling levels are established

### Phase 3 - Concurrent operation

- test whether opposite-band receivers remain useful during local TX
- test simultaneous 915 MHz and 2.4 GHz transmissions
- measure packet loss, desense, recovery time, and RF interaction
- experimentally test same-band simultaneous TX/RX only if isolation measurements justify it

### Phase 4 - Hardware optimization

- compare four antennas against shared-antenna alternatives
- evaluate whether an LNA is useful on any receive lane
- evaluate filters, duplexers, switches, or limiters where measurements justify them
- compare standard-power and high-power module options
- revisit whether a fifth dedicated transmitter provides any measured advantage

### Phase 5 - Link-selection experiments

- track per-peer reception by lane
- choose an outgoing lane based on traffic type and observed link state
- implement fallback behavior
- characterize latency, range, throughput, packet loss, interference, and power consumption

## Open Questions

1. What exact network profile should be standardized for each of the four lanes?
2. Which specific module is the best candidate for each lane within the node budget?
3. How much same-band receiver desense occurs when its neighboring lane transmits at practical power levels?
4. Can the 915 MHz and 2.4 GHz systems transmit simultaneously without materially degrading each other?
5. How much antenna separation is required in a walkie-talkie-sized enclosure?
6. Which lanes actually benefit from 27-30 dBm hardware once legal profile limits and battery cost are included?
7. Is a high-power LR2021 worthwhile for 915-FLRC, or is the standard-power version sufficient?
8. Does 2.4-LoRa benefit enough from an amplified SX1280/LR1121 implementation to justify its power draw?
9. Can mixed radio families share one SPI bus comfortably, or is splitting the buses cleaner for the final host?
10. Does a later shared-antenna design save enough size to justify its splitter/switch/filter complexity and receive loss?
11. After testing the four-transceiver design, is there any remaining reason to add a fifth dedicated TX radio?

## Current Design Intent

This is a proposed architecture to test, not a claim that every RF detail is solved. The current design direction is:

> **Use four persistent, fixed-role transceivers: 915-LoRa, 915-FLRC, 2.4-LoRa, and 2.4-FLRC. Keep all four in RX during normal idle operation, and let the appropriate lane temporarily transmit without retuning to another network role. Select the best practical hardware independently for each lane instead of forcing all four lanes onto LR2021.**

The first prototype should favor simple, independently testable RF chains over aggressive antenna sharing or same-band full-duplex operation. High-power hardware, LNAs, filters, shared antennas, and additional transmitters should be added only when measurements show that they improve the system enough to justify their cost, power, and RF complexity.
