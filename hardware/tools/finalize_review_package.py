#!/usr/bin/env python3
"""Record hashes only after every board and schematic check succeeds."""
from pathlib import Path
import json,hashlib
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
drc=json.loads((ROOT/'validation/layout-drc-results.json').read_text())
erc=json.loads((ROOT/'validation/tool-results.json').read_text())
assert len(drc)==len(erc)==4
for row in drc:assert row['exit']==0 and not any(row['findings'].values()),row
for row in erc:assert all(row[k]==0 for k in ['erc','pdf','netlist']),row
for row in json.loads((ROOT/'validation/layout-audit.json').read_text()).values():assert not any(row['drc_findings'].values())
assert len(list(ROOT.rglob('*.kicad_pcb')))==4
assert not [p for p in ROOT.rglob('*') if p.suffix.lower() in ['.gbr','.drl','.ger','.gbl','.gtl']]
returns=json.loads((ROOT/'validation/return-path-audit.json').read_text())['boards']
invariants=json.loads((ROOT/'validation/layout-invariants.json').read_text())
power=json.loads((ROOT/'validation/power-route-audit.json').read_text())
assert all(r['missing_count']==0 for r in power['ground_corridors'].values())
for board in ROOT.rglob('*.kicad_pcb'):
 sha=hashlib.sha256(board.read_bytes()).hexdigest();name=board.stem
 assert returns[name]['board_sha256']==invariants[name]['current_board_sha256']==sha,name
 assert invariants[name]['result']=='PASS',name
 assert returns[name]['B_Cu_GND_components']['count']==1,name
 assert all(t['nearest_GND_via_mm'] is not None and t['nearest_GND_via_mm']<=1.6 for t in returns[name]['SPI_via_transitions']),name
p=ROOT/'validation/review-results.json';data=json.loads(p.read_text());data.update(drc=drc,erc=erc,scope='Schematic and routed PCB review only; no manufacturing release.',manufacturing_files_generated=False,orders_placed=False)
data.update(date=date.today().isoformat(),documentation_update='Ground-reference rerouting, exact return-gap audit, local E28 feedback sense, E22 voltage limitation and refreshed native/access/power/termination checks and renders.')
data['human_review_pending']={'SPI_reference_interruptions_mm':{name:r['SPI_reference_void_length_mm'] for name,r in returns.items()},'E22_full_30dBm_guaranteed':False,'physical_fit_and_signal_integrity_qualification':'Pending'}
files=[]
for f in ROOT.rglob('*'):
 if not f.is_file() or 'sources' in f.relative_to(ROOT).parts or f==p:continue
 if f.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro','.pdf','.png','.svg','.md'] or f.name in ['BOM.csv','connectivity.json','connectivity-check.json','layout-audit.json','mechanical-access.json','power-route-audit.json','layout-drc-results.json','footprint-geometry.json','return-path-audit.json','return-path-baseline.json','layout-invariants.json']:files.append(f)
data['artifacts']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
p.write_text(json.dumps(data,indent=2)+'\n');print('Final package recorded:',len(files),'artifacts; four clean PCBs and schematics; no manufacturing exports.')
