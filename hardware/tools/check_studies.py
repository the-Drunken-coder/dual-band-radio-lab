#!/usr/bin/env python3
"""Verify critical connections in KiCad's exported XML, independently of the generator."""
import csv,json,math
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def read(board):
 tree=ET.parse(ROOT/'validation'/board/'netlist.xml');pins={};members={}
 for net in tree.findall('./nets/net'):
  name=net.attrib['name'].lstrip('/');nodes={(n.attrib['ref'],n.attrib['pin']) for n in net.findall('node')};members[name]=nodes
  for p in nodes:
   assert p not in pins,(board,p)
   pins[p]=name
 return pins,members
def expect(board,connections,isolated=()):
 pins,members=read(board)
 for p,n in connections.items():assert pins.get(p)==n,(board,p,n,pins.get(p))
 for p in isolated:assert p not in pins or members[pins[p]]=={p},(board,'NC connected',p)
 checks.append(dict(board=board,checked_pin_assignments=len(connections),isolated_pins=len(isolated),result='PASS'))
def numbered(ref,m):return {(ref,str(p)):n for p,n in m.items()}
def check_series(board, ref, source_net, bus_net, drivers, bus_pins):
 pins,members=read(board)
 assert source_net!=bus_net
 assert pins[(ref,'1')]==source_net and pins[(ref,'2')]==bus_net,(board,ref,'resistor endpoints')
 assert members[source_net]==set(drivers)|{(ref,'1')},(board,ref,'source bypass or extra stub')
 assert members[bus_net]==set(bus_pins)|{(ref,'2')},(board,ref,'bus topology')
 path=ROOT/'carrier-rev-a' if board=='carrier-rev-a' else ROOT/'adapters'/board
 row=next(r for r in csv.DictReader((path/'BOM.csv').open()) if r['reference']==ref)
 assert row['value']=='22' and row['mpn']=='RC0603FR-0722RL'
 assert row['footprint']=='Resistor_SMD:R_0603_1608Metric'
 assert 'RC0603JR-070RL' in row['assembly'] and 'oscilloscope/IBIS' in row['assembly']
 # Check the native schematic export too, so a stale BOM cannot validate a wrong value.
 tree=ET.parse(ROOT/'validation'/board/'netlist.xml')
 comp=next(c for c in tree.findall('./components/comp') if c.attrib['ref']==ref)
 assert comp.findtext('value')=='22' and comp.findtext('footprint')==row['footprint']
 checks.append(dict(board=board,check='source-series topology and population',reference=ref,result='PASS'))
def main():
 e22={p:'GND' for p in [1,2,3,4,5,11,12,20,22]};e22.update({6:'RX_EN',7:'TX_EN',8:'AUX0',9:'SLOT_5V',10:'SLOT_5V',13:'IRQ',14:'BUSY',15:'RESET_N',16:'SPI_MISO_SRC',17:'SPI_MOSI',18:'SPI_SCK',19:'CS_N'})
 expect('e22-900m30s-rev-a',numbered('U1',e22),[('U1','21'),('J2','6')])
 e28=numbered('U1',{1:'RADIO_3V3',2:'GND',3:'SPI_MISO_SRC',4:'SPI_MOSI',5:'SPI_SCK',6:'CS_N',7:'GND',8:'RX_EN',9:'TX_EN',10:'GND',11:'RESET_N',12:'BUSY',13:'IRQ',14:'AUX0',16:'GND'})
 e28.update(numbered('U2',{1:'RADIO_3V3',2:'SLOT_5V',3:'SLOT_5V',4:'GND',5:'SW',6:'BST'}));e28.update({('L1','1'):'SW',('L1','2'):'RADIO_3V3',('C4','1'):'BST',('C4','2'):'SW'})
 expect('e28-2g4m27s-rev-a',e28,[('U1','15'),('J2','6'),('J2','7')])
 core=numbered('U1',{2:'GND',3:'IRQ',4:'AUX0',7:'GND',8:'RADIO_3V3',9:'BUSY',10:'RESET_N',11:'SPI_MISO_SRC',12:'SPI_MOSI',13:'SPI_SCK',14:'CS_N',15:'GND'})
 core.update(numbered('U2',{1:'SLOT_5V',2:'GND',3:'SLOT_5V',5:'RADIO_3V3'}))
 for p in range(1,17):
  n=core.get(('U1',str(p)))
  if n:core[('J3' if p<=8 else 'J4',str(p if p<=8 else p-8))]=n
 expect('core2021-hf-m-rev-a',core,[(r,str(p)) for r,p in [('U1',1),('U1',5),('U1',6),('U1',16),('U2',4),('J2',3),('J2',4),('J2',6),('J2',7)]])
 signals={1:'S1_IRQ',2:'S1_BUSY',4:'S2_IRQ',5:'S2_BUSY',6:'SPI_MISO',7:'S1_CS_N',9:'SPI_SCK',10:'SPI_MOSI',11:'S3_IRQ',12:'S3_BUSY',14:'S4_IRQ',15:'S4_BUSY',16:'S2_CS_N',17:'S3_CS_N',19:'S4_CS_N',20:'EXP_CS_N',21:'EXP_RESET_N',22:'IO_OE_N'}
 carrier=numbered('U1',{p:'P_'+n for p,n in signals.items()});carrier.update(numbered('U1',{36:'PICO_3V3',39:'PICO_VSYS',40:'USB_VBUS',33:'GND'}))
 for p in range(1,41):
  n=carrier.get(('U1',str(p)))
  if n:carrier[('J10' if p<=20 else 'J11',str(p if p<=20 else p-20))]=n
 carrier.update(numbered('Q1',{1:'USB_VBUS',2:'PICO_VSYS',3:'RADIO_5V'}));carrier.update(numbered('U2',{1:'UVLO',2:'OVLO',5:'EXT_5V',6:'RADIO_5V',7:'DVDT',8:'GND',9:'ILIM'}))
 carrier.update({('C1','1'):'DVDT_C',('C1','2'):'GND',('R19','1'):'DVDT',('R19','2'):'DVDT_C'})
 carrier.update(numbered('U3',{1:'RADIO_5V',2:'GND',3:'RADIO_5V',5:'IOREF_3V3'}))
 carrier.update(numbered('U4',{9:'IOREF_3V3',10:'GND',11:'EXP_CS_N',12:'SPI_SCK',13:'SPI_MOSI',14:'EXP_MISO_SRC',15:'GND',16:'GND',17:'GND',18:'EXP_RESET_N'}))
 for i in range(1,5):carrier[('U4',str(i))]=f'S{i}_RESET_N'
 for i,n in enumerate(['S1_TX_EN','S1_RX_EN','S3_TX_EN','S3_RX_EN','S4_TX_EN','S4_RX_EN']):carrier[('U4',str(21+i))]=n
 for ref,direction,names in [('U5','PICO_3V3',['SPI_SCK','SPI_MOSI','S1_CS_N','S2_CS_N','S3_CS_N','S4_CS_N','EXP_CS_N','EXP_RESET_N']),('U6','GND',['S1_BUSY','S1_IRQ','S2_BUSY','S2_IRQ','S3_BUSY','S3_IRQ','S4_BUSY','S4_IRQ'])]:
  carrier.update(numbered(ref,{1:'PICO_3V3',2:direction,11:'GND',12:'GND',13:'GND',22:'P_IO_OE_N',23:'IOREF_3V3',24:'IOREF_3V3'}))
  for i,n in enumerate(names):carrier[(ref,str(3+i))]='P_'+n;carrier[(ref,str(21-i))]=n+'_SRC' if ref=='U5' and n in ['SPI_SCK','SPI_MOSI'] else n
 carrier.update(numbered('U7',{1:'PICO_3V3',2:'GND',3:'P_SPI_MISO',4:'SPI_MISO',5:'GND',6:'IOREF_3V3'}))
 for slot in range(1,5):
  a,b='J'+str(slot*2-1),'J'+str(slot*2)
  carrier.update(numbered(a,{1:'GND',2:'RADIO_5V',3:'RADIO_5V',4:'GND',5:'SPI_SCK',6:'SPI_MOSI',7:'SPI_MISO',8:f'S{slot}_CS_N',9:f'S{slot}_RESET_N',10:'GND'}))
  carrier.update(numbered(b,{1:f'S{slot}_BUSY',2:f'S{slot}_IRQ',7:'IOREF_3V3',8:'GND'}))
  if slot!=2:carrier.update(numbered(b,{3:f'S{slot}_TX_EN',4:f'S{slot}_RX_EN'}))
 spare=[24,25,26,27,29,31,32,34]
 isolated=[('U1',str(p)) for p in spare]+[('J11',str(p-20)) for p in spare]+[(f'J{2*s}',str(p)) for s in range(1,5) for p in [5,6]]+[('J4','3'),('J4','4')]
 expect('carrier-rev-a',carrier,isolated)
 for ref,signal,pin,receiver in [('R20','SPI_SCK','21','12'),('R21','SPI_MOSI','20','13')]:
  check_series('carrier-rev-a',ref,signal+'_SRC',signal,[('U5',pin)],[('U4',receiver)]+[(f'J{2*i-1}','5' if signal=='SPI_SCK' else '6') for i in range(1,5)])
 check_series('carrier-rev-a','R22','EXP_MISO_SRC','SPI_MISO',[('U4','14')],[('U7','4'),('R10','1')]+[(f'J{2*i-1}','7') for i in range(1,5)])
 for board,ref,drivers in [('e22-900m30s-rev-a','R5',[('U1','16')]),('e28-2g4m27s-rev-a','R5',[('U1','3')]),('core2021-hf-m-rev-a','R3',[('U1','11'),('J4','3')])]:
  check_series(board,ref,'SPI_MISO_SRC','SPI_MISO',drivers,[('J1','7')])
 assert len(signals)==18 and len(spare)==8
 for bom in ROOT.rglob('BOM.csv'):
  for row in csv.DictReader(bom.open()):assert row['mpn'] and row['mpn']!='UNSELECTED',(bom,row['reference'])
 for erc in ROOT.glob('validation/*/erc.json'):
  data=json.loads(erc.read_text());assert not [v for sh in data['sheets'] for v in sh['violations']],erc
 # Post geometry is an interface specification, not a routed-board check.
 # Normal +/- one pitch: hole center moves 2.54 mm, far beyond radial clearance.
 clearance=(3.5-2.9)/2
 assert 2.54>clearance
 # On 180-degree reversal, rows swap; asymmetric post x=7.62 maps to x=22.86.
 assert abs((30.48-7.62)-7.62)>clearance
 # 1.6 +/-10% PCB, 25 mm screw with conservative 0.3 mm length allowance.
 post_min=24.7-1.76
 first_contact_max=8.51+.25+2.54+.25+5.84+.20
 assert post_min>first_contact_max
 checks.append(dict(check='mechanical post first-engagement margin',margin_mm=round(post_min-first_contact_max,2),result='PASS',scope='normal straight mating, solid capture zones required; no board or physical fit test'))
 report=dict(scope='Schematic netlist, ERC, BOM and interface arithmetic. No PCB validation.',checks=checks,result='PASS')
 (ROOT/'validation/connectivity-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
