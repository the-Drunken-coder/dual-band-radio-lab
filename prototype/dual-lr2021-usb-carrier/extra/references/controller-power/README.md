# Verified controller reference

For **Waveshare ESP32-S3-DEV-KIT-N8R8-M**, SKU 24243. Only this reference directory was written. No canonical board, schematic, project, generator or intent file was changed.

Use [verified-controller.json](verified-controller.json) for the complete header map and [power-recommendation.md](power-recommendation.md) for the regulator circuit and limits. Downloaded vendor files are in `sources/`; [sources.json](sources.json) records URLs and SHA256 hashes, and [SHA256SUMS](SHA256SUMS) can verify the downloads.

## Geometry

- Two **1×22** headers, **2.54mm pitch**, **22.86mm row-center spacing**. First-to-last pin span is **53.34mm**.
- Body **63.3 × 25.4mm**, PCB **1.6mm** thick. Vendor drawing shows pins extending **8.5mm below the PCB**. Socket mating height is a separate carrier choice.
- Top view, antenna up and USB down: **P1 left, P2 right; both pin 1 ends at the antenna**. Vendor numbers each header 1–22 independently. Do not use WROOM pad numbers for carrier socket pins.
- The STEP H1 connector assembly projects approximately **0.29mm past the USB end**. Provide clearance for the actual USB cable overmold. A connector shell projection does not define plug clearance.
- Four nominal Ø2mm mounting holes; centers span 59.7 × 21.8mm and sit about 1.8mm from the edges. The schematic suggests M1.4 fixing screws. Sockets provide the primary mating interface here.
- Keep the controller PCB antenna clear of carrier copper and nearby metal. Prefer an antenna overhang at the carrier edge, following Espressif guidance.

`inspect_controller.py` extracts the 44 header holes and H1 assembly bounds directly from vendor STEP entities using Python's standard library. Run `python3 extra/references/controller-power/inspect_controller.py` from project root. See [step-measurements.json](extracted/step-measurements.json). No CAD geometry was modified. CAD import artifacts differ slightly from nominal drawing dimensions; these results are not production tolerances.

## Carrier orientation and connector names

The proposed 100×75mm carrier puts USB at the top edge on the left side, with two radios to the right. In this orientation P1 is on the **right**, P2 on the **left**, and both rows run 22→1 from top to bottom. Use two individual 1×22 female sockets 22.86mm apart, at 2.54mm pitch. Suggested assignment is J1=P1 on the right and J2=P2 on the left. See the complete [USB-up row table](header-rows-usb-up.md) and [machine-readable rows](header-rows-usb-up.json). This is a placement reference, not a fit approval.

## Proposed radio GPIOs

| Carrier signal | GPIO | Controller socket pin |
| --- | --- | --- |
| Shared SCK | 12 | P1.18 |
| Shared MOSI | 11 | P1.17 |
| Shared MISO | 13 | P1.19 |
| Radio A CS_N | 10 | P1.16 |
| Radio A DIO11 / IRQ | 4 | P1.4 |
| Radio A BUSY | 5 | P1.5 |
| Radio A RESET_N | 6 | P1.6 |
| Radio B CS_N | 9 | P1.15 |
| Radio B DIO11 / IRQ | 7 | P1.7 |
| Radio B BUSY | 15 | P1.8 |
| Radio B RESET_N | 16 | P1.9 |

These avoid USB19/20, programming UART43/44, straps0/3/45/46, PSRAM35/36/37, actual onboard RGB38, and requested reserve48. External JTAG39–42 also stays free. SCK12/MOSI11/MISO13 use the ESP32-S3 FSPI pin functions. Radio DIO11 means the **radio signal name**, not ESP32 GPIO11.

Use separate 47k pullups on both CS signals and 10k pullups on both RESET signals to the radio rail. Add one 33Ω series resistor on shared SCK and one on shared MOSI near the MCU, before fanout. Hold both CS high before SPI initialization, serialize radio transactions, and initialize/reset both radios after every controller boot. Exact radio pins, bus timing and reset timing belong to the independent radio verification.

## One USB cable for agent tests

The controller's single USB-C feeds a CH334F hub. One branch reaches native ESP32 USB on GPIO19/20; the other reaches CH343P USB-to-UART on GPIO43/44. Use the **CH343 serial interface** for repeated agent flashing and hardware reset. The native interface remains available for USB/JTAG and application tests.

CH343 DTR/RTS drive the existing two-S8050 automatic BOOT/EN circuit. The official schematic already has EN pullup and capacitors, plus BOOT/RESET buttons. No carrier reset transistors or second USB connector are required. Preserve button access and avoid loading EN/BOOT/UART. Ordinary serial terminals can toggle reset lines; use deliberate DTR/RTS settings.

## Conflicts and remaining limits

The legacy wiki incorrectly describes GPIO35–37 as general-purpose on N8R8. Current Waveshare docs and the Espressif module datasheet say the octal PSRAM uses them. The schematic and pinout identify the RGB LED as **GPIO38**, so both 38 and 48 are reserved.

P1.21 power is downstream of D1, and Waveshare gives **no external-load guarantee**. The selected AP7361C-33E-13 SOT223 regulator has 1 IN, 2 GND, 3 OUT and a GND tab. It is rated 1A with thermal limits and a proposed 300mA radio budget, but the controller diode, trace capacity, USB host allowance and complete assembly temperatures still require bench verification. See the power note before canonical design release.

This is document and source-geometry verification. No physical sample, electrical test, KiCad DRC, or FreeCAD fit test was performed. KiCad and FreeCAD were not used.

Primary pages: [Waveshare resources](https://docs.waveshare.com/ESP32-S3-DEV-KIT-N8R8/Resources-And-Documents), [current overview](https://docs.waveshare.com/ESP32-S3-DEV-KIT-N8R8), [legacy wiki](https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8), [USB FAQ](https://docs.waveshare.com/ESP32-S3-DEV-KIT-N8R8/FAQ), and [Espressif automatic boot selection](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html).
