#!/usr/bin/env python3
"""Resolve native same-net drill-spacing findings without moving other routes.
Join the old centres on both layers inside the former overlapping via copper.
"""
import pcbnew as p,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in sys.argv[1:]:
 path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path));items={t.m_Uuid.AsString():t for t in b.GetTracks()};removed=set()
 for v in json.loads((ROOT/'validation'/name/'drc.json').read_text())['violations']:
  if v['type']!='hole_to_hole':continue
  ids=[a['uuid'] for a in v['items']]
  if any(i in removed for i in ids):continue
  a,c=[items.get(i) for i in ids]
  if not isinstance(a,p.PCB_VIA) or not isinstance(c,p.PCB_VIA) or a.GetNetname()!=c.GetNetname():continue
  start,end=a.GetPosition(),c.GetPosition();net=a.GetNet()
  if (start-end).EuclideanNorm()/1e6>.55:continue
  b.Remove(c);removed.add(ids[1])
  for layer in [p.F_Cu,p.B_Cu]:
   t=p.PCB_TRACK(b);t.SetStart(start);t.SetEnd(end);t.SetLayer(layer);t.SetWidth(p.FromMM(.2));t.SetNet(net);b.Add(t)
 p.SaveBoard(str(path),b);print(name,len(removed),'redundant drills removed')
