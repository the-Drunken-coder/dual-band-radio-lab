#!/usr/bin/env python3
"""Add adjacent return vias at SPI transitions, checking real copper and keepouts.
Native DRC and the filled-reference audit must be rerun after placement.
"""
import pcbnew as p
from pathlib import Path
import math,json,sys,re
from audit_layouts import xy,distance_to_segment
ROOT=Path(__file__).resolve().parents[1];report={}
for path in ROOT.rglob('*.kicad_pcb'):
 names=[a for a in sys.argv[1:] if not a.startswith('--')]
 if names and path.stem not in names:continue
 b=p.LoadBoard(str(path));tracks=list(b.GetTracks());pads=[a for f in b.GetFootprints() for a in f.Pads()];gnd=b.FindNet('/GND');vias=[t for t in tracks if isinstance(t,p.PCB_VIA)];gv=[xy(t.GetPosition()) for t in vias if t.GetNetname()=='/GND'];rows=[];rip=set()
 keepouts=[z.Outline() for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
 capture=[] if path.stem=='carrier-rev-a' else [[4.12,-.96,11.12,11.12],[19.36,-6.04,26.36,31.44]]
 def clear(pt,ignored=()):
  x,y=pt
  if any(a-.16<x<c+.16 and bb-.16<y<dd+.16 for a,bb,c,dd in capture):return False
  for z in keepouts:
   if any(z.Contains(p.VECTOR2I(p.FromMM(x+dx),p.FromMM(y+dy))) for dx,dy in [(0,0),(.31,0),(-.31,0),(0,.31),(0,-.31)]):return False
  for a in pads:
   if a.GetDrillSize().x and math.dist(pt,xy(a.GetPosition()))<a.GetDrillSize().x/2e6+.15+.27:return False
   if a.GetNetname()=='/GND':continue
   bb=a.GetBoundingBox();dist=math.hypot(max(bb.GetX()/1e6-x,0,x-(bb.GetX()+bb.GetWidth())/1e6),max(bb.GetY()/1e6-y,0,y-(bb.GetY()+bb.GetHeight())/1e6))
   if dist<.47:return False
  for t in tracks:
   if t.GetNetname() in ignored:continue
   if isinstance(t,p.PCB_VIA):
    if math.dist(pt,xy(t.GetPosition()))<max(.57,t.GetWidth(p.F_Cu)/2e6+.46):return False
   elif t.GetNetname()!='/GND' and distance_to_segment(pt,xy(t.GetStart()),xy(t.GetEnd()))[0]<t.GetWidth()/2e6+.46:return False
  return True
 for t in [v for v in vias if 'SPI' in v.GetNetname() or v.GetNetname()=='/EXP_MISO_SRC']:
  pos=xy(t.GetPosition());nearest=min([math.dist(pos,a) for a in gv],default=999)
  if nearest<=1.6:rows.append(dict(signal=pos,existing_distance_mm=nearest));continue
  found=None
  for radius in [.8,.9,1,1.1,1.2,1.3,1.4,1.5]:
   for i in range(32):
    pt=tuple(round(pos[j]+radius*(math.cos(i*math.pi/16) if j==0 else math.sin(i*math.pi/16)),4) for j in [0,1])
    if clear(pt):found=pt;break
   if found:break
  if not found and '--reserve' in sys.argv:
   movable={tt.GetNetname() for tt in tracks if 'SPI' not in tt.GetNetname() and tt.GetNetname() not in ['/GND','/EXP_MISO_SRC','/RADIO_5V','/EXT_5V','/USB_VBUS','/PICO_VSYS']}
   options=[]
   for radius in [.8,1,1.2,1.4,1.5]:
    for i in range(64):
     pt=(round(pos[0]+radius*math.cos(i*math.pi/32),4),round(pos[1]+radius*math.sin(i*math.pi/32),4))
     if not clear(pt,movable):continue
     conflicts=set()
     for tt in tracks:
      if tt.GetNetname() not in movable:continue
      dist=math.dist(pt,xy(tt.GetPosition()))-tt.GetWidth(p.F_Cu)/2e6 if isinstance(tt,p.PCB_VIA) else distance_to_segment(pt,xy(tt.GetStart()),xy(tt.GetEnd()))[0]-tt.GetWidth()/2e6
      if dist<.47:conflicts.add(tt.GetNetname())
     options.append((len(conflicts),radius,pt,sorted(conflicts)))
   if options:
    _,_,found,conflicts=min(options)
    rip.update(old_track.m_Uuid.AsString() for old_track in tracks if old_track.GetNetname() in conflicts)
    tracks=[old_track for old_track in tracks if old_track.GetNetname() not in conflicts]
    rows.append(dict(reserved_GND_via=found,reroute_nets=conflicts));print('REROUTE',json.dumps(conflicts),flush=True)
  if not found:rows.append(dict(signal=pos,unresolved=True,nearest_mm=nearest));continue
  v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(found[0]),p.FromMM(found[1])));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(gnd);b.Add(v);tracks.append(v);gv.append(found);rows.append(dict(signal=pos,added_GND_via=found,distance_mm=math.dist(pos,found)))
 temporary=Path('/private/tmp/'+path.stem+'-stitch-edit.kicad_pcb');p.SaveBoard(str(temporary),b)
 content=temporary.read_text()
 # Strip only the explicitly selected complete copper records before reloading;
 # KiCad would otherwise assign a colliding new return via to the old signal.
 content=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda match:'' if any(identifier in match.group(0) for identifier in rip) else match.group(0),content,flags=re.S)
 path.write_text(content);report[path.stem]=rows
print(json.dumps(report,indent=2))
