"""Remove obsolete open-ended copper and rip up only DRC-confirmed conflicting segments.
The next native DRC reports all connections that must be restored.
"""
import pcbnew as p,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in sys.argv[1:]:
 path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path));r=json.loads((ROOT/'validation'/name/'drc.json').read_text())
 tracks={t.m_Uuid.AsString():t for t in b.GetTracks()};removed=set()
 for err in r['violations']:
  types=['via_dangling','items_not_allowed','clearance','shorting_items']
  if err['type'] not in types:continue
  for item in err['items']:
   t=tracks.get(item['uuid'])
   if t is None or item['uuid'] in removed:continue
   if t.GetNetname() in ['/RADIO_5V','/EXT_5V'] and err['type']!='via_dangling':continue
   if err['type']=='via_dangling' and not isinstance(t,p.PCB_VIA):continue
   removed.add(t.m_Uuid.AsString());b.Remove(t)
 # Merge touching same-net power pours into one polygon set rather than overlapping zones.
 zs=[z for z in b.Zones() if z.GetNetname()=='/RADIO_5V' and not z.GetIsRuleArea()]
 if len(zs)>1:
  for z in zs[1:]:zs[0].Outline().BooleanAdd(z.Outline());b.Remove(z)
 for t in b.GetDrawings():
  if isinstance(t,p.PCB_TEXT) and t.GetText()=='S4 5V':t.SetPosition(p.VECTOR2I(p.FromMM(140),p.FromMM(23)))
 p.SaveBoard(str(path),b);print(name,'removed',len(removed),'conflicting/dangling items')
