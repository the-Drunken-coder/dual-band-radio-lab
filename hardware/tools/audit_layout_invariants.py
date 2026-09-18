#!/usr/bin/env python3
"""Compare this layout pass with an explicit review snapshot supplied as argv[1].
Reject changes to approved schematics/BOMs, footprint placement, source-series
copper, original GND via nets, or the high-current 5 V distribution.
"""
from pathlib import Path
import pcbnew as p,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];before=Path(sys.argv[1]);result={}
def fp_state(b):
 return {f.GetReference():dict(position=(f.GetPosition().x,f.GetPosition().y),angle=f.GetOrientationDegrees(),layer=f.GetLayer(),pads=sorted((a.GetNumber(),a.GetNetname(),a.GetPosition().x,a.GetPosition().y) for a in f.Pads())) for f in b.GetFootprints()}
def traces(b):
 return sorted((t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth()) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and (t.GetNetname().endswith('_SRC') or t.GetNetname() in ['/RADIO_5V','/EXT_5V','/SLOT_5V']))
for path in ROOT.rglob('*.kicad_pcb'):
 old=before/path.relative_to(ROOT);a=p.LoadBoard(str(old));b=p.LoadBoard(str(path));assert fp_state(a)==fp_state(b),(path.stem,'footprint placement/net drift');assert traces(a)==traces(b),(path.stem,'source or 5 V copper changed')
 av={t.m_Uuid.AsString():t.GetNetname() for t in a.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='/GND'};bv={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks() if isinstance(t,p.PCB_VIA)}
 assert all(bv.get(i)==net for i,net in av.items()),(path.stem,'original GND via missing/reassigned')
 files=[path.with_suffix('.kicad_sch'),path.parent/'BOM.csv']
 old_project=json.loads(old.with_suffix('.kicad_pro').read_text());new_project=json.loads(path.with_suffix('.kicad_pro').read_text())
 # Native KiCad upgrades only the serialization version from 1 to 3.
 old_project['meta'].pop('version',None);new_project['meta'].pop('version',None)
 assert old_project==new_project,(path.stem,'design rules/project settings changed')
 for f in files:assert f.read_bytes()==(before/f.relative_to(ROOT)).read_bytes(),(f,'approved electrical/configuration file changed')
 result[path.stem]=dict(result='PASS',baseline_board_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),current_board_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),unchanged_footprints=len(fp_state(b)),unchanged_original_GND_vias=len(av),unchanged_files=[str(f.relative_to(ROOT)) for f in files])
(ROOT/'validation/layout-invariants.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
