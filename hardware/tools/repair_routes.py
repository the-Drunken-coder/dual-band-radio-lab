#!/usr/bin/env python3
"""Close specific KiCad-reported opens with clearance-aware local grid paths.
Uses KiCad's JSON DRC as the endpoint authority. Every result must pass native DRC.
KiCad Python exports exact existing geometry to the numerical Python worker.
"""
import pcbnew as p
import json,sys,subprocess,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NUMPY='/Users/lanearaujo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
def xy(pt):return [pt.x/1e6,pt.y/1e6]
def box(it):
 b=it.GetBoundingBox();return [b.GetX()/1e6,b.GetY()/1e6,(b.GetX()+b.GetWidth())/1e6,(b.GetY()+b.GetHeight())/1e6]
def main():
 for name in sys.argv[1:]:
  path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path))
  drc=json.loads((ROOT/'validation'/name/'drc.json').read_text());items={};shapes=[]
  for fp in b.GetFootprints():
   for pad in fp.Pads():
    key=pad.m_Uuid.AsString();items[key]=pad
    shapes.append(dict(type='pad',box=box(pad),drill=pad.GetDrillSize().x/1e6,center=xy(pad.GetPosition()),net=pad.GetNetname(),layers=[i for i,l in enumerate([p.F_Cu,p.B_Cu]) if pad.IsOnLayer(l)]))
  for t in b.GetTracks():
   key=t.m_Uuid.AsString();items[key]=t
   if isinstance(t,p.PCB_VIA):shapes.append(dict(type='via',a=xy(t.GetPosition()),width=t.GetWidth(p.F_Cu)/1e6,net=t.GetNetname(),layers=[0,1]))
   else:shapes.append(dict(type='track',a=xy(t.GetStart()),b=xy(t.GetEnd()),width=t.GetWidth()/1e6,net=t.GetNetname(),layers=[0 if t.GetLayer()==p.F_Cu else 1]))
  keepouts=[]
  for z in b.Zones():
   if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
    poly=z.Outline();pts=[xy(poly.CVertex(i)) for i in range(poly.TotalVertices())];keepouts.append(pts)
  tasks=[]
  for a in drc['unconnected_items']:
   if any(d['uuid'] not in items for d in a['items']):continue
   ends=[];net=None
   for d in a['items']:
    it=items[d['uuid']];net=it.GetNetname()
    if isinstance(it,p.PCB_TRACK) and not isinstance(it,p.PCB_VIA):
     ends.append(dict(points=[xy(it.GetStart()),xy(it.GetEnd())],layers=[0 if it.GetLayer()==p.F_Cu else 1]))
    else:ends.append(dict(points=[xy(it.GetPosition())],layers=[i for i,l in enumerate([p.F_Cu,p.B_Cu]) if it.IsOnLayer(l)]))
   for end in ends:
    attached=[sh['a'] for sh in shapes if sh['type']=='via' and sh['net']==net and any(math.dist(sh['a'],pt)<.001 for pt in end['points'])]
    if attached:end.update(points=attached,layers=[0,1])
   tasks.append(dict(net=net,ends=ends,width=.15 if net in ('/ILIM','/S2_CS_N','/P_S2_IRQ') else .25))
  data=dict(shapes=shapes,keepouts=keepouts,tasks=tasks,outline=box(b.GetBoardEdgesBoundingBox()) if False else ([0,0,250,210] if name=='carrier-rev-a' else [-12,-12,72,68]))
  job=ROOT/'layout'/(name+'-repair.json');job.write_text(json.dumps(data))
  subprocess.run([NUMPY,str(ROOT/'tools/route_grid.py'),str(job)],check=True)
  routes=json.loads(job.with_suffix('.routes.json').read_text())
  for route in routes:
   net=b.FindNet(route['net']);pts=route['points'];width=route['width']
   for a,c in zip(pts,pts[1:]):
    if a[2]!=c[2]:
     t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetWidth(p.FromMM(.65));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu)
    else:
     t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(c[0]),p.FromMM(c[1])));t.SetWidth(p.FromMM(width));t.SetLayer(p.F_Cu if a[2]==0 else p.B_Cu)
    t.SetNet(net);b.Add(t)
  p.SaveBoard(str(path),b);print(name,'closed',len(routes),'reported opens',flush=True)
if __name__=='__main__':main()
