# Source evidence

`manifest.json` records successful downloads with URL, retrieval date, byte count and SHA-256. `online-evidence.md` records manufacturer pages read through the web tool when shell downloads failed. Text extractions help search; drawings and pin tables remain authoritative. Manufacturer copyrights remain with their owners.

Use `../FOOTPRINT_REVIEW.md` for the selected-part dimensional comparison, `../ASSEMBLY_NOTES.md` for exact JLC IPEX population evidence and E28 selector requirements, and `../POWER_BUDGET.md` for document-derived values versus engineering assumptions.

The E22/E28 manuals were retrieved from Ebyte's current product links. E22 electrical and pin tables disagree about minimum voltage; use the stricter 3.3 V floor. E28 section 9.2 shows PCB/IPEX selection but gives no component value or reference number. Its download archive contains 12S/20S footprints, so the 27S footprint was built from the exact 27S drawing.

The saved Waveshare LR20xx PDF is v2.1 and has 243 pages. Semtech lists v2.2, but its download returned an HTML viewer; that file is marked HTML rather than misrepresented as a datasheet. Connector mapping is taken from the Waveshare module schematic and dimensioned drawing.

Exact JLC listings and their front photographs are saved for C411294 and C411312. Both show populated IPEX connectors. Catalog photos are reference evidence, not a lot inspection or confirmation of factory E28 antenna-path selection.

The retained Murata 16 V 22 uF sheet is a superseded candidate. The selected 22 uF part in every current BOM is TDK C3225X7R1E226M250AB. No incomplete/failed download is represented as a manufacturer PDF.
