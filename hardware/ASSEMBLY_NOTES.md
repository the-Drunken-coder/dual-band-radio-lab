# Rev A assembly requirements

These notes specify the intended assembly configuration for schematic review. There are no manufacturing files and nothing has been submitted for assembly.

## Antenna population evidence

The exact [JLC C411294 E22 listing](https://jlcpcb.com/partdetail/E22-900M30S/C411294) specifies an IPEX interface and shows a fitted coax receptacle in its product photo. The exact [JLC C411312 E28 listing](https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E282G4M27S/C411312) specifies both IPEX and onboard PCB antenna and likewise shows a fitted receptacle. Both listings identify SMT assembly. Archived listing HTML and the actual corresponding product photographs are in `sources/jlc-c411294*` and `sources/jlc-c411312*`, retrieved 2026-09-17. The photographed shield markings match the exact requested models.

Conclusion: catalog evidence supports **IPEX connectors included on both module assemblies**; no separate carrier-side IPEX part should be added to their BOMs. JLC labels images as reference images. This is not a lot inspection or a promise that its standard assembly service changes the E28 antenna selector. Verify populated receptacles during incoming inspection and reject connectorless substitutions.

## Mandatory E28 external-IPEX variant

The current [Ebyte E28-2G4M27S manual](https://www.cdebyte.com/pdf-down.aspx?id=3077), revision history v1.4 dated 2024-04-18, section 9.2 on physical PDF page 10, shows **two alternative positions of the antenna-selection component**. The left illustration selects the PCB antenna; the right selects IPEX. The manual's default is the PCB path. Presence of the connector is insufficient.

For both assembled E28 daughtercards:

- Select the IPEX branch exactly as in the right-hand section 9.2 image, connecting the module RF feed to its IPEX receptacle. The PCB-antenna branch must be open. Never populate both selector paths.
- Use manufacturer-configured IPEX modules, or have the assembler move the existing selector component before delivery under this work instruction. The user performs no resistor relocation, module rework or soldering.
- The public manual does **not** give the selector's reference designator, resistance/value or a complete internal matching schematic. Do not invent an R-number or assume a zero-ohm replacement. Preserve the vendor-installed component and topology; if a replacement is needed, obtain its specification from Ebyte before assembly.
- Inspect the selector against the manual image and record a clear macro photograph for each card. Verify the completed card's RF path at the external connector using an appropriate conducted test and load; visual inspection alone is not a gain/return-loss qualification.

This choice appears on U1's schematic Assembly property, as visible schematic text, and in the E28 BOM's assembly field. JLC C411312 is the base module identifier, **not a verified IPEX-selected ordering suffix**. No supplier has confirmed the extra module-rework service. Procurement must obtain acceptance of this configuration before ordering; ordinary placement of C411312 without that agreement does not satisfy Rev A. This is the remaining external assembly confirmation, not work delegated to the user.

E22 uses its populated IPEX; external ANT pad 21 stays NC. No undocumented selector modification is specified for it. Core2021-HF-M uses its intended module coax connector; exposed RF header contacts remain isolated.

## Factory-installed mechanics and parts

Install all ordinary TSW and SSQ headers, including the underside daughtercard headers and two Pico/Core sockets. They are through-hole assembly work, not covered merely by a catalog's SMT label. Install each captive M3 x 25 alignment post and its threadlocked clamp nut before delivery. The user only plugs in modules/cards/cables. Follow the mating orientation and required solid capture regions in `radio-slot-v0.1.md`; perform its unpowered offset/reversal acceptance checks.

The 1757019 power plug must be supplied preterminated with an 18 AWG or larger lead pair and marked polarity. No source selection or connection to the Pico VBUS pin is permitted on that cable. Follow each manufacturer's soldering profile and moisture sensitivity requirements. Electrolytic pin 1 is positive. Do not substitute shorter posts, narrower copper ratings, unpopulated IPEX variants or smaller/bias-weaker ceramic capacitors without review.

## SPI resistor population

Initially populate carrier R20/R21/R22, E22 R5, Core2021 R3 and R5 on both E28 cards with 22-ohm RC0603FR-0722RL. All use the existing 0603 footprint. RC0603JR-070RL is the explicit 0-ohm configuration option, subject to bring-up measurement and recording the selected configuration. Do not populate both alternatives or omit the resistor: DNP opens that signal. See DESIGN_REVIEW.md for source placement and oscilloscope/IBIS verification.
