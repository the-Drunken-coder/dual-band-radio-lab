#!/usr/bin/env python3
"""Render native boards and export temporary VRMLs solely for assembly review."""
from pathlib import Path
import subprocess,concurrent.futures,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
CLI='/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def render(path):
 cmd=[CLI,'pcb','render','--width','1800','--height','1400','--background','opaque','--rotate','25,0,15','--zoom','0.65' if path.stem.startswith('e22') else '0.8','-o',str(OUT/(path.stem+'-3d.png')),str(path)]
 r=subprocess.run(cmd,capture_output=True,text=True);(OUT/(path.stem+'-render.log')).write_text(r.stdout+r.stderr)
 assert r.returncode==0,(path,r.stderr)
 if path.stem!='carrier-rev-a':
  r=subprocess.run([CLI,'pcb','export','vrml','--force','--units','tenths','--user-origin','0x0mm','-o','/private/tmp/'+path.stem+'.wrl',str(path)],capture_output=True,text=True)
  assert r.returncode==0,(path,r.stderr)
 return path.stem
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:print(list(pool.map(render,ROOT.rglob('*.kicad_pcb'))))
