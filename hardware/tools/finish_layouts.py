#!/usr/bin/env python3
"""Import locally routed copper and place legible silkscreen clear of exposed pads.
Re-running uses the placement board plus its matching session, not a manufacturing file.
"""
import pcbnew as p
import sys,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from layout_plan import BOARDS,SLOTS
from build_layouts import v,mm,xy

def box(item,gap=0):
 b=item.GetBoundingBox();return (b.GetX()/1e6-gap,b.GetY()/1e6-gap,(b.GetX()+b.GetWidth())/1e6+gap,(b.GetY()+b.GetHeight())/1e6+gap)
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def silk(b,name):
 outline=BOARDS[name]['outline'];obstacles=[];texts=[]
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   if pad.IsOnLayer(p.F_Mask):obstacles.append(box(pad,.25))
  for g in fp.GraphicalItems():
   if g.GetLayer()==p.F_SilkS:obstacles.append(box(g,.15))
  # Package body / pad courtyard is also avoided even when silk DRC would allow a label there.
  if not fp.GetReference().startswith('TP'):
   for g in fp.GraphicalItems():
    if g.GetLayer()==p.F_Fab:obstacles.append(box(g,.15))
  t=fp.Reference()
  if t.IsVisible() and t.GetLayer()==p.F_SilkS:texts.append(t)
 for d in b.GetDrawings():
  if isinstance(d,p.PCB_TEXT) and d.GetLayer()==p.F_SilkS:texts.append(d)
 # Longer board identifiers get priority. Placement stays near the associated item.
 probe_labels={}
 previous=ROOT/'layout'/(name+'-labels.json')
 history=json.loads(previous.read_text()) if previous.exists() else []
 for ref,tp in BOARDS[name]['testpoints'].items():
  label=tp['label'].replace('_',' ').replace('SPI ','').replace('RESET N','RST').replace('CS N','CS').replace('CLIP GND','GND').replace('MOD GND','GND')
  matching=[t for t in texts if t.GetText() in [tp['label'],label]]
  if not matching:continue
  t=min(matching,key=lambda t:math.dist(xy(t.GetPosition()),(tp['x'],tp['y'])))
  probe_labels[t.m_Uuid.AsString()]=(ref,tp)
 texts.sort(key=lambda t:(t.m_Uuid.AsString() not in probe_labels,-len(t.GetText())))
 changes=[]
 for t in texts:
  old=xy(t.GetPosition());text=t.GetText().replace('_',' ').replace('SPI ','').replace('RESET N','RST').replace('CS N','CS').replace('CLIP GND','GND').replace('MOD GND','GND')
  t.SetText(text);t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
  candidates=[(0,0)]+[(dx,dy) for radius in [1.5,3,4.5,6,8,10,14] for dx,dy in [(0,-radius),(0,radius),(-radius,0),(radius,0),(-radius,-radius),(radius,-radius),(-radius,radius),(radius,radius)]]
  probe=probe_labels.get(t.m_Uuid.AsString())
  if probe:
   ref,tp=probe
   if tp['label']=='OUT_3V3':text='3V3';t.SetText(text)
   if tp['label']=='REG_GND':text='GND';t.SetText(text)
   old=(tp['x'],tp['y']-1.9)
   if name!='carrier-rev-a' and tp['x']==-4:
    old=(-9,tp['y']);candidates=[(0,0)]
   elif name!='carrier-rev-a' and tp['label'] in ['BUSY','IRQ','TX_EN','RX_EN']:
    text={'BUSY':'B','IRQ':'I','TX_EN':'T','RX_EN':'R'}[tp['label']]
    t.SetText(text);old=(36.6,tp['y']);candidates=[(0,0)]
   else:
    candidates=[(0,0),(0,-.7),(0,-1.5),(-2,1.9),(2,1.9),(0,3.8),(0,4.5),(-3,1.9),(3,1.9),(0,-2.5),(-4,1.9),(4,1.9)]
  if probe and probe[1]['label']=='SW':old=(12,34.5);candidates=[(0,0),(2,0),(-2,0)]
  chosen=None
  for dx,dy in candidates:
   t.SetPosition(v(old[0]+dx,old[1]+dy));bb=box(t,.15)
   if bb[0]<outline[0]+.3 or bb[1]<outline[1]+.3 or bb[2]>outline[2]-.3 or bb[3]>outline[3]-.3:continue
   if not any(hit(bb,o) for o in obstacles):chosen=bb;break
  if chosen is None:raise RuntimeError((name,text,'no clear label position'))
  obstacles.append(chosen)
  changes.append(dict(text=text,xy=xy(t.GetPosition()),original_xy=old,moved_mm=round(math.dist(old,xy(t.GetPosition())),2)))
 return changes

def main():
 for name in sys.argv[1:] or BOARDS:
  path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb')
  b=p.LoadBoard(str(path))
  if name!='carrier-rev-a':
   for d in b.GetDrawings():
    if isinstance(d,p.PCB_SHAPE) and d.GetLayer()==p.Edge_Cuts:
     for getter,setter in [(d.GetStart,d.SetStart),(d.GetEnd,d.SetEnd)]:
      q=getter()
      if abs(q.x/1e6+8)<.001:setter(v(-12,q.y/1e6))
   for z in b.Zones():
    if not z.GetIsRuleArea():
     o=z.Outline()
     for i in range(o.TotalVertices()):
      q=o.CVertex(i)
      if abs(q.x/1e6+7.5)<.01:q.x=mm(-11.5)
   BOARDS[name]['outline']=(-12,-12,72,68)
  ses=ROOT/'layout'/(name+'.ses')
  assert p.ImportSpecctraSES(b,str(ses)),ses
  labels=silk(b,name)
  p.SaveBoard(str(path),b)
  (ROOT/'layout'/(name+'-labels.json')).write_text(json.dumps(labels,indent=2)+'\n')
  print(name,'session imported',len(b.GetTracks()),'tracks/vias',flush=True)
if __name__=='__main__':main()
