#!/usr/bin/env python3
"""Refresh measured review tables after the native-board audits complete."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'validation/layout-audit.json').read_text());now=json.loads((ROOT/'validation/return-path-audit.json').read_text())['boards'];before=json.loads((ROOT/'validation/return-path-baseline.json').read_text())['boards']
p=ROOT/'DESIGN_REVIEW.md';s=p.read_text().replace('2026-09-17. **Four routed','2026-09-18. **Four routed')
carrier=layout['carrier-rev-a']['spi']
for net,res,pin,local in [('SPI_SCK','R20','5','U4.12'),('SPI_MOSI','R21','6','U4.13'),('SPI_MISO','R22','7','U7.4')]:
 vals=[carrier[net]['paths'][f'J{i}.{pin}']['length_mm'] for i in [1,3,5,7]]
 row='| '+net+' ('+res+') | '+' | '.join(f'{v:.1f} mm' for v in vals)+f" | {carrier[net]['paths'][local]['length_mm']:.1f} mm ({local}) |"
 s=re.sub(r'^\| '+net+r' \('+res+r'\).*$',lambda _:row,s,flags=re.M)
for name in ['e22-900m30s-rev-a','core2021-hf-m-rev-a','e28-2g4m27s-rev-a']:
 vals=[layout[name]['spi'][n]['header_to_load']['length_mm'] for n in ['SPI_SCK','SPI_MOSI','SPI_MISO']]
 s=re.sub(r'^\| '+name+r' \|.*$',lambda _: '| '+name+' | '+' | '.join(f'{v:.1f} mm' for v in vals)+' |',s,flags=re.M)
rows=[];signals=[];refs=[]
for name in ['carrier-rev-a','e22-900m30s-rev-a','core2021-hf-m-rev-a','e28-2g4m27s-rev-a']:
 a=before[name];b=now[name];x=a['non_GND_B_Cu'];y=b['non_GND_B_Cu'];sig=b['non_GND_B_Cu_signals_only'];ground=b['B_Cu_GND_components'];maxvia=max((t['nearest_GND_via_mm'] for t in b['SPI_via_transitions']),default=0)
 rows.append(f"| {name} | {x['segments']} / {x['length_mm']:.1f} mm | {y['segments']} / {y['length_mm']:.1f} mm | {(1-y['length_mm']/x['length_mm'])*100:.1f}% | {sig['segments']} / {sig['length_mm']:.1f} mm |")
 signals.append(f"| {name} | {a['SPI_length_mm'].get('B.Cu',0):.1f} mm | {b['SPI_length_mm'].get('B.Cu',0):.1f} mm | {len(b['SPI_via_transitions'])} | {f'{maxvia:.3f} mm' if maxvia else 'No transitions'} |")
 refs.append(f"| {name} | {a['SPI_reference_void_length_mm']:.1f} mm | {b['SPI_reference_void_length_mm']:.1f} mm | {ground['count']} | {b['B_Cu_GND_area_mm2']:.1f} mm2 |")
section='''## Ground-reference pass, 2026-09-18

The four boards retain two 70 um copper layers, the original footprints and slot geometry, the approved electrical schematics/BOMs, all source-side series-resistor copper and the 5 V distribution. `layout-invariants.json` compares those items against the pre-pass boards. No power architecture or GPIO assignment changed.

Bottom routing was replaced with front-layer routes and short bottom crossings where the fixed pinout and existing copper prevent a practical front-only path. SPI received routing priority. Longer front-only detours were rejected when a short crossing with a nearby return via preserved a much shorter interconnect. The source-resistor connections were not moved or branched.

| Board | Before: non-GND B.Cu segments / length | After: non-GND B.Cu segments / length | Length reduction | After: signals only, segments / length |
| --- | ---: | ---: | ---: | ---: |
'''+ '\n'.join(rows)+'''

The all-net totals include power and switch nodes. The signals-only column excludes those nets; the JSON lists the exclusion names and every per-net count. Segment counts are native KiCad primitives, including short bends and fanouts. A higher primitive count does not mean less total bottom copper; both quantities are reported without substituting one for the other.

| Board | Before: SPI on B.Cu | After: SPI on B.Cu | SPI via transitions | Greatest nearest-GND-via distance |
| --- | ---: | ---: | ---: | ---: |
'''+ '\n'.join(signals)+'''

The audit includes shared SPI, Pico-side SPI and the local source nets. Every transition has its coordinates, net, UUID, nearest GND via and distance recorded. Through-hole back-layer escapes are reported separately. Added return vias pass native connectivity checks on both layers. Close same-net redundant drills were consolidated; no drill-spacing finding was waived.

### Remaining reference interruptions

The layouts have one continuous filled B.Cu GND region per board, but they do **not** provide an uninterrupted opposite-layer reference beneath every millimetre of SPI. Connector/via antipads, local crossovers and crowded buffer/expander escapes still produce interruptions. These remain explicit human-review items. Clean DRC does not approve them electrically.

| Board | Before: SPI length with sampled reference gaps | After: SPI length with sampled reference gaps | Connected B.Cu GND regions | Filled B.Cu GND area |
| --- | ---: | ---: | ---: | ---: |
'''+ '\n'.join(refs)+'''

`audit_return_paths.py` subtracts native opposite-layer GND copper from each SPI track's full copper outline, retaining the missing polygons and areas. Polygonized arcs use a 0.005 mm error bound. The length summary samples the centre and both trace edges at intervals no longer than 0.1 mm; it includes terminal antipads rather than hiding them. Exact polygon findings can therefore exist even where a short gap falls between length samples. Nearby pads and crossing nets are recorded to locate each finding. This is a geometric audit, not a field solver or impedance certification.

The [carrier reference map](renders/carrier-rev-a-return-reference.svg), [E22 map](renders/e22-900m30s-rev-a-return-reference.svg), [Core map](renders/core2021-hf-m-rev-a-return-reference.svg) and [E28 map](renders/e28-2g4m27s-rev-a-return-reference.svg) show bottom ground, SPI layers and missing reference copper. Magenta regions must be reviewed with the actual source/loading and intended clock speed. Do not interpret a large ground-area percentage as proof that a particular signal has a good return path.

The 10 mm carrier main ground-return corridors and 4 mm terminal corridors were rechecked after refill. A RESET transition that intruded into the left corridor was rerouted; the audit rejects any missing sample instead of retaining the old voltage-drop estimate. The high-current positive traces remain unchanged. The E22 voltage and 30 dBm limitation are explicit in POWER_BUDGET.md.

Native top/bottom and assembled 3D images were regenerated. Footprint positions, card insertion geometry, alignment-post capture, USB/BOOTSEL access, IPEX access and probe access remain unchanged and pass the geometric audit. The original physical-fit, thermal, inrush, RF coexistence and oscilloscope/IBIS qualification steps remain pending. This package stops for human review and is not a fabrication release.

'''
start='## Ground-reference pass, 2026-09-18'
if start in s:s=s[:s.index(start)]+s[s.index('## Final checks and stop point',s.index(start)):]
s=s.replace('## Final checks and stop point',section+'## Final checks and stop point')
p.write_text(s)
print('Updated SPI path tables and ground-reference review from native audit results.')
