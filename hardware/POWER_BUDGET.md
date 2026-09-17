# Rev A power budget and architecture

Design target: **regulated 5 V, at least 4 A continuous at the carrier input**. Specify 5 V +/-2% at the source, a short 18 AWG or larger pair, and at least 4.75 V at J9 under load. The connector/protection/main copper are sized for 4 A continuous and the roughly 5.13 A upper current-limit bound. All calculations are design bounds, not measurements.

## Power path

J9 is Phoenix Contact 1757242, 12 A, with 1757019 mating plug. Pin 1 is external +5 V, pin 2 ground. U2 TPS259470LRPWR protects the radio bus against reverse polarity, reverse current, overcurrent, undervoltage and overvoltage, and controls inrush. This electronic fuse is the selected fuse/protection implementation; no unselected fuse placeholder remains. Use a current-limited external supply.

Q1 DMG2305UX-7 follows Pico 2 datasheet section 5.5, figure 9: **gate = USB VBUS, source = Pico VSYS, drain = protected RADIO_5V**. Its body diode points from external power toward VSYS. This apparently reversed source/drain arrangement is intentional. R7 discharges the VBUS gate when USB is absent. Pico's onboard D1 supplies VSYS from USB and blocks external VSYS from backfeeding USB.

| State | Pico | RADIO_5V and IOREF_3V3 | Isolation |
| --- | --- | --- | --- |
| USB only | Powered through onboard D1 | Off, apart from bounded device leakage | Q1 off; reverse body diode blocks VSYS-to-radio current; translators isolate absent VCCB |
| External only | Powered through Q1 | Powered through U2 | Q1 on; onboard D1 reverse-biased |
| USB and external | Powered from ORed inputs | Powered exclusively from external input | Q1 channel may be off; external body-diode path and USB D1 share according to actual voltages; neither source is directly tied to USB |
| Pico held/reset or 3V3 disabled, external on | GPIO domain inactive/off | Radio domain powered | OE pull-up disables U5/U6; VCCA isolation handles the unpowered case; GP26-28 physically NC |
| Both removed | Discharges | Discharges through R11/R12 and loads | No battery or independent daughtercard power allowed |

U3 creates IOREF_3V3 only from RADIO_5V. It powers the expander and radio side of U5-U7. No Pico 3.3 V supply crosses onto a daughtercard. R11/R12 provide 1 kohm rail bleeders. Off does not mean mathematical zero leakage: Q1 and translators have specified leakage, discharged by the bleeders. USB-only operation cannot provide a usable radio supply. Verify leakage and USB-source isolation during hardware acceptance. No external voltage may be injected into VSYS, IOREF or daughtercard outputs outside these power states.

## Continuous input allocation

Manufacturer E22 table: 500-620 mA at 30 dBm; use 650 mA nominal budget and 850 mA design reserve. E28: 580 mA typical at 3.3 V, with 30% current margin recommended; reserve **1 A per local 3.3 V regulator**, greater than 754 mA. Core: chip-level 105 mA nominal, reserve 150 mA for the module. Pico reserve is an input-current allocation, not a measured maximum.

| Load | Conservative basis | External current |
| --- | --- | ---: |
| E22 | Direct 5 V load | 0.850 A |
| E28, each | 3.3 V x 1 A / 80% efficiency / 4.4 V protected bus | 0.9375 A |
| Two E28 | Both at the preceding bound | 1.875 A |
| Core and LDO | 150 mA allocation | 0.150 A |
| Pico, including its conversion losses | VSYS input reserve | 0.300 A |
| Expander, translators, bleeders and regulator overhead | Engineering reserve | 0.050 A |
| Total | All four RF loads budgeted simultaneously | **3.225 A** |

At 5.1 V input this conservatively combines to **16.45 W**, below the 20.4 W available from a 5.1 V / 4 A source, with 0.775 A current headroom. Nominal operation using 650 mA E22, 580 mA each E28 at 85% efficiency, 105 mA Core and 150 mA Pico/logic is about 1.81 A at 5 V. The 80% efficiency bound is an engineering allowance to be measured on the eventual layout. Electrical budgeting does not authorize simultaneous same-band TX/RX.

U2 maximum on-resistance is 45 milliohms. At 4 A its drop is 0.18 V and dissipation 0.72 W. A minimum 4.75 V connector input leaves 4.57 V before copper/slot losses; 4.4 V is the budget floor at each buck. AP63203 needs at least 3.8 V. E22 remains above its stricter 3.3 V operating minimum, but its manual's full-power requirement is >=5 V at the module. **Exactly 5 V at J9 does not guarantee full 30 dBm after losses.** Do not raise input above its specified range to hide that limitation.

## Protection values

- R1/R2 = 267 kohm / 100 kohm, 1%: nominal UVLO rising threshold 4.404 V using the 1.2 V comparator. Comparator and resistor tolerances give approximately 4.28-4.56 V before leakage.
- R3/R4 = 340 kohm / 100 kohm, 0.1%: nominal OVLO 5.28 V; approximately 5.20-5.39 V including comparator/resistor allowance. The 5.1 V maximum normal input stays below the lowest threshold; E22's 5.5 V maximum remains the stricter steady-state ceiling. Fast input spikes and turn-off overshoot require bench verification.
- R5 = 715 ohm, 1%: nominal limit 3334/715 = 4.66 A. Scaling the datasheet's 750-ohm limits and including resistor tolerance gives approximately 4.11-5.13 A. This retains 4 A service while remaining below U2's 5.5 A continuous rating. It is a conservative interpolation of the specified current-limit law, not a separate guaranteed 715-ohm production test. The datasheet's UL-recognition condition RILM>=750 ohm is not met; no UL-recognition claim is made for this design.
- ITIMER open selects the documented minimum fault response; AUXOFF and FLT are unused. TPS259470L is the latch-off active-current-limit variant. A persistent overload must not be handled by firmware retries.

## Inrush and capacitance

C1=10 nF with R19=100 ohm in series sets nominal slew rate 2000/10000 = **0.2 V/ms**, about **25 ms** to 5 V per TI equation 4. C1 tolerance alone gives 22.5-27.5 ms; the formula is typical and does not bound every IC process corner. The series resistor follows TI's recommendation for capacitance above 10 nF, covering C1's positive tolerance. All radio bulk is after U2; the connector sees only 1 uF of deliberate carrier input bypass before it.

There are four 220 uF bulk capacitors in the assembled four-slot system, 880 uF nominal / 1056 uF at +20%. Selected TDK 22 uF capacitors total 352 uF nominal across carrier and all daughtercards / 422.4 uF at +20%. Counting downstream 3.3 V capacitors as if they charge directly at 5 V is conservative at this voltage and efficiency. Add a 120 uF allowance for Pico, module-internal and small bypass capacitance: **1.60 mF** rounded design bound.

At 0.2 V/ms, capacitive inrush is 0.32 A. Use twice this slew rate as a stress case, giving **0.64 A**. Combined with the entire 3.225 A running allocation it is 3.865 A, below 4 A. Actual startup must keep TX disabled for 100 ms; standby/reset draw is substantially below the all-TX allocation. Stored-energy upper bound is 0.5 x 1.6 mF x 5.1 V squared = **20.8 mJ**. The ramp stress case is an engineering design check, not a guaranteed device maximum; measure startup with the selected supply and all four cards before fabrication release can become a qualified assembly release.

E28 uses 2x22 uF at its buck input and 3x22 uF at its output. The 4.7 uH XAL5030-472MEC has 6.7 A saturation rating, 40 milliohm maximum DCR and exceeds the regulator's current-margin guidance. AP63203 allows 2.2-10 uH; 4.7 uH is a deliberate supported departure from the 3.9 uH example. The selected 25 V, 20% X7R ceramics have ample voltage rating. With a combined 50% retention allowance for DC bias and aging, plus 20% initial tolerance and 15% temperature loss, effective output is 66 x .8 x .5 x .85 = **22.44 uF**; input is **14.96 uF**. The combined 50% retention is a conservative design allowance, not a manufacturer-guaranteed curve. Confirm it by characterization or measurement for the purchased lot; no interchangeable smaller-package substitution is allowed. The LDO output networks exceed their 1 uF minimum by a large margin.

Panasonic EEEFK1A221P is 220 uF, 10 V, +/-20%, maximum 0.26 ohm impedance at 100 kHz, 300 mA ripple rating. A 650 mA, 100 us E22 step gives 0.369 V ideal droop at 176 uF plus up to roughly 0.169 V using that impedance as an ESR estimate. Ceramics shunt fast edges; the supply must carry sustained TX. Qualification must check actual ripple current and voltage at the module.

## Copper and thermal requirements for the later layout

Rev A does not optimize for size. Use generous power pours and keep the four slots spread out. The dimensions below are minimums; increase copper area where space permits and recalculate voltage drop for the actual route lengths. Keep local switcher loops compact and provide accessible power/ground measurements as specified in [LAYOUT_REQUIREMENTS.md](LAYOUT_REQUIREMENTS.md).

Use two layers with **2 oz finished copper on both sides**, a continuous ground plane and power pours. Main 5 V and its ground return must each have at least **4 mm uninterrupted width**, with no thermal-relief bottleneck at J9 or U2 power connections. For a 100 mm run and 70 um copper, R=0.01724 x 0.1/(4 x .070)=6.16 milliohms at 20 C. At 60 C this becomes 7.13 milliohms, 28.5 mV drop and 114 mW at 4 A per conductor. Budget both outgoing and return paths. Where a layer change is unavoidable use at least eight 0.30 mm finished vias with >=25 um barrel copper; 0.5 A per via at 4 A. Each slot's supply branch needs >=1.5 mm width and both +5 V contacts. Recalculate for actual lengths and fabricator copper tolerances; these are requirements, not claims about nonexistent copper.

Design ambient is 0-40 C for the first bench prototype. U2's test-board 74.5 C/W estimate gives 54 C rise at 4 A. Each buck at 1 A and 80% efficiency dissipates 0.825 W, approximately 73 C rise using 89 C/W. Core LDO at 5.1 V and 150 mA dissipates 0.270 W, about 50 C rise using 184 C/W. These estimates require the respective reference layouts and copper; no enclosed or 85 C ambient operation is qualified. Evaluate the 6 A fault-path copper case and U2 thermal shutdown separately from the 4 A service target.

Sources: saved Pico 2 datasheet sections 5.2/5.5; TPS25947 SLVSFC9C sections 6/7; Diodes AP63203 DS41326 and AP2112 DS39724; module manuals; Coilcraft XAL50xx; Panasonic FK. Exact source links and hashes are in sources/manifest.json and FOOTPRINT_REVIEW.md.
