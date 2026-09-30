# Manufacturing handoff

**Current upload list: none.** Do not upload these electrical-study BOMs as an assembly order. No fabrication ZIP or CPL exists, and the selected BOMs have not been released for procurement.

The eventual board quantities for one complete radio are:

| PCB design | Assembled quantity |
| --- | ---: |
| carrier-rev-a | 1 |
| e22-900m30s-rev-a | 1 |
| core2021-hf-m-rev-a | 1 |
| e28-2g4m27s-rev-a | 2 |

Pico 2 with headers and Core2021-HF-M are separately purchased plug-in items. Factory assembly must include all mating sockets and male daughtercard headers, so the end user performs no soldering. This includes any required underside or through-hole assembly. Both E28 modules must arrive with IPEX selected.

## Required future release files

After human layout review, supplier process acceptance and explicit authorization for manufacturing output, each board directory should contain the following exact release paths, with `<board>` replaced by that directory's board name:

- `fabrication/<board>-gerbers.zip`: top/bottom copper, top/bottom solder mask, silkscreen, board outline, plated/non-plated drills and the necessary paste layers for the agreed assembly process. Confirm the ZIP contents in the manufacturer's preview.
- `fabrication/<board>-jlc-bom.csv`: approved manufacturer and supplier codes, references, values and quantities. Exclude the separately purchased plug-in modules from the factory placement BOM.
- `fabrication/<board>-jlc-cpl.csv`: footprint reference, centroid X/Y, rotation and board side from the final PCB. Verify each physical part's pin 1 in the assembly preview; do not apply a universal rotation offset.
- `fabrication/<board>-assembly.pdf`: top/bottom assembly views, pin 1, slot role, voltage labels, antenna access, underside header orientation, no-fit list, approved connector MPNs and the E28 antenna-selection requirement where applicable.
- `fabrication/<board>-release.json`: KiCad version, source revision, output hashes, ERC/DRC results and human review record.

Upload the Gerber ZIP for fabrication, then the approved assembly BOM and CPL for assembly, with the assembly drawing as the agreed manufacturing instruction. The paths above are a required output contract, **not files already generated**. Source PDFs, KiCad project files, `connectivity.json`, and the current study `BOM.csv` are not substitutes for those release outputs.

No order, quotation request, manufacturer upload or supplier message was made during this work.
