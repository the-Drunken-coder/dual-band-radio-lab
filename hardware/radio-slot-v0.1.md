# Radio Slot v0.1

Schematic interface frozen for review on 2026-09-17. Retains separate 1x10 A and 1x8 B headers on 2.54 mm pitch. No hot insertion. Remove USB and external power before exchanging cards.

| Pin | A, 1x10 | B, 1x8 |
| --- | --- | --- |
| 1 | GND | BUSY |
| 2 | +5 V | IRQ |
| 3 | +5 V | TX_EN |
| 4 | GND | RX_EN |
| 5 | SPI SCK | AUX0, no carrier connection |
| 6 | SPI MOSI | AUX1, NC on Rev A |
| 7 | SPI MISO | IOREF_3V3, external-only |
| 8 | CS_N | GND |
| 9 | RESET_N | n/a |
| 10 | GND | n/a |

S2 Core does not use TX_EN/RX_EN. E28 and Core do not consume IOREF_3V3; their pull-ups use local 3.3 V. E22 uses IOREF_3V3 only for logic pull-ups. A2/A3 share current. Do not route 4 A through one daughtercard: each slot is allocated at most 1 A at 5 V and each power contact is conservatively allocated 0.5 A. The carrier's total design rating is 4 A.

## Mechanical interface and anti-misinsertion

Use Samtec SSQ-110-01-G-S and SSQ-108-01-G-S on the carrier; TSW-110-07-G-S and TSW-108-07-G-S on daughtercard undersides. Unequal pin counts alone are not a key. Both strips are ordinary fully populated parts. The mandatory alignment post provides the positive key.

Coordinates below are an interface specification, in mm, looking down through the installed daughtercard toward the carrier. They do not constitute a PCB layout. A1=(0,0), A10=(0,22.86), B1=(30.48,0), B8=(30.48,17.78). The mandatory post/hole is **H=(7.62,5.08)**. Both boards use a 3.4 mm NPTH, finished tolerance +0.1/-0 mm, and a 7 mm diameter no-copper/no-component zone through all layers. Hole center tolerance is +/-0.10 mm relative to the header pattern. Numbering on the daughtercard bottom view is mirrored; preserve the installed-view coordinates.

Each carrier slot gets an Accu SSCF-M3-25-A2 fully threaded M3 x 25 screw inserted from below. An HPN-M3-A2 nut above the carrier clamps it permanently; the assembler applies threadlocker and verifies it cannot loosen during card removal. The screw head is 5.5 mm diameter and 3 mm high; the nut is 5.5 mm across flats and 2.4 mm thick. These are selected BOM parts. No user installation of the key is allowed. Daughtercards have the mating H1 hole encoded in their schematics and assigned hole footprints.

For 1.6 mm +/-10% carrier thickness and a conservative 0.3 mm screw-length allowance, the post projects at least **22.94 mm** above the carrier. Even allowing +0.25 mm socket height, +0.25 mm male-header body and +0.20 mm exposed pin length, electrical engagement cannot begin above **17.59 mm**. The post therefore meets the daughtercard at least **5.35 mm before pins can reach socket contacts**. Normal mated board separation is 8.51+2.54 = 11.05 mm. Preserve clearance above the protruding post and access beneath its screw head.

A +/- one-pin offset moves the hole 2.54 mm; maximum radial clearance is only 0.30 mm using a conservative 2.9 mm post diameter and 3.5 mm hole. It cannot fit. A 180-degree reversed card moves its hole to x=22.86 mm rather than 7.62 mm, a 15.24 mm mismatch.

**Solid capture areas are mandatory:** retain solid laminate over the post strike locations around the intended hole at y=2.54 and 7.62 mm, and along the reversed-post corridor x=22.86 mm, y=-2.54 through 27.94 mm. Keep a minimum 3.5 mm radius around that corridor free of holes, cutouts and components, on both faces. The daughtercard must span that area; neither an outline notch nor a module clearance hole may bypass the key. Header placement is invalid if the post can pass outside the card during reversal or a one-pin offset. These constraints must be transferred into the later mechanical drawing before layout release.

This is a straight-insertion key for intact parts, not a claim against deliberate angled forcing. Factory fit acceptance, with all power removed: correct orientation seats; +/- one-pitch offsets and 180-degree reversal, including shifts that align the unequal rows, stop on the post before any electrical engagement. Confirm post projection >=22.94 mm and the solid capture regions. No PCB has yet been made, so this physical fit test is an eventual assembly acceptance test, not a reported result.
