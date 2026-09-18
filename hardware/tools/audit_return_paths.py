#!/usr/bin/env python3
"""Measure non-ground bottom routing and sample SPI's opposite-layer reference.
Uses native refilled zones, GND pads/traces, and real track/via locations.
Sampling is a geometric screening check, not a field solver or SI certification.
"""
import pcbnew as p
from pathlib import Path
import json,math,collections,sys,hashlib,heapq
from audit_layouts import xy,distance_to_segment,NetGraph
ROOT=Path(__file__).resolve().parents[1]
def audit(path):
 b=p.LoadBoard(str(path));tracks=list(b.GetTracks());pads=[a for f in b.GetFootprints() for a in f.Pads()];vias=[t for t in tracks if isinstance(t,p.PCB_VIA)];gndvias=[v for v in vias if v.GetNetname()=='/GND'];signal=collections.defaultdict(lambda:dict(segments=0,length_mm=0))
 for t in tracks:
  if isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.B_Cu or t.GetNetname()=='/GND':continue
  row=signal[t.GetNetname()];row['segments']+=1;row['length_mm']+=t.GetLength()/1e6
 for r in signal.values():r['length_mm']=round(r['length_mm'],3)
 zones={l:[z.GetFilledPolysList(l) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='/GND' and z.IsOnLayer(l)] for l in [p.F_Cu,p.B_Cu]}
 gp={l:[a for a in pads if a.GetNetname()=='/GND' and a.IsOnLayer(l)] for l in zones};gt={l:[t for t in tracks if not isinstance(t,p.PCB_VIA) and t.GetLayer()==l and t.GetNetname()=='/GND'] for l in zones}
 def ground(pt,layer):
  q=p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
  return reference[layer].Contains(q)
 reference={}
 for layer in [p.F_Cu,p.B_Cu]:
  copper=p.SHAPE_POLY_SET()
  for z in zones[layer]:copper.BooleanAdd(z)
  for item in pads+tracks:
   if item.GetNetname()!='/GND' or not item.IsOnLayer(layer):continue
   shape=p.SHAPE_POLY_SET();item.TransformShapeToPolygon(shape,layer,0,p.FromMM(.005),p.ERROR_INSIDE);copper.BooleanAdd(shape)
  reference[layer]=copper
 exact_voids=[]
 spi=[t for t in tracks if 'SPI' in t.GetNetname() or t.GetNetname()=='/EXP_MISO_SRC'];transitions=[];voids=[];lengths=collections.defaultdict(float)
 for t in spi:
  if isinstance(t,p.PCB_VIA):
   pos=xy(t.GetPosition());nearest=min(gndvias,key=lambda v:math.dist(pos,xy(v.GetPosition()))) if gndvias else None
   transitions.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),xy_mm=pos,nearest_GND_via_mm=round(math.dist(pos,xy(nearest.GetPosition())),3) if nearest else None,GND_via_xy_mm=xy(nearest.GetPosition()) if nearest else None));continue
  a,c=xy(t.GetStart()),xy(t.GetEnd());length=math.dist(a,c)
  missing=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(missing,t.GetLayer(),0,p.FromMM(.005),p.ERROR_OUTSIDE)
  missing.BooleanSubtract(reference[p.B_Cu if t.GetLayer()==p.F_Cu else p.F_Cu])
  if missing.Area()>0:
   exact_voids.append(dict(track_uuid=t.m_Uuid.AsString(),net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer()),unreferenced_copper_area_mm2=round(missing.Area()/1e12,8),polygons=[[[round(missing.COutline(i).CPoint(j).x/1e6,5),round(missing.COutline(i).CPoint(j).y/1e6,5)] for j in range(missing.COutline(i).PointCount())] for i in range(missing.OutlineCount())]))
  if not length:continue
  layer=t.GetLayer();ref=p.B_Cu if layer==p.F_Cu else p.F_Cu;lengths[b.GetLayerName(layer)]+=length;n=max(1,math.ceil(length/.1));dx,dy=(c[0]-a[0])/length,(c[1]-a[1])/length;width=t.GetWidth()/1e6;bad=[]
  for i in range(n):
   frac=(i+.5)/n;pt=(a[0]+frac*(c[0]-a[0]),a[1]+frac*(c[1]-a[1]));ok=all(ground((pt[0]-dy*offset,pt[1]+dx*offset),ref) for offset in [-width/2,0,width/2]);bad.append(not ok)
  start=None
  for i in range(n+1):
   if i<n and bad[i] and start is None:start=i
   if start is not None and (i==n or not bad[i]):
    aa=[a[j]+start/n*(c[j]-a[j]) for j in [0,1]];cc=[a[j]+i/n*(c[j]-a[j]) for j in [0,1]];mid=[(aa[j]+cc[j])/2 for j in [0,1]]
    # Antipads at connectors/vias are still reported, never silently excluded.
    nearby=[]
    for pad in pads:
     if pad.GetNetname()=='/GND' or not pad.IsOnLayer(ref):continue
     bb=pad.GetBoundingBox();r=math.hypot(bb.GetWidth(),bb.GetHeight())/2e6+.3
     if math.dist(mid,xy(pad.GetPosition()))<r:nearby.append(pad.GetParentFootprint().GetReference()+'.'+pad.GetNumber())
    voids.append(dict(net=t.GetNetname(),track_uuid=t.m_Uuid.AsString(),layer=b.GetLayerName(layer),reference_layer=b.GetLayerName(ref),start_mm=aa,end_mm=cc,length_mm=round((i-start)*length/n,4),nearby_non_GND_pads=nearby,nearest_GND_via_mm=round(min((math.dist(mid,xy(v.GetPosition())) for v in gndvias),default=999),3),opposite_layer_non_GND_tracks=sorted(set(tt.GetNetname() for tt in tracks if not isinstance(tt,p.PCB_VIA) and tt.GetLayer()==ref and tt.GetNetname()!='/GND' and distance_to_segment(mid,xy(tt.GetStart()),xy(tt.GetEnd()))[0]<tt.GetWidth()/2e6+.35))));start=None
 pth=[]
 for a in pads:
  if not a.GetDrillSize().x or 'SPI' not in a.GetNetname():continue
  layers=set()
  for t in spi:
   if isinstance(t,p.PCB_VIA) or t.GetNetname()!=a.GetNetname():continue
   if a.HitTest(t.GetStart()) or a.HitTest(t.GetEnd()):layers.add(t.GetLayer())
  if p.B_Cu in layers:
   pos=xy(a.GetPosition());pth.append(dict(reference=a.GetParentFootprint().GetReference()+'.'+a.GetNumber(),net=a.GetNetname(),xy_mm=pos,attached_track_layers=[b.GetLayerName(l) for l in layers],nearest_GND_via_mm=round(min((math.dist(pos,xy(v.GetPosition())) for v in gndvias),default=999),3)))
 feedback=None
 if path.stem=='e28-2g4m27s-rev-a':
  graph=NetGraph(b,'/RADIO_3V3');start=graph.pads[('U2','1')];end=graph.pads[('C2','1')];heap=[(0,start,[])];seen=set()
  while heap:
   length,node,edges=heapq.heappop(heap)
   if node==end:
    feedback=dict(source='U2.1 FB',sense_node='C2.1 local output capacitor',length_including_vias_mm=round(length,3),edges=edges);break
   if node in seen:continue
   seen.add(node)
   for nn,ll,rr in graph.graph[node]:
    if nn not in seen:heapq.heappush(heap,(length+ll,nn,edges+[(node,nn)]))
  assert feedback is not None,'No FB-to-output-capacitor path'
 components=[]
 for poly in zones[p.B_Cu]:
  for i in range(poly.OutlineCount()):components.append((abs(poly.COutline(i).Area())-sum(abs(poly.CHole(i,j).Area()) for j in range(poly.HoleCount(i))))/1e12)
 rails={'/RADIO_5V','/EXT_5V','/SLOT_5V','/RADIO_3V3','/PICO_3V3','/IOREF_3V3','/PICO_VSYS','/USB_VBUS','/SW','/BST'}
 signal_only={net:row for net,row in signal.items() if net not in rails}
 return dict(non_GND_B_Cu_signals_only=dict(segments=sum(row['segments'] for row in signal_only.values()),length_mm=round(sum(row['length_mm'] for row in signal_only.values()),3),excluded_power_and_switch_nodes=sorted(rails)),B_Cu_GND_components=dict(count=len(components),largest_area_mm2=round(max(components,default=0),3),largest_fraction=round(max(components,default=0)/sum(components),6) if components else 0),E28_feedback=feedback,SPI_exact_reference_voids=exact_voids,SPI_PTH_back_layer_escapes=pth,board_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),non_GND_B_Cu=dict(segments=sum(r['segments'] for r in signal.values()),length_mm=round(sum(r['length_mm'] for r in signal.values()),3),by_net=dict(signal)),SPI_length_mm={k:round(v,3) for k,v in lengths.items()},SPI_via_transitions=transitions,SPI_reference_void_intervals=voids,SPI_reference_void_length_mm=round(sum(r['length_mm'] for r in voids),3),B_Cu_GND_area_mm2=round(sum(z.Area()/1e12 for z in zones[p.B_Cu]),3))
def main():
 source=Path('/private/tmp/rev-a-ground-before') if '--baseline' in sys.argv else ROOT
 data={path.stem:audit(path) for path in sorted(source.rglob('*.kicad_pcb'))}
 out=ROOT/'validation'/('return-path-baseline.json' if '--baseline' in sys.argv else 'return-path-audit.json')
 out.write_text(json.dumps(dict(method='Boolean subtraction of opposite-layer native filled GND plus GND pads/tracks/vias from full SPI track copper, arcs polygonized within 0.005 mm; exact missing polygon areas reported. Length summaries use <=0.1 mm longitudinal intervals, trace centre and both edges sampled; all SPI nets including Pico and source segments. Every via reported. Antipads included. No electromagnetic or impedance claim.',boards=data),indent=2)+'\n')
 for name,d in data.items():print(name,d['non_GND_B_Cu']['segments'],d['non_GND_B_Cu']['length_mm'],'bottom mm;',len(d['SPI_via_transitions']),'SPI vias;',d['SPI_reference_void_length_mm'],'mm without full sampled reference')
if __name__=='__main__':main()
