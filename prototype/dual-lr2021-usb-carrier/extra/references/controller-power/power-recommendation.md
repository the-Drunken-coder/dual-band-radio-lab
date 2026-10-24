# Controller and radio power

Select **AP7361C-33E-13**, fixed 3.3V, 1A, SOT223, for the separate always-on `RADIO_3V3` rail. Feed IN from controller P1.21, downstream of D1. Connect grounds. Keep the regulator output separate from controller 3V3. Each radio has its own RESET_N control. No module power switching is added.

## Exact package and footprint

The official product page currently links [AP7361C datasheet DS37274 Rev. 5-2, October 2020](https://www.diodes.com/datasheet/download/AP7361C.pdf). The download and assets URLs served identical bytes. This verification uses AP7361C itself, not its AP7361 predecessor.

| Exact order code | Package | Pin 1 | Pin 2 | Pin 3 | Tab |
| --- | --- | --- | --- | --- | --- |
| **AP7361C-33E-13 selected** | E / SOT223 | **IN** | **GND** | **OUT** | **GND / pin 2** |
| AP7361C-33ER-13 excluded | ER / SOT223R | GND | OUT | IN | OUT / pin 2 |

Ordering page 13 distinguishes E from ER. The pin table on page 2 and marking diagrams on page 15 independently agree. SOT223 has **no EN pin**, as stated on page 11.

Use **Package_TO_SOT_SMD:SOT-223-3_TabPin2** with a symbol wired **1 IN, 2 GND, 3 OUT**. The reference footprint has two pads numbered 2: the center lead and the large tab. Both connect to GND for the selected E device. A 1117/TLV1117LV symbol would wire this part incorrectly. E and ER share package geometry but have different electrical assignments.

The reference footprint's 2.30mm lead pitch matches the package drawing on page 19. Its pads are larger than the suggested pattern on page 21; it is a standard assembly footprint, not an exact copy of that pattern. Give the tab substantial GND copper for heat spreading.

## BOM and signal conditioning

| Quantity | Part or requirement | Connection |
| --- | --- | --- |
| 1 | AP7361C-33E-13, SOT223 | 1 IN to P1.21; 2 and tab GND; 3 OUT to RADIO_3V3 |
| 4 | KEMET C1206C106K3RACTU, 10uF, 25V, X7R, 1206, 10% | Regulator IN, regulator OUT, and each radio supply |
| 2 | KEMET C0805C104K5RACTU, 100nF, 50V, X7R, 0805, 10% | Each radio supply with a short GND return |
| 2 | 47k, 1%, 0805, at least 0.125W | Each CS_N to RADIO_3V3 |
| 2 | 10k, 1%, 0805, at least 0.125W | Each RESET_N to RADIO_3V3 |
| 2 | 33Ω, 1%, 0805, at least 0.125W | Shared SCK and MOSI, near MCU and before fanout |

- GPIO12/P1.18 → `SPI_SCK_MCU` → 33Ω → `SPI_SCK` to both radios.
- GPIO11/P1.17 → `SPI_MOSI_MCU` → 33Ω → `SPI_MOSI` to both radios.
- MISO connects directly to GPIO13/P1.19.

These are two common series resistors, not two per radio. Validate timing and waveforms with final routing and the intended clock. Exact resistor manufacturer part numbers remain a procurement choice.

AP7361C recommends at least 1uF input ceramic and requires **at least 2.2uF output ceramic**. Its typical circuit uses 4.7uF on each side. Use the selected 10uF parts and maintain at least 2.2uF effective output capacitance after bias, temperature, tolerance and aging. Place the regulator's own capacitors directly at IN/OUT and GND; remote radio capacitors do not replace them. Do not externally drive RADIO_3V3. The datasheet does not guarantee reverse-current blocking.

## Thermal budget

Two task-specified 105mA radios draw about 210mA. Allocate 300mA to the radio rail pending module/load verification. At 5.0V IN and 3.3V OUT:

| Radio current | LDO heat | AP7361C SOT223 estimated rise | Rejected AP2112K SOT23 estimated rise |
| --- | --- | --- | --- |
| 210mA | 0.357W | **39.3°C** | 65.7°C |
| 300mA | 0.510W | **56.1°C** | 93.8°C |

AP7361C uses its own datasheet value of **110°C/W**, not the earlier TLV1117LV value of 62.9°C/W. Actual copper and airflow matter. At 50°C ambient, the 300mA estimate gives about 106°C junction before layout uncertainty. D1's forward drop normally reduces regulator dissipation somewhat. The 1A current rating and 1.1W package absolute rating do not establish 1A usability on this board. AP2112K is rejected for this design. The earlier TLV1117LV choice is superseded.

The controller module datasheet lists a 355mA Wi-Fi TX peak. Adding the two radios already gives 565mA before the hub, bridge and LEDs. Plan an actual host source permitting at least 1A at 5V, and use 850mA as a preliminary system allowance. USB-C alone does not grant that allowance. The upstream controller path still needs load and thermal checks.

## The controller's 5V path

The official schematic connects H1 USB VBUS through **D1 B5819WS**, anode pin 1 to USB VBUS and cathode pin 2 to `VDDUSB`. `VDDUSB` also carries the `VCC_5V` label at **P1.21** and feeds controller regulator U2. Thus the radio regulator input is USB voltage **minus D1's forward drop**. D1 carries controller current plus radio-regulator input current.

D1's fitted manufacturer and allowable external load are unspecified. A reference B5819WS datasheet lists 1A but only 250mW package dissipation. At 850mA and an illustrative 0.4V drop, D1 would dissipate 340mW. That example explains why a family current rating is insufficient; it does not establish the fitted diode's limit. Board traces, host allowance, inrush and temperatures remain unverified.

D1 is oriented to block external P1.21 power from returning to USB VBUS through the diode. That is not a full self-powered USB guarantee. This design uses the laptop as the only supply and adds no second input or switching circuit. The separate regulator removes radio load from controller U2, but it does not bypass D1.

Before release, test both radios at maximum intended duty cycle, plus intended Wi-Fi activity, on the actual laptop and cable. Measure the header rail, radio rail, total current, D1 temperature and LDO temperature. If D1 or voltage margin fails, change the power architecture before fabrication approval. A carrier regulator cannot fix an undersized upstream path.

Sources, exact downloads, and SHA256 hashes are in [sources.json](sources.json) and [SHA256SUMS](SHA256SUMS). The downloaded KiCad footprint is a reference only. No canonical board or schematic was edited.
