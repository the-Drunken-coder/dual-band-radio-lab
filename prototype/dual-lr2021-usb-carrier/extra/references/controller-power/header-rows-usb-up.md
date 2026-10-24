# Controller sockets with USB at top

Component-side view. USB up, antenna down. This rotates the vendor view 180 degrees; it does not mirror it. Proposed connector names preserve vendor header identity: **J1=P1 on the right; J2=P2 on the left**. Each socket remains independently numbered 1–22. **Pad 1 belongs at the bottom of both sockets.**

Use two 1×22 female sockets, 2.54mm pitch, 22.86mm row-center spacing. Top-to-bottom first/last pad span is 53.34mm. Coordinates below take the left topmost socket pad as (0,0), x right, y down.

| From top | y mm | Left J2=P2 pin | Left function | Right J1=P1 pin | Right function |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.00 | 22 | GND | 22 | GND |
| 2 | 2.54 | 21 | GND | 21 | USB5V_DIODE |
| 3 | 5.08 | 20 | GPIO19 | 20 | GPIO14 |
| 4 | 7.62 | 19 | GPIO20 | 19 | GPIO13 |
| 5 | 10.16 | 18 | GPIO21 | 18 | GPIO12 |
| 6 | 12.70 | 17 | GPIO47 | 17 | GPIO11 |
| 7 | 15.24 | 16 | GPIO48 | 16 | GPIO10 |
| 8 | 17.78 | 15 | GPIO45 | 15 | GPIO9 |
| 9 | 20.32 | 14 | GPIO0 | 14 | GPIO46 |
| 10 | 22.86 | 13 | GPIO35 | 13 | GPIO3 |
| 11 | 25.40 | 12 | GPIO36 | 12 | GPIO8 |
| 12 | 27.94 | 11 | GPIO37 | 11 | GPIO18 |
| 13 | 30.48 | 10 | GPIO38 | 10 | GPIO17 |
| 14 | 33.02 | 9 | GPIO39 | 9 | GPIO16 |
| 15 | 35.56 | 8 | GPIO40 | 8 | GPIO15 |
| 16 | 38.10 | 7 | GPIO41 | 7 | GPIO7 |
| 17 | 40.64 | 6 | GPIO42 | 6 | GPIO6 |
| 18 | 43.18 | 5 | GPIO2 | 5 | GPIO5 |
| 19 | 45.72 | 4 | GPIO1 | 4 | GPIO4 |
| 20 | 48.26 | 3 | GPIO44 | 3 | EN |
| 21 | 50.80 | 2 | GPIO43 | 2 | 3V3 |
| 22 | 53.34 | 1 | GND | 1 | 3V3 |

Left socket x=0; right socket x=22.86mm. Both pin 1 centers are at y=53.34mm. If the canonical design instead assigns J1 to physical left, explicitly exchange the J1/J2 references while retaining P2-left/P1-right and the same vendor pin numbers.

The right top-row power entry marked USB5V_DIODE is vendor 5V0/5V, P1.21, downstream of controller D1. The bottom two 3V3 pins are controller 3V3; do not connect them to RADIO_3V3.

Machine-readable counterpart: [header-rows-usb-up.json](header-rows-usb-up.json). Source electrical mapping: [verified-controller.json](verified-controller.json). This is a connector/placement reference only; no canonical footprint has been edited.
