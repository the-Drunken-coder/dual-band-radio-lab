#!/usr/bin/env python3
"""Export/apply the explicit ground-reference reroute. Final boards require native DRC.
Input snapshots are kept in /private/tmp, never as fabrication data.
"""
from pathlib import Path
import pcbnew as p,json,sys
from repair_routes import xy,box
ROOT=Path(__file__).resolve().parents[1]
name=sys.argv[2];path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb')
b=p.LoadBoard(str(path));job=Path('/private/tmp/'+name+'-ground.json')
keep={'/GND','/SLOT_5V','/RADIO_5V','/EXT_5V','/RADIO_3V3','/USB_VBUS','/PICO_VSYS','/SW','/BST','/UVLO','/OVLO','/DVDT','/ILIM'}
nets=sorted({a.GetNetname() for f in b.GetFootprints() for a in f.Pads() if a.GetNetname() and not a.GetNetname().startswith('unconnected')}-keep)
nets=[n for n in nets if not n.endswith('_SRC')]
if '--control' in sys.argv:nets=[n for n in nets if 'SPI' not in n]
elif len(sys.argv)>3:nets=sys.argv[3:]
nets.sort(key=lambda n:(0 if 'SPI' in n else 1 if 'CS_N' in n else 3 if '3V3' in n else 2,n))
if sys.argv[1]=='export':
 shapes=[];pads=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   row=dict(type='pad',box=box(a),drill=a.GetDrillSize().x/1e6,center=xy(a.GetPosition()),net=a.GetNetname(),layers=[i for i,l in enumerate([p.F_Cu,p.B_Cu]) if a.IsOnLayer(l)],ref=f.GetReference(),pin=a.GetNumber())
   shapes.append(row);pads.append(row)
 for t in b.GetTracks():
  if t.GetNetname() in nets:continue
  if isinstance(t,p.PCB_VIA):shapes.append(dict(type='via',a=xy(t.GetPosition()),width=t.GetWidth(p.F_Cu)/1e6,net=t.GetNetname(),layers=[0,1]))
  else:shapes.append(dict(type='track',a=xy(t.GetStart()),b=xy(t.GetEnd()),width=t.GetWidth()/1e6,net=t.GetNetname(),layers=[0 if t.GetLayer()==p.F_Cu else 1]))
 keepouts=[]
 for z in b.Zones():
  if z.GetIsRuleArea() and z.GetDoNotAllowTracks():keepouts.append([xy(z.Outline().CVertex(i)) for i in range(z.Outline().TotalVertices())])
 data=dict(nets=nets,shapes=shapes,pads=pads,keepouts=keepouts,outline=[0,0,250,210] if name=='carrier-rev-a' else [-12,-12,72,68],captures=[] if name=='carrier-rev-a' else [[4.12,-.96,11.12,11.12],[19.36,-6.04,26.36,31.44]])
 job.write_text(json.dumps(data));print(job)
else:
 data=json.loads(job.read_text());nets=data['nets'];routes=json.loads(job.with_suffix('.routes.json').read_text());assert set(nets)==set(routes),set(nets)-set(routes)
 for t in list(b.GetTracks()):
  if t.GetNetname() in nets or t.m_Uuid.AsString() in data.get('removed_ground_tracks',[]):b.Remove(t)
 for net,branches in routes.items():
  for branch in branches:
   pts=branch['points']
   for a,c in zip(pts,pts[1:]):
    if a[2]!=c[2]:
     t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu)
    else:
     if a==c:continue
     t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(c[0]),p.FromMM(c[1])));t.SetWidth(p.FromMM(branch['width']));t.SetLayer(p.F_Cu if a[2]==0 else p.B_Cu)
    t.SetNet(b.FindNet(net));b.Add(t)
 for xy_ in data.get('added_ground_vias',[]):
  v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(xy_[0]),p.FromMM(xy_[1])));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('/GND'));b.Add(v)
 p.SaveBoard(str(path),b);print(name,'applied',len(routes),'nets')
