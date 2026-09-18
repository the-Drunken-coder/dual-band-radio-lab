# Schematic and PCB verification

KiCad 10.0.6, 2026-09-17. All four native boards pass DRC with **zero violations, zero unconnected items and zero schematic-parity findings**. All four schematics pass ERC with zero errors/warnings. Raw reports and process exit codes are retained, with no added exclusions or downgraded severities.

- `layout-drc-results.json` and each board's `drc.json` / `drc.log`: all severities, refilled zones and schematic parity.
- `layout-audit.json`: exact slot header/post coordinates, source-series lengths/membership, GP26–28 isolation, SPI paths and power-trace resistance.
- `mechanical-access.json`: solid capture, no added holes/vias/components in capture regions, card/module envelopes, probe/cable/USB access.
- `power-route-audit.json`: current-weighted positive copper, sampled ground corridors and explicit contact/return allowances. These are estimates, not measured voltages.
- `connectivity-check.json`: independent exported schematic netlists, 272 pin assignments, 40 isolation checks, GPIO headroom, series topology and mechanical engagement arithmetic.
- `footprint-geometry.json` / `footprint-sources.json`: manufacturer comparison of selected library geometry.
- `review-results.json`: final artifact hashes and review scope.

Run checks from the repository root, with the installed KiCad and bundled Python paths adjusted for another host:

```sh
python3 hardware/tools/validate_schematics.py
python3 hardware/tools/check_studies.py
python3 hardware/tools/check_layouts.py
KICAD_PY='/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3'
"$KICAD_PY" hardware/tools/audit_layouts.py
"$KICAD_PY" hardware/tools/audit_mechanics.py
"$KICAD_PY" hardware/tools/audit_power.py
```

DRC refills/saves zones; it does not generate manufacturing output. `render_layouts.py` generates only 3D review PNGs and temporary VRMLs, and `assemble_review_model.py` builds a temporary four-card preview from the same E28 design twice. The final native PCBs are authoritative. Do not rerun the initial placement generator, import the old SES, or rerun one-time repair scripts over them.

DRC is not a thermal, signal-integrity, physical-fit or RF-performance certification. Oscilloscope/IBIS work, load/inrush/thermal tests, unpowered misinsertion tests and manufacturing process acceptance remain pending. Harmless KiCad Python wxApp/font diagnostics are retained in logs and are distinct from DRC/ERC results.
