#!/usr/bin/env python3
"""Make a temporary, non-electrical assembly preview using one E28 design twice."""
import pcbnew as p
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'carrier-rev-a/carrier-rev-a.kicad_pcb';b=p.LoadBoard(str(src))
for fp in b.GetFootprints():
 models=list(fp.Models())
 fp.Models().clear()
 for m in models:
  m.m_Filename=m.m_Filename.replace('${KIPRJMOD}',str(src.parent));fp.Add3DModel(m)
 for ref,name in [('J1','e22-900m30s-rev-a'),('J3','core2021-hf-m-rev-a'),('J5','e28-2g4m27s-rev-a'),('J7','e28-2g4m27s-rev-a')]:
  if fp.GetReference()==ref:
   m=p.FP_3DMODEL();m.m_Filename='/private/tmp/'+name+'.wrl';m.m_Offset.z=11.85;fp.Add3DModel(m)
p.SaveBoard('/private/tmp/rev-a-assembly-preview.kicad_pcb',b)
