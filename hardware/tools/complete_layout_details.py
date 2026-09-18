#!/usr/bin/env python3
"""Physical review corrections after routing: probe access, keepouts and ground stitching."""
import pcbnew as p
import sys,math,uuid,json
from pathlib import Path
from build_layouts import Board,v,mm,xy
from layout_plan import BOARDS,SLOTS
ROOT=Path(__file__).resolve().parents[1]
def tag(s):return p.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,'rev-a-layout/'+s)))
def main():
 for name in sys.argv[1:] or BOARDS:
  path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path));fp={f.GetReference():f for f in b.GetFootprints()}
  h=Board.__new__(Board);h.b=b;h.name=name;h.plan=BOARDS[name];h.fp=fp;h.nets={n.GetNetname().lstrip('/'):n for n in b.GetNetsByNetcode().values()}
  # Correct source UUID paths for future Update PCB from Schematic operations.
  uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'dual-band-radio-lab/rev-a-study/'+s))
  for ref,f in fp.items():f.SetPath(p.KIID_PATH('/'+uid(name)+'/'+uid(name+ref)))
  if name=='e28-2g4m27s-rev-a':
   t=fp['TP16'];t.SetPosition(v(10.1,39.7));t.SetFPID(p.LIB_ID('RadioLab','Probe_Pad_D0.6mm'))
   for a in t.Pads():a.SetSize(v(.6,.6))
   h.track('SW',[(10.1,39.7),(10.5,40.5)],.25)
  if name=='carrier-rev-a':
   for ref,tp in BOARDS[name]['testpoints'].items():
    if tp['x']==144:
     fp[ref].SetPosition(v(138,tp['y']));tp['x']=138
     # Move that probe's label by the same delta, using the label audit identity.
     label=tp['label'].replace('_',' ').replace('RESET N','RST').replace('CS N','CS')
     for t in b.GetDrawings():
      if isinstance(t,p.PCB_TEXT) and t.GetText()==label:
       x,y=xy(t.GetPosition());t.SetPosition(v(x-6,y))
   # Keep disconnected E28 PCB-antenna regions clear on carrier as well as card.
   for slot in [3,4]:
    x,y=SLOTS[slot];h.keepout(h.corners((x+40,y+13,x+61,y+29.5)),True,False)
   for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='/RADIO_5V' and t.GetWidth()>=mm(4):
     x,y=xy(t.GetStart());xx,yy=xy(t.GetEnd());w=t.GetWidth()/2e6
     if x==xx or y==yy:h.zone('RADIO_5V',(min(x,xx)-w,min(y,yy)-w,max(x,xx)+w,max(y,yy)+w),priority=2)
  else:
   # Capture regions allow copper but prohibit vias/holes in the laminate that stops a bad insertion.
   h.keepout(h.corners((4.12,-.96,11.12,11.12)),False,False)
   z=b.Zones()[-1];z.SetDoNotAllowVias(True)
  # Stitch only where the existing filled ground is clear on both faces over the full via disk.
  ground=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='/GND']
  polys={layer:[z.GetFilledPolysList(layer) for z in ground if z.IsOnLayer(layer)] for layer in [p.F_Cu,p.B_Cu]}
  existing=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
  count=0;bounds=BOARDS[name]['outline'];pitch=10 if name=='carrier-rev-a' else 7
  for x in range(math.ceil(bounds[0]+3),math.floor(bounds[2]-2),pitch):
   for y in range(math.ceil(bounds[1]+3),math.floor(bounds[3]-2),pitch):
    if any(math.hypot(x-a,y-c)<1 for a,c in existing):continue
    if any(z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.Outline().Contains(v(x,y)) for z in b.Zones()):continue
    samples=[v(x+.55*math.cos(i*math.pi/8),y+.55*math.sin(i*math.pi/8)) for i in range(16)]+[v(x,y)]
    if all(any(poly.Contains(pt) for poly in polys[layer]) for layer in polys for pt in samples):h.via('GND',x,y);count+=1
  p.SaveBoard(str(path),b);print(name,'ground stitching added',count,flush=True)
if __name__=='__main__':main()
