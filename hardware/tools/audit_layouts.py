#!/usr/bin/env python3
"""Independent native-board measurements for Rev A geometry, connectivity and route lengths.
Run using KiCad Python after native DRC has completed with zero findings.
"""
import pcbnew as p
import math,json,heapq,collections,sys
from pathlib import Path
from layout_plan import BOARDS,SLOTS
ROOT=Path(__file__).resolve().parents[1]
def xy(a):return (a.x/1e6,a.y/1e6)
def rounded(a):return tuple(round(x,4) for x in a)
def distance_to_segment(pt,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];d=dx*dx+dy*dy
 t=max(0,min(1,((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/d)) if d else 0
 return math.hypot(pt[0]-a[0]-t*dx,pt[1]-a[1]-t*dy),t
class NetGraph:
 def __init__(self,b,net):
  self.graph=collections.defaultdict(list);self.pads={};segs=[];points=collections.defaultdict(set);vias=[]
  self.total=0
  for t in b.GetTracks():
   if t.GetNetname()!=net:continue
   if isinstance(t,p.PCB_VIA):
    a=rounded(xy(t.GetPosition()));vias.append(a)
    for l in [0,2]:points[l].add(a)
   else:
    a,c=rounded(xy(t.GetStart())),rounded(xy(t.GetEnd()));l=t.GetLayer();w=t.GetWidth()/1e6
    if a!=c:segs.append((a,c,l,w));points[l].update([a,c]);self.total+=math.dist(a,c)
  for fp in b.GetFootprints():
   for pad in fp.Pads():
    if pad.GetNetname()!=net:continue
    center=rounded(xy(pad.GetPosition()));layers=[l for l in [0,2] if pad.IsOnLayer(l)]
    self.pads[(fp.GetReference(),pad.GetNumber())]=center+(layers[0],)
    for l in layers:
     for pt in list(points[l]):
      if pad.HitTest(p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))):self.edge(center+(l,),pt+(l,),math.dist(center,pt),0)
     points[l].add(center)
    if len(layers)==2:self.edge(center+(0,),center+(2,),0,0)
  # Split T junctions and crossings on the same net.
  for i,(a,c,l,w) in enumerate(segs):
   for aa,cc,ll,ww in segs[i+1:]:
    if l!=ll:continue
    dx,dy=c[0]-a[0],c[1]-a[1];ex,ey=cc[0]-aa[0],cc[1]-aa[1];den=dx*ey-dy*ex
    if abs(den)<1e-10:continue
    t=((aa[0]-a[0])*ey-(aa[1]-a[1])*ex)/den;u=((aa[0]-a[0])*dy-(aa[1]-a[1])*dx)/den
    if -.00001<=t<=1.00001 and -.00001<=u<=1.00001:points[l].add(rounded((a[0]+t*dx,a[1]+t*dy)))
  for a,c,l,w in segs:
   on=[]
   for pt in points[l]:
    dist,t=distance_to_segment(pt,a,c)
    if dist<.001:on.append((t,pt))
   on.sort()
   for (_,x),(_,y) in zip(on,on[1:]):
    length=math.dist(x,y);r=.01724*(length/1000)/(w*.07)*1.1572
    self.edge(x+(l,),y+(l,),length,r)
  for x in vias:self.edge(x+(0,),x+(2,),1.6,.0015)
 def edge(self,a,b,length,resistance):
  self.graph[a].append((b,length,resistance));self.graph[b].append((a,length,resistance))
 def path(self,source,dest,by_resistance=False):
  start=self.pads[source];goal=self.pads[dest];heap=[(0,start,0,0)];seen=set()
  while heap:
   cost,node,length,res=heapq.heappop(heap)
   if node==goal:return {'length_mm':round(length,3),'resistance_60C_ohm':round(res,6)}
   if node in seen:continue
   seen.add(node)
   for n,ll,rr in self.graph[node]:
    if n not in seen:heapq.heappush(heap,(cost+(rr if by_resistance else ll),n,length+ll,res+rr))
  return {'unresolved_graph_path':True,'source':source,'destination':dest}
def main():
 result={}
 for name,plan in BOARDS.items():
  path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()}
  out=dict(dimensions_mm=[250,210] if name=='carrier-rev-a' else [84,80],copper_layers=b.GetCopperLayerCount(),board_thickness_mm=b.GetDesignSettings().GetBoardThickness()/1e6,slots=[],sources=[],spi={},power={},testpoints=[])
  def pt(ref,num):return xy(next(a for a in fps[ref].Pads() if a.GetNumber()==str(num)).GetPosition())
  slots=[(s,'J'+str(2*s-1),'J'+str(2*s),'H'+str(s),(x,y)) for s,(x,y) in SLOTS.items()] if name=='carrier-rev-a' else [(0,'J1','J2','H1',(0,0))]
  for s,a,c,h,origin in slots:
   for i in range(1,11):assert math.dist(pt(a,i),(origin[0],origin[1]+(i-1)*2.54))<.001
   for i in range(1,9):assert math.dist(pt(c,i),(origin[0]+30.48,origin[1]+(i-1)*2.54))<.001
   assert math.dist(xy(fps[h].GetPosition()),(origin[0]+7.62,origin[1]+5.08))<.001
   out['slots'].append(dict(slot=s,A1=origin,B1=pt(c,1),post=xy(fps[h].GetPosition()),result='PASS'))
  pairs=[('U5','21','R20'),('U5','20','R21'),('U4','14','R22')] if name=='carrier-rev-a' else [('J4','3','R3')] if name.startswith('core') else [('U1','16' if name.startswith('e22') else '3','R5')]
  for ref,pin,res in pairs:
   pad=next(a for a in fps[ref].Pads() if a.GetNumber()==pin);net=pad.GetNetname();g=NetGraph(b,net)
   members=sorted(g.pads);assert members==sorted([(ref,pin),(res,'1')]),(name,net,members)
   route=g.path((ref,pin),(res,'1'));assert 'length_mm' in route and abs(g.total-route['length_mm'])<.01,(name,net,'extra source copper or layer transition');out['sources'].append(dict(net=net,source=ref+'.'+pin,resistor=res,**route,total_source_copper_mm=round(g.total,3)))
  for net,res in [('SPI_SCK','R20'),('SPI_MOSI','R21'),('SPI_MISO','R22')]:
   g=NetGraph(b,'/'+net)
   if name=='carrier-rev-a':
    targets=[(f'J{2*s-1}',str({'SPI_SCK':5,'SPI_MOSI':6,'SPI_MISO':7}[net])) for s in SLOTS]
    if net=='SPI_MISO':targets.append(('U7','4'))
    else:targets.append(('U4','12' if net=='SPI_SCK' else '13'))
    out['spi'][net]=dict(total_trace_mm=round(g.total,3),paths={'.'.join(t):g.path((res,'2'),t) for t in targets})
   else:
    start=('J1',str({'SPI_SCK':5,'SPI_MOSI':6,'SPI_MISO':7}[net]));dest=(('R3' if name.startswith('core') else 'R5'),'2') if net=='SPI_MISO' else (('J4', '5' if net=='SPI_SCK' else '4') if name.startswith('core') else ('U1',('18' if net=='SPI_SCK' else '17') if name.startswith('e22') else ('5' if net=='SPI_SCK' else '4')))
    out['spi'][net]=dict(total_trace_mm=round(g.total,3),header_to_load=g.path(start,dest),probe_to_header=g.path(('TP'+str({'SPI_SCK':1,'SPI_MOSI':2,'SPI_MISO':3}[net]),'1'),start))
  if name=='carrier-rev-a':
   g=NetGraph(b,'/RADIO_5V')
   for s in SLOTS:out['power'][f'S{s}']=g.path(('U2','6'),(f'J{2*s-1}','2'),True)
   out['power']['external_to_efuse']=NetGraph(b,'/EXT_5V').path(('J9','1'),('U2','5'),True)
   for pin in ['11','12','14']:
    pad=next(a for a in fps['J11'].Pads() if a.GetNumber()==pin)
    assert pad.GetNetname().startswith('unconnected-'),('ADC back-power',pin,pad.GetNetname())
  else:
   dst=('U1','9') if name.startswith('e22') else ('U2','3') if name.startswith('e28') else ('U2','1')
   out['power']['slot_to_load']=NetGraph(b,'/SLOT_5V').path(('J1','2'),dst,True)
  for ref,t in plan['testpoints'].items():
   pos=xy(fps[ref].GetPosition());pad=next(iter(fps[ref].Pads()));out['testpoints'].append(dict(reference=ref,label=t['label'],net=pad.GetNetname(),xy=pos))
   if name=='carrier-rev-a':
    for x,y in SLOTS.values():assert not (x-12<pos[0]<x+72 and y-12<pos[1]<y+68),(ref,'hidden beneath installed card')
    assert not (104.39<pos[0]<125.39 and 9.46<pos[1]<60.46),(ref,'hidden beneath Pico')
  # Filled copper fraction is useful evidence, but does not by itself prove a return path.
  out['ground_area_mm2']={}
  for layer in [p.F_Cu,p.B_Cu]:out['ground_area_mm2'][b.GetLayerName(layer)]=round(sum(z.GetFilledPolysList(layer).Area()/1e12 for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='/GND' and z.IsOnLayer(layer)),2)
  drc=json.loads((ROOT/'validation'/name/'drc.json').read_text());out['drc_findings']={k:len(drc[k]) for k in ['violations','unconnected_items','schematic_parity']}
  result[name]=out
 (ROOT/'validation/layout-audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({n:{k:v[k] for k in ['sources','spi','power','drc_findings']} for n,v in result.items()},indent=2))
if __name__=='__main__':main()
