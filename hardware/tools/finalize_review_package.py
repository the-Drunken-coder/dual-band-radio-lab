#!/usr/bin/env python3
"""Record hashes only after every board and schematic check succeeds."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
drc=json.loads((ROOT/'validation/layout-drc-results.json').read_text())
erc=json.loads((ROOT/'validation/tool-results.json').read_text())
assert len(drc)==len(erc)==4
for row in drc:assert row['exit']==0 and not any(row['findings'].values()),row
for row in erc:assert all(row[k]==0 for k in ['erc','pdf','netlist']),row
for row in json.loads((ROOT/'validation/layout-audit.json').read_text()).values():assert not any(row['drc_findings'].values())
assert len(list(ROOT.rglob('*.kicad_pcb')))==4
assert not [p for p in ROOT.rglob('*') if p.suffix.lower() in ['.gbr','.drl','.ger','.gbl','.gtl']]
p=ROOT/'validation/review-results.json';data=json.loads(p.read_text());data.update(drc=drc,erc=erc,scope='Schematic and routed PCB review only; no manufacturing release.',manufacturing_files_generated=False,orders_placed=False)
files=[]
for f in ROOT.rglob('*'):
 if not f.is_file() or 'sources' in f.relative_to(ROOT).parts or f==p:continue
 if f.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro','.pdf','.png','.md'] or f.name in ['BOM.csv','connectivity.json','connectivity-check.json','layout-audit.json','mechanical-access.json','power-route-audit.json','layout-drc-results.json','footprint-geometry.json']:files.append(f)
data['artifacts']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
p.write_text(json.dumps(data,indent=2)+'\n');print('Final package recorded:',len(files),'artifacts; four clean PCBs and schematics; no manufacturing exports.')
