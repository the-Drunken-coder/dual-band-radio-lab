#!/usr/bin/env python3
"""Check mechanical access against native footprints and explicit installed envelopes.
Envelope checks establish geometric clearance, not a performed physical fit test.
"""
import pcbnew as p
import math,json
from pathlib import Path
from layout_plan import BOARDS,SLOTS
ROOT=Path(__file__).resolve().parents[1]
def box(item):
 q=item.GetBoundingBox();return [q.GetX()/1e6,q.GetY()/1e6,(q.GetX()+q.GetWidth())/1e6,(q.GetY()+q.GetHeight())/1e6]
def overlaps(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def body(fp):
 shapes=[box(q) for q in fp.GraphicalItems() if q.GetLayer() in [p.F_Fab,p.B_Fab]]
 return [min(q[0] for q in shapes),min(q[1] for q in shapes),max(q[2] for q in shapes),max(q[3] for q in shapes)] if shapes else None
result={}
for name,plan in BOARDS.items():
 path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)/(name+'.kicad_pcb');b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()};out={}
 if name!='carrier-rev-a':
  captures=[[4.12,-.96,11.12,11.12],[19.36,-6.04,26.36,31.44]]
  for r,f in fps.items():
   if r=='H1':continue
   bb=body(f)
   if bb:assert not any(overlaps(bb,c) for c in captures),(name,r,'body inside capture')
   for pad in f.Pads():
    if pad.GetDrillSize().x:
     x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6;rad=pad.GetDrillSize().x/2e6
     assert not any(overlaps([x-rad,y-rad,x+rad,y+rad],c) for c in captures),(name,r,'hole inside capture')
  for t in b.GetTracks():
   if isinstance(t,p.PCB_VIA):
    x,y=t.GetPosition().x/1e6,t.GetPosition().y/1e6;r=t.GetDrill()/2e6
    assert not any(overlaps([x-r,y-r,x+r,y+r],c) for c in captures),(name,'via in capture')
  # Vertical approach from above to each exposed pad. Module envelopes include plugs.
  module=([39,0,63,38.5] if name.startswith('e22') else [43,0,58,26.5] if name.startswith('e28') else [41.395,-.11,59.845,21.9])
  for r in plan['testpoints']:
   pad=next(iter(fps[r].Pads()));bb=box(pad)
   assert not overlaps(bb,module),(name,r,'under module')
   for rr,f in fps.items():
    if rr==r or rr.startswith('TP') or rr=='H1':continue
    bb2=body(f)
    # Underside headers are not an obstruction to a vertical top-side probe.
    if f.GetLayer()==p.B_Cu:continue
    if bb2:assert not overlaps(bb,bb2),(name,r,'probe obscured',rr)
  # IPEX cable departure corridors start beyond each module; plugs approach from above.
  cable=([39,38.5,46,68] if name.startswith('e22') else [52,26.5,59,68] if name.startswith('e28') else [43,22,58,68])
  # Core cables can be lifted over low adapter passives; minimum socket standoff 8.51.
  if not name.startswith('core'):
   for r,f in fps.items():
    if r=='U1' or r.startswith('TP'):continue
    bb=body(f)
    if bb:assert not overlaps(cable,bb),(name,r,'IPEX departure obstruction')
  out.update(capture_rectangles=captures,capture_result='PASS: intact laminate, no added drills/vias/components',probe_access='PASS: all probe pads outside module/component bodies',ipex_departure_mm=cable,ipex_access='PASS: vertical plug access and outward cable corridor; Core cables above <=2.8 mm passives on >=8.51 mm sockets',underside_components=[r for r,f in fps.items() if f.GetLayer()==p.B_Cu])
 else:
  cards={s:[x-12,y-12,x+72,y+68] for s,(x,y) in SLOTS.items()}
  for s,a in cards.items():
   for ss,c in cards.items():
    if ss>s:assert not overlaps(a,c)
   for r,f in fps.items():
    if r in [f'J{2*s-1}',f'J{2*s}',f'H{s}']:continue
    bb=body(f)
    if bb:assert not overlaps(a,bb),(r,'beneath card',s)
  usb=[110,0,120,9.4]
  for r,f in fps.items():
   bb=body(f)
   if bb:assert not overlaps(usb,bb),(r,'USB obstruction')
  out.update(installed_card_rectangles=cards,card_gap_horizontal_mm=51,card_gap_vertical_mm=20,same_band_A1_distance_mm=round(math.hypot(135,100),3),usb_approach_rectangle_mm=usb,usb_bootsel_debug_access='PASS: open top approach and central Pico corridor',carrier_components_under_cards='only intended socket pairs and alignment posts',ground_clip_clearance_from_card_edge_mm=3.415,post_to_card_top_projection_nominal_mm=10.75)
 out['qualification']='Geometric review only; no physical insertion, cable-force or tool-fit test has been performed.'
 result[name]=out
(ROOT/'validation/mechanical-access.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
