#!/usr/bin/env python3
"""Compile explicit Rev A placement and critical copper. No manufacturing output.
Run with KiCad's Python. General signals may be completed through Specctra,
then checked with KiCad DRC and the independent layout audit.
"""
import pcbnew as p
import math,json,sys,uuid
from xml.etree import ElementTree as ET
from pathlib import Path
from layout_plan import BOARDS,SLOTS
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
OUT=ROOT/'layout';OUT.mkdir(exist_ok=True)
def mm(x):return p.FromMM(x)
def v(x,y):return p.VECTOR2I(mm(x),mm(y))
def xy(pt):return pt.x/1e6,pt.y/1e6
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'radio-lab:'+s))
class Board:
 def __init__(self,name):
  self.name=name;self.plan=BOARDS[name];self.path=ROOT/('carrier-rev-a' if name=='carrier-rev-a' else 'adapters/'+name)
  self.parts=json.loads((self.path/'connectivity.json').read_text());self.b=p.BOARD();self.b.SetFileName(str(self.path/(name+'.kicad_pcb')))
  self.b.SetCopperLayerCount(2);self.b.GetDesignSettings().SetBoardThickness(mm(1.6))
  self.b.GetDesignSettings().m_MinClearance=mm(.15);self.b.GetDesignSettings().m_TrackMinWidth=mm(.15)
  self.b.GetDesignSettings().m_CopperEdgeClearance=mm(.3)
  self.nets={};self.fp={};self.critical=[]
  tree=ET.parse(ROOT/'validation'/name/'netlist.xml');pin_nets={}
  for n in tree.findall('./nets/net'):
   fullname=n.attrib['name'];key=fullname.lstrip('/')
   net=p.NETINFO_ITEM(self.b,fullname);self.b.Add(net);self.nets[key]=net
   for node in n.findall('node'):pin_nets[(node.attrib['ref'],node.attrib['pin'])]=key
  for a in self.parts:
   if not a['footprint']:continue
   ref=a['reference'];family,foot=a['footprint'].split(':');base=ROOT/'libraries/RadioLab.pretty' if family=='RadioLab' else LIB/(family+'.pretty')
   fp=p.FootprintLoad(str(base),foot);assert fp,a['footprint']
   fp.SetReference(ref);fp.SetValue(a['value']);fp.SetFPID(p.LIB_ID(family,foot))
   self.b.Add(fp);self.fp[ref]=fp
   x,y,ang=self.plan['parts'][ref];fp.SetPosition(v(x,y));fp.SetOrientationDegrees(ang)
   if name!='carrier-rev-a' and ref in ['J1','J2']:
    fp.Flip(fp.GetPosition(),True);fp.SetOrientationDegrees(180)
   fp.SetExcludedFromBOM(a['mpn'] in ['MECH-NPTH-3.4','PCB-PROBE-PAD'])
   for key,val in [('MPN',a['mpn']),('Supplier',a['supplier']),('Status','UNRELEASED'),('Source',a['source']),('Assembly',a['assembly'])]:
    fp.SetField(key,val);fp.GetField(key).SetVisible(False)
   fp.SetPath(p.KIID_PATH('/'+uid(name)+'/'+uid(name+ref)))
   fp.Reference().SetVisible(True);fp.Reference().SetTextSize(v(.8,.8));fp.Reference().SetTextThickness(mm(.12))
   fp.Value().SetVisible(False)
   for pad in fp.Pads():
    n=pin_nets.get((ref,pad.GetNumber()))
    if n:pad.SetNet(self.nets[n])
    pad.SetLocalClearance(mm(.15))
   # All parts are placed intentionally. Critical tracks are fixed as well.
   fp.SetLocked(True)
  x0,y0,x1,y1=self.plan['outline'];self.rect((x0,y0,x1,y1),p.Edge_Cuts,.05)
  self.text('REV A / 2L 2oz / REVIEW ONLY',((x0+x1)/2,y1-3),1.1)
  self.text(name,((x0+x1)/2,y0+3),1.2)
  # NPTH/post clearance is explicit on both copper layers.
  for ref,fp in self.fp.items():
   if ref.startswith('H'):
    x,y=xy(fp.GetPosition());self.keepout([(x+3.5*math.cos(i*math.pi/32),y+3.5*math.sin(i*math.pi/32)) for i in range(64)],copper=True,components=False)
  if name!='carrier-rev-a':
   # Capture laminate may carry copper, but never components or additional holes.
   for box in [(19.36,-6.04,26.36,31.44)]:
    self.keepout(self.corners(box),copper=False,components=True)
   self.text('A1 GND',(0,-4),.8);self.text('B1 BUSY',(30.48,-4),.8)
   self.text('HEADER PINS DOWN / IPEX OUT',(32,63),.9)
  else:
   for s,(x,y) in SLOTS.items():
    self.text({1:'915 LORA',2:'915 FLRC',3:'2.4 LORA',4:'2.4 FLRC'}[s],(x+32,y-17),2)
    self.rect((x-8,y-12,x+72,y+68),p.Dwgs_User,.15)
    self.text('A1 GND',(x,y-4),.8);self.text('B1 BUSY',(x+30.48,y-4),.8)
   self.rect((104.39,9.46,125.39,60.46),p.Dwgs_User,.15)
   self.text('PICO USB',(115,5),1.2);self.text('5V INPUT + / -',(116,205),1.5)
  for ref,t in self.plan['testpoints'].items():
   self.fp[ref].Reference().SetVisible(False)
   self.text(t['label'],(t['x'],t['y']-1.4),.8)
  self.sources()
 def corners(self,b):x0,y0,x1,y1=b;return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 def rect(self,b,layer,width):
  pts=self.corners(b)
  for a,c in zip(pts,pts[1:]+pts[:1]):
   s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*c));s.SetLayer(layer);s.SetWidth(mm(width));self.b.Add(s)
 def text(self,s,at,size):
  t=p.PCB_TEXT(self.b);t.SetText(s);t.SetPosition(v(*at));t.SetTextSize(v(size,size));t.SetTextThickness(mm(.12));t.SetLayer(p.F_SilkS);self.b.Add(t)
 def keepout(self,pts,copper=True,components=False):
  z=p.ZONE(self.b);z.SetIsRuleArea(True);ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
  z.SetDoNotAllowTracks(copper);z.SetDoNotAllowVias(copper or components);z.SetDoNotAllowPads(False);z.SetDoNotAllowZoneFills(copper);z.SetDoNotAllowFootprints(components)
  o=z.Outline();o.NewOutline()
  for x,y in pts:o.Append(mm(x),mm(y))
  self.b.Add(z)
 def pad(self,ref,num):return next(a for a in self.fp[ref].Pads() if a.GetNumber()==str(num))
 def pt(self,ref,num):return xy(self.pad(ref,num).GetPosition())
 def track(self,net,pts,width=.25,layer=p.F_Cu):
  for a,c in zip(pts,pts[1:]):
   if a==c:continue
   t=p.PCB_TRACK(self.b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(self.nets[net]);t.SetLocked(True);self.b.Add(t)
 def via(self,net,x,y):
  t=p.PCB_VIA(self.b);t.SetPosition(v(x,y));t.SetWidth(mm(.65));t.SetDrill(mm(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(self.nets[net]);t.SetLocked(True);self.b.Add(t)
 def zone(self,net,box,layer=p.F_Cu,priority=1):
  z=p.ZONE(self.b);z.SetLayer(layer);z.SetNet(self.nets[net]);z.SetLocalClearance(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2));z.SetAssignedPriority(priority)
  o=z.Outline();o.NewOutline()
  for x,y in self.corners(box):o.Append(mm(x),mm(y))
  self.b.Add(z)
 def sources(self):
  pairs=[('U5','21','R20'),('U5','20','R21'),('U4','14','R22')] if self.name=='carrier-rev-a' else [('J4','3','R3')] if self.name.startswith('core') else [('U1','16' if self.name.startswith('e22') else '3','R5')]
  for r,n,res in pairs:
   a,c=self.pt(r,n),self.pt(res,1);net=self.pad(r,n).GetNetname().lstrip('/')
   self.track(net,[a,(a[0]+1.1,a[1]),c] if r=='U5' else [a,c],.2);self.critical.append(dict(source=r+'.'+n,resistor=res,source_length_mm=math.dist(a,c)))
 def module_keepout(self,box):
  self.keepout(self.corners(box),False,False)
  z=self.b.Zones()[-1];z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
 def power(self):
  if self.name=='carrier-rev-a':
   # 6 mm distribution spine, 2 mm branches. Local package lead escapes widen immediately.
   self.track('RADIO_5V',[(113.25,181),(113.25,178.8)],.3)
   self.track('RADIO_5V',[(113.25,178.8),(115,177.75),(128,177.75)],1.5)
   self.track('RADIO_5V',[(128,177.75),(128,201),(240,201),(240,7)],6)
   # U2 IN strip exits below the device; the two opposing long power pads never share copper.
   self.track('EXT_5V',[(112.75,181),(112.75,183.3)],.3)
   self.track('EXT_5V',[(112.75,183.3),(112.75,184.5),(112.75,191)],1.5)
   self.track('EXT_5V',[(112.75,191),(119,191),(119,195)],4)
   self.track('RADIO_5V',[(240,7),(17,7)],6)
   self.track('RADIO_5V',[(240,100),(17,100)],6)
   for s,(x,y) in SLOTS.items():
    # Top feeder lane is above both header rows and post pattern.
    self.track('RADIO_5V',[(x-3,7 if y==25 else 100),(x-3,y+2.54),(x,y+2.54)],2)
    self.track('RADIO_5V',[(x,y+2.54),(x,y+5.08)],1.5)
   # No power vias are required in this top-layer distribution tree.
   return
  self.track('SLOT_5V',[self.pt('J1',2),self.pt('J1',3)],1.5)
  if self.name.startswith('e22'):
   self.track('SLOT_5V',[self.pt('J1',2),(-2,2.54),(-2,-7),(66.5,-7),(66.5,6)],1.5)
   self.track('SLOT_5V',[(66.5,6),self.pt('U1',9)],1.5)
   self.track('SLOT_5V',[self.pt('U1',9),self.pt('U1',10)],1.5)
   # Bulk ties around the outside of the module, never beneath its RF assembly.
   self.track('SLOT_5V',[(66.5,6),(66.5,44),(49.9,44),self.pt('C1',1)],1.5)
  else:
   self.track('SLOT_5V',[self.pt('J1',2),(-2,2.54),(-2,34),(3,34),(3,45.5)],1.5)
   if self.name.startswith('e28'):
    self.track('SLOT_5V',[(3,45.5),self.pt('C1',1),self.pt('C8',1)],1.5)
    self.track('SLOT_5V',[(3,45.5),(3,61.5),self.pt('C5',1)],1.5)
    self.track('SLOT_5V',[self.pt('U2',3),(6.8625,44.3),self.pt('C1',1)],.6)
    self.track('SLOT_5V',[self.pt('U2',2),(5.5,42),(5.5,44.8),self.pt('C1',1)],.25)
    self.track('SW',[self.pt('U2',5),(10.6,42),self.pt('L1',1)],.55)
    self.track('SW',[self.pt('C4',2),(11,37.5),(11,40.5),(10.5,40.5),(10.6,42)],.3)
    self.track('BST',[self.pt('U2',6),(9.1375,39),(8.625,38.4875),(8.625,37.5),self.pt('C4',1)],.25)
    self.track('RADIO_3V3',[self.pt('L1',2),(15.155,47),self.pt('C2',1),self.pt('C3',1),self.pt('C7',1)],1.5)
    self.track('RADIO_3V3',[self.pt('L1',2),(18.5,41.6),(18.5,34),(33,34),(33,-5),(43,-5),(43,1.5)],1.5)
    self.track('RADIO_3V3',[(43,1.5),self.pt('U1',1)],.6)
    # Kelvin FB from output capacitor, on the quiet side of the IC and outside SW.
    self.track('RADIO_3V3',[self.pt('U2',1),(5,41.05),(5,38.7),(3,38.7),(3,53),(11,56),self.pt('C7',1)],.25,p.B_Cu)
    for x,y in [self.pt('U2',1),self.pt('C7',1)]:self.via('RADIO_3V3',x,y)
    for x,y in [(9.8,44.3),(9.8,46.5),(9.8,47.6),(9.8,50.2),(9.8,51.3),(9.8,52.4),(9.8,53.5),(9.8,54.6)]:self.via('GND',x,y)
   else:
    self.track('SLOT_5V',[(3,45.5),(-.5,45.5),(-.5,38),self.pt('C1',1)],1.5)
    self.track('SLOT_5V',[self.pt('U2',1),(6.8,40.5),(7.4,40.5),(7.4,35),(2.025,35),self.pt('C1',1)],.5)
    self.track('SLOT_5V',[self.pt('U2',3),(6.8625,44.8),(3,44.8)],.5)
    self.track('RADIO_3V3',[self.pt('U2',5),(10.2,41.05),(14,41.05),self.pt('C2',1)],.6)
    self.track('RADIO_3V3',[self.pt('C2',1),(15,38),(15,34),(37,34),(37,23),(43,23),self.pt('J3',8)],1.5)
 def ground(self):
  x0,y0,x1,y1=self.plan['outline'];self.zone('GND',(x0+.5,y0+.5,x1-.5,y1-.5),p.B_Cu,0);self.zone('GND',(x0+.5,y0+.5,x1-.5,y1-.5),p.F_Cu,0)
  # Direct ground stitching adjacent to every ground SMD pad; position reviewed by DRC.
  for fp in self.fp.values():
   for pad in fp.Pads():
    if pad.GetNetname()!='/GND' or pad.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
    x,y=xy(pad.GetPosition());sx,sy=xy(pad.GetSize())
    # Via is outside paste opening; route a short ground connection.
    center=fp.GetPosition().x/1e6
    if fp.GetReference()=='U1' and self.name.startswith(('e22','e28')):center+=12 if self.name.startswith('e22') else 7.5
    dx=1 if x>=center else -1
    vx=x+dx*(sx/2+.6)
    if vx>self.plan['outline'][2]-.7:
     vx=x;self.via('GND',vx,y+sy/2+.6);self.track('GND',[(x,y),(vx,y+sy/2+.6)],.35);continue
    self.via('GND',vx,y);self.track('GND',[(x,y),(vx,y)],.35)
 def save(self):
  p.SaveBoard(self.b.GetFileName(),self.b)
  # SWIG exposes no stackup copper thickness setter. Persist native stackup explicitly.
  f=Path(self.b.GetFileName());s=f.read_text();pos=s.index('(setup')+len('(setup')
  stack='''
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.07))
      (layer "dielectric 1" (type "core") (thickness 1.44) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.07))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "ENIG") (dielectric_constraints no))
'''
  s=s[:pos]+stack+s[pos:];f.write_text(s)
  project=self.path/(self.name+'.kicad_pro');pr=json.loads(project.read_text());pr['board']={'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_hole_clearance':.25,'min_copper_edge_clearance':.3},'drc_exclusions':[]}}
  pr['net_settings']={'classes':[{'name':'Default','clearance':.15,'track_width':.25,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25,'wire_width':6,'bus_width':12}], 'meta':{'version':4}}
  project.write_text(json.dumps(pr,indent=2)+'\n')
  self.b=p.LoadBoard(str(f));p.ExportSpecctraDSN(self.b,str(OUT/(self.name+'.dsn')))
  (OUT/(self.name+'-critical.json')).write_text(json.dumps(self.critical,indent=2)+'\n')

def main():
 for name in sys.argv[1:] or BOARDS:
  b=Board(name)
  # No signal or power routing below the radio bodies; grounded shield beneath.
  if name.startswith('e22'):b.module_keepout((40.5,1,61.5,38))
  if name.startswith('e28'):
   b.module_keepout((44.5,1,56.5,12.2))
   b.keepout(b.corners((40,13,61,29.5)),True,False)
  b.power();b.ground();b.save();print(name,len(b.fp),'footprints',flush=True)
if __name__=='__main__':main()
