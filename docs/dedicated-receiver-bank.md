# Dedicated Receiver Bank Architecture

**Status:** Proposed architecture for prototyping and evaluation

## Motivation

The current dual-band concept needs to support both LoRa and FLRC on both ~915 MHz and 2.4 GHz. A single transceiver can only be configured for one PHY/mode at a time, which creates a discovery and coordination problem: a node can be physically in range but fail to hear a packet because its radio is listening with the wrong PHY.

This proposal reduces that failure mode by separating reception from transmission and keeping a dedicated receive path assigned to each target band/PHY combination.

## Proposed Architecture

Use four inexpensive LR2021 modules as dedicated, continuously listening receivers and a fifth independent transceiver as the single agile transmitter.

```text
                         Host MCU / SBC
                              |
              +---------------+---------------+
              |                               |
          RX BANK                         AGILE TX
              |                               |
   +----------+----------+----------+          |
   |          |          |          |          |
   v          v          v          v          v
915 LoRa   915 FLRC   2.4 LoRa   2.4 FLRC   TX radio
   RX         RX          RX          RX      switches
                                           band / PHY
```

Nominal receiver assignments:

| Receiver | Band | PHY | Normal state |
|---|---|---|---|
| RX A | ~915 MHz | LoRa | Continuous RX on the canonical 915-LoRa rendezvous profile |
| RX B | ~915 MHz | FLRC | Continuous RX on the canonical 915-FLRC rendezvous profile |
| RX C | 2.4 GHz | LoRa | Continuous RX on the canonical 2.4-LoRa rendezvous profile |
| RX D | 2.4 GHz | FLRC | Continuous RX on the canonical 2.4-FLRC rendezvous profile |
| TX | ~915 MHz / 2.4 GHz | LoRa / FLRC | Changes as commanded; one transmission at a time |

The four receive paths are deliberately fixed most of the time. They remove band/PHY guessing only for the standardized rendezvous profiles described below; they do not decode every possible LoRa or FLRC configuration automatically.

## Rendezvous Profile Contract

Band and PHY alone are not enough to define a decodable link. Each receiver must be configured to a known network rendezvous profile, and transmitting nodes must use that same profile when they expect the dedicated listener to hear them.

The exact numeric profiles are intentionally not finalized yet, but the contract must define at least:

- center frequency / channel
- packet and synchronization settings
- expected bandwidth
- PHY-specific coding parameters
- LoRa spreading-factor behavior, including whether LR2021 Multi-SF reception is enabled and what SFs are covered
- LoRa sync word / header-mode assumptions as applicable
- FLRC bitrate, coding, sync-word, and packet-format assumptions as applicable

The initial architecture therefore means **four continuously monitored rendezvous profiles**, not four receivers capable of hearing arbitrary traffic anywhere in each band. Peers may move to other channels/profiles for data transfer after discovery, but returning to a known rendezvous profile must remain possible unless a later design adds scanning or additional parallel receive paths.

## Receiver Hardware Baseline

The intended receiver module is the **Waveshare Core2021-HF-M / Core2021-XF family based on the Semtech LR2021**:

- Product: https://www.waveshare.com/core2021-xf.htm?sku=34523
- Waveshare SKU **34523** = Core2021-HF-M
- LR2021-based transceiver module
- HF variant supports the required 850-930 MHz region and the 2.4 GHz ISM band
- Supports LoRa and FLRC
- SPI-controlled from an external MCU
- Can both receive and transmit; the four modules are assigned as receivers by firmware rather than being receiver-only hardware
- Header/module form factor is suitable for a low-cost bench prototype without designing the LR2021 RF section from scratch

The same Core2021-HF-M hardware can therefore be used for all four receive assignments. Separate 2.4-GHz-only receiver modules are not required.

### Cost constraint

The low-cost Waveshare LR2021 modules are part of the architecture, not just temporary development hardware.

The receiver bank is only attractive if four independent receive paths remain inexpensive. Moving the receiver bank to SDRs or substantially more expensive radio modules would likely push the project outside its intended per-node price range. Unless testing finds a fundamental limitation, the design should assume these inexpensive LR2021 modules remain the receiver implementation through later revisions.

At roughly the current ~$13/module price level, four receivers are about **$52**, and five identical modules would be about **$65** before the host, RF combining/switching, antennas, enclosure, and power hardware.

The fifth transmitter may initially be another identical Core2021-HF-M. The architecture does not require the transmitter to remain identical if a later specialized transmit path is justified without breaking the project budget.

## Shared Antennas

The four receivers do not necessarily require four external antennas.

A likely arrangement is one antenna per band, with each antenna feeding two receive paths through a proper 50-ohm two-way RF splitter:

```text
                915 MHz antenna
                       |
                  2-way splitter
                   /         \
                  v           v
             915 LoRa RX   915 FLRC RX

                2.4 GHz antenna
                       |
                  2-way splitter
                   /         \
                  v           v
             2.4 LoRa RX   2.4 FLRC RX
```

Two receive-only radios can share an antenna this way because neither receiver is intentionally transmitting energy into the other. A proper splitter with useful port-to-port isolation should be used rather than directly teeing two RF ports together.

The main passive penalty is the approximately 3 dB ideal power split, plus real insertion loss. This needs to be measured against the simplicity of having only two external receive antennas. If the loss is unacceptable, separate antennas or an LNA/filter ahead of the splitter can be evaluated later.

### LoRa and FLRC coexistence

The LoRa receiver and FLRC receiver on the same band can listen simultaneously. One receiver merely being configured for FLRC does not inherently disrupt the receiver configured for LoRa.

However, LoRa and FLRC transmissions are not automatically orthogonal. Two strong transmitters occupying the same or heavily overlapping RF channel can still interfere. The channel plan should therefore provide reasonable frequency separation between simultaneous LoRa and FLRC traffic when practical.

## Dedicated Transmitter

The current design uses **one agile transmitter**, independent of the four receive assignments. The host selects the transmit band and PHY based on destination, link state, traffic type, or routing policy.

Because there is one TX chain, 915 MHz and 2.4 GHz transmissions are serialized. **Simultaneous dual-band transmission is not a requirement for this prototype architecture.** The receiver bank can still monitor both bands simultaneously whenever local TX isolation permits.

The transmitter must have an RF/antenna arrangement capable of safely supporting both target bands, such as appropriate antenna switching, separate per-band antenna paths, or another validated dual-band arrangement. The fact that the LR2021 silicon supports both bands does not by itself make a single-band antenna suitable for both.

Example policy:

```text
Long-range / weak link       -> 915 LoRa
General-purpose sub-GHz      -> 915 FLRC
Robust short-range 2.4 GHz   -> 2.4 LoRa
High-rate burst              -> 2.4 FLRC
```

These mappings are intentionally not final. The purpose of the receiver-bank architecture is to make experimenting with and changing link-selection policy easier without sacrificing the standardized discovery paths.

## Why This Helps

With a conventional single agile radio:

```text
Node A transmits the canonical 915-FLRC rendezvous profile
Node B happens to be in 915-LoRa RX
-> packet is never detected
```

With the receiver bank:

```text
Node A transmits the canonical 915-FLRC rendezvous profile
RX B is permanently listening for that profile
-> packet is detected
-> host learns source / link information
-> dedicated TX answers using the selected band and PHY
```

This moves much of the problem from **PHY rendezvous/synchronization** into **link selection and routing**, while retaining a defined profile contract that both peers must follow.

## Host Interface

The LR2021 modules can share an SPI bus with individual chip-select lines, provided the final implementation also handles each radio's required interrupt/busy/control signals cleanly.

Conceptually:

```text
SCK  --------+----+----+----+----+
MOSI --------+----+----+----+----+
MISO --------+----+----+----+----+
             |    |    |    |    |
            RXA  RXB  RXC  RXD   TX

CS_A -------->|   |    |    |    |
CS_B ------------>|    |    |    |
CS_C ----------------->|    |    |
CS_D ---------------------->|    |
CS_TX -------------------------->|
```

The software should treat each receiver as an independent link-observation source and report at minimum:

- source/node ID after packet decode
- band
- PHY
- rendezvous profile ID
- channel/frequency
- RSSI
- SNR or equivalent quality information where available
- receive timestamp
- payload / packet metadata

This gives the routing/link-selection layer a continuously updated view of which standardized paths are actually working.

## Transmit/Receive Isolation

The largest RF risk is the node's own transmitter overwhelming the nearby receiver bank.

A same-band transmitter may be tens to more than one hundred decibels stronger at the local receiver input than a wanted distant signal. Software blanking can prevent packet processing during TX, but it does **not** protect the RF front end from excessive coupled power.

Likely approaches to investigate:

- RF switch between shared antenna path and TX path
- receiver blanking/muting during same-band TX
- limiter/protection components at receiver inputs
- physical antenna separation
- filtering between 915 MHz and 2.4 GHz subsystems
- shielding and careful board layout

Before any full-power local TX test, the prototype must establish either a validated protected RF path or a safely attenuated/conducted test arrangement. Initial characterization should begin at low power and verify coupled power at receiver inputs before increasing transmit power.

The first goal is **not** true same-band full duplex. It is to remain continuously aware of all four rendezvous profiles whenever the node is not actively transmitting, while minimizing how much of the receive bank must be blanked during TX.

## U.S. Transmission Validation Gate

The project requires license-free U.S. operation. Before over-the-air transmission is enabled on either band, the selected test configuration must be checked against the applicable FCC Part 15 requirements for that operating mode.

At minimum, the validation record should capture:

- intended frequency/channel
- occupied bandwidth / modulation configuration
- configured transmitter output power
- antenna type and gain
- resulting EIRP where relevant
- applicable spectral-density, out-of-band/spurious-emission, and other operating constraints for the selected rule basis

This architecture document does not attempt to select the final regulatory rule basis or certify compliance. It establishes a gate: automatic link selection must not choose an unvalidated transmit profile.

## Prototype Plan

### Phase 1 - Receiver bank proof of concept

- 4x Waveshare Core2021-HF-M modules, SKU 34523
- one host MCU/SBC
- define one temporary canonical rendezvous profile for each receiver:
  - 915 LoRa
  - 915 FLRC
  - 2.4 LoRa
  - 2.4 FLRC
- verify that packets on all four configured profiles can be detected without retuning the listeners
- initially use simple/separate antennas if that makes debugging easier

### Phase 2 - Shared-antenna evaluation

- add one proper two-way splitter for 915 MHz
- add one proper two-way splitter for 2.4 GHz
- quantify splitter insertion loss and receiver sensitivity impact
- test simultaneous LoRa/FLRC traffic at useful channel separations

### Phase 3 - Protected dedicated transmitter

- add a fifth independent LR2021 transceiver as the single agile TX
- establish receiver protection and TX/RX switching/blanking before live local TX characterization
- use a conducted/attenuated path or minimum-power test first and verify receiver-input coupling before increasing TX power
- complete the U.S. transmission validation gate for each transmit profile before normal over-the-air testing
- implement host-controlled band/PHY/profile selection
- characterize how TX affects all four receivers

### Phase 4 - Link-selection experiments

- track per-peer reception by band/PHY/profile
- test automatic PHY/band selection using only validated transmit profiles
- evaluate fallback behavior
- characterize latency, range, throughput, packet loss, and interference

## Open Questions

1. What exact rendezvous profile should be standardized for each band/PHY combination?
2. How much practical range is lost from the per-band two-way split?
3. How much channel separation is required for simultaneous LoRa and FLRC reception under realistic near/far conditions?
4. How badly does local TX desensitize the opposite-band receivers as well as the same-band receivers?
5. What minimum RF switching/limiting arrangement safely protects the receiver inputs?
6. Can one shared SPI bus service five LR2021s comfortably at the packet rates we care about?
7. What antenna-switching or dual-band arrangement should the single agile TX use?
8. Which traffic classes should prefer each of the four band/PHY combinations?

## Current Design Intent

This is a proposed architecture to test, not a claim that every RF detail is solved. The core design intent is:

> **Keep four inexpensive Core2021-HF-M/LR2021 receive paths continuously assigned to four standardized band/PHY rendezvous profiles, and use one separate agile transmitter so nodes do not become deaf simply because their only radio is listening in the wrong mode.**

The cost of the receiver bank is a first-order requirement. The design should prefer solving coexistence, antenna sharing, protection, and control problems around the inexpensive Core2021-HF-M modules rather than replacing them with substantially more expensive receiver hardware.
