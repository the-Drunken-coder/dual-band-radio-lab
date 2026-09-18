#!/usr/bin/env python3
"""Run unfiltered KiCad DRC, including schematic parity, on each native board."""
from pathlib import Path
import subprocess,json,concurrent.futures,collections,sys
ROOT=Path(__file__).resolve().parents[1]
CLI='/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def check(board):
 out=ROOT/'validation'/board.stem;out.mkdir(exist_ok=True)
 r=subprocess.run([CLI,'pcb','drc','--format','json','--schematic-parity','--severity-all','--refill-zones','--save-board','--exit-code-violations','-o',str(out/'drc.json'),str(board)],capture_output=True,text=True)
 (out/'drc.log').write_text(r.stdout+r.stderr)
 if not (out/'drc.json').exists():return {'board':board.stem,'exit':r.returncode,'error':r.stderr}
 d=json.loads((out/'drc.json').read_text())
 return dict(board=board.stem,exit=r.returncode,findings={k:dict(collections.Counter(v['type'] for v in d.get(k,[]))) for k in ['violations','unconnected_items','schematic_parity']})
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:r=list(pool.map(check,[b for b in sorted(ROOT.rglob('*.kicad_pcb')) if len(sys.argv)==1 or b.stem in sys.argv[1:]]))
(ROOT/'validation/layout-drc-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
