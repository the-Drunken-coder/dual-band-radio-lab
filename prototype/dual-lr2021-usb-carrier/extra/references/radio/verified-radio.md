# Waveshare Core2021-HF-M verification

Verified against Waveshare's HF schematic and official photos. SKU 34523 has two pre-soldered straight 1x8 male headers underneath. Sources and SHA256 hashes are in `verified-radio.json` and `SHA256SUMS`.

## Socket coordinates

Top view, shield text upright, antenna connectors on the right. Origin is the upper-left header center, module pin 8. X goes right and Y goes down. All values are millimeters. The published pinout photo shows the underside.

| Module pin | Signal | X | Y |
| --- | --- | ---: | ---: |
| 1 | 2.4G_ANT | 17.78 | 0.00 |
| 2 | GND | 15.24 | 0.00 |
| 3 | DIO11 | 12.70 | 0.00 |
| 4 | DIO8 | 10.16 | 0.00 |
| 5 | DIO7 | 7.62 | 0.00 |
| 6 | NC | 5.08 | 0.00 |
| 7 | GND | 2.54 | 0.00 |
| 8 | 3V3 | 0.00 | 0.00 |
| 9 | BUSY | 0.00 | 15.24 |
| 10 | RESET | 2.54 | 15.24 |
| 11 | MISO | 5.08 | 15.24 |
| 12 | MOSI | 7.62 | 15.24 |
| 13 | SCK | 10.16 | 15.24 |
| 14 | NSS | 12.70 | 15.24 |
| 15 | GND | 15.24 | 15.24 |
| 16 | LoRa_ANT | 17.78 | 15.24 |

Both official dimensional sources agree on 2.54 pitch, 17.78 end-to-end span, and 15.24 between row centers. Pin 1 is upper-right next to the 2.4 GHz port; pin 16 is lower-right next to the Sub-GHz port. The supplied pinout is correct.

## RF connections

ANT1 is the IPEX4 2.4 GHz port; ANT2 is the IPEX4 868/915 MHz port. Module pin 1 connects to the 2.4 GHz RF net through optional R2, and pin 16 to the Sub-GHz RF net through optional R3. Both are marked `NC/0R` in the official schematic.

For the carrier using those IPEX4 ports, leave pins 1 and 16 isolated with no traces, planes or testpoints. Leave pin 6 isolated. The RF pins are optional antenna breakouts, not GPIO. `NC/0R` alone does not prove the actual fitted resistor configuration of a received module.

## Female socket option

Two Samtec SSW-108-01-G-S sockets per module provide eight positions at 2.54 pitch. Samtec's [single-row footprint](https://suddendocs.samtec.com/prints/ssw-s.pdf) specifies a 1.04 mm hole. A 1.80 mm copper land gives a nominal 0.38 mm annular ring and 0.74 mm adjacent copper gap. The land diameter is an explicit carrier design choice, not a Waveshare dimension. Hole plating and fabrication tolerances remain board-rule inputs.

Samtec specifies 0.635 mm square mating posts, 3.68 to 6.35 mm insertion, and an 8.51 mm socket body height. Waveshare does not dimension its supplied male posts. A sample fit must confirm their cross-section and exposed length before claiming this exact socket is a verified mate. The XY pattern itself is verified.

## Conflicting body dimensions

- Official CAD PDF: 22.01 x 18.45 mm, 1.00 mm PCB, 2.50 mm from PCB bottom to shield top.
- Official product image: 22.00 x 19.00 mm, 3.27 mm overall bare-module thickness.
- Both show the same header geometry. Keep clearance for at least 22.01 x 19.00 mm plus assembly margin. Neither gives the installed height of the -M headers plus socket.
- The module's 1.00 mm hole is not the carrier socket drill size.

`drawing-detail.png` shows the PDF annotations; `dimensions.png` shows the conflicting product image. `schematic-pinout-detail.png` shows U2 and the optional RF links. The official STEP is archived as `core2021-xf-3D.stp`; no new mechanical model was created.

## Sources

- [Waveshare resources index](https://docs.waveshare.com/Core2021-XF/Resources-And-Documents)
- [Waveshare product page, HF-M SKU](https://www.waveshare.com/core2021-xf.htm?sku=34523)
- [Waveshare repository](https://github.com/waveshareteam/core2021-xf), pinned commit `92dc63be8c6930b27cd1a52b7563aebb581aaa90`
- [Samtec socket](https://www.samtec.com/products/ssw-108-01-g-s), [catalog](https://suddendocs.samtec.com/catalog_english/ssw_th.pdf)

Only the intent file and radio references were written. No carrier design files were changed.
