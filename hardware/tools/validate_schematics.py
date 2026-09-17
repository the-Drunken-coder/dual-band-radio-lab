#!/usr/bin/env python3
"""Export schematics and run unfiltered ERC. Does not invoke any PCB command."""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLI='/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
results=[]
for sch in sorted(ROOT.rglob('*.kicad_sch')):
 name=sch.stem; out=ROOT/'validation'/name;out.mkdir(parents=True,exist_ok=True)
 result={'project':name}
 for label,args in [('pdf',['sch','export','pdf','-o',str(sch.with_suffix('.pdf'))]),('netlist',['sch','export','netlist','--format','kicadxml','-o',str(out/'netlist.xml')]),('erc',['sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json')])]:
  r=subprocess.run([CLI,*args,str(sch)],capture_output=True,text=True)
  (out/(label+'.log')).write_text(r.stdout+r.stderr);result[label]=r.returncode
 results.append(result)
(ROOT/'validation'/'tool-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
