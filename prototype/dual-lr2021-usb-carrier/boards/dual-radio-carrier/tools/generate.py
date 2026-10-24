"""Create the carrier's schematic, libraries, PCB placement, and assembly tables."""

from __future__ import annotations

import argparse
import csv
import json

from cad import NAME, PROJECT, ROOT, flatten_pads, write_board, write_schematic


def passive(ref, value, at, nets, schematic, bulk=False, mpn=None):
    dx, size = (1.45,[1.2,1.8]) if bulk else (.95,[1.1,1.5])
    kind = 'C_1206' if bulk else 'R_0805' if ref.startswith('R') else 'C_0805'
    return {'ref':ref,'value':value,'at':at,'schematic':schematic,'footprint':kind,
            'mpn':mpn or ('RC0805FR-0710KL' if value=='10k' else 'RC0805FR-0733RL'),
            'outlines':[['F.Fab',[-1.6 if bulk else -1,-.8 if bulk else -.65,1.6 if bulk else 1,.8 if bulk else .65]],
                        ['F.CrtYd',[-2.3 if bulk else -1.8,-1.2,2.3 if bulk else 1.8,1.2]]],
            'ref_at':[0,-1.8],
            'pads':[{'number':str(i+1),'at':[(-dx if i==0 else dx),0],'size':size,'shape':'roundrect','net':net,
                     'function':str(i+1)} for i,net in enumerate(nets)]}


def socket(ref, at, pin_definitions, schematic, reverse=False):
    count=len(pin_definitions)
    horizontal=count==8
    axis=-1 if reverse else 1
    pads=[]
    for i,p in enumerate(pin_definitions):
        pads.append({'number':str(i+1),'at':[i*2.54,0] if horizontal else [0,axis*i*2.54],
                     'size':[1.8,1.8],'drill':1.04,'shape':'rect' if i==0 else 'circle',**p})
    outline=[-1.5,-1.35,19.3,1.35] if horizontal else [-1.35,axis*53.34-1.5,1.35,1.5] if reverse else [-1.35,-1.5,1.35,54.84]
    courtyard=[outline[0]-.3,outline[1]-.3,outline[2]+.3,outline[3]+.3]
    return {'ref':ref,'value':f'SSW-1{count:02d}-01-G-S','mpn':f'SSW-1{count:02d}-01-G-S',
            'socket':True,'at':at,'schematic':schematic,
            'footprint':f'Socket_1x{count:02d}_P2.54_'+('Horizontal' if horizontal else 'USB_Top'),
            'description':'Female socket, 2.54mm pitch, Samtec 1.04mm recommended finished hole; sample mating fit required',
            'datasheet':'https://suddendocs.samtec.com/prints/ssw-s.pdf',
            'ref_at':[8.89,-2.9] if horizontal else [0,3.0],
            'outlines':[['F.Fab',outline],['F.CrtYd',courtyard]],'pads':pads}


def design_data():
    controller=json.loads((PROJECT/'extra/references/controller-power/verified-controller.json').read_text())
    radio=json.loads((PROJECT/'extra/references/radio/verified-radio.json').read_text())
    assert controller['mechanical']['row_center_spacing']==22.86
    assert radio['header_geometry']['row_center_spacing_mm']==15.24
    selected={p['header_pin']:p['signal'] for p in controller['selected_radio_signals']}
    selected[18]='SPI_SCK_HOST'
    selected[17]='SPI_MOSI_HOST'
    components=[]
    for ref,header,x,sx in [('J1','P1',32.0,40.64),('J2','P2',9.14,106.68)]:
        pins=[]
        for p in controller['headers'][header]:
            net=selected.get(p['pin']) if header=='P1' else None
            if p['name']=='GND':
                net='GND'
            if header=='P1' and p['pin']==21:
                net='USB_5V'
            pins.append({'function':p['name'],'net':net,'module_pin':f'{header}.{p["pin"]}',
                         'pin_type':'power_out' if header=='P1' and p['pin'] in (21,22) else 'passive'})
        components.append(socket(ref,[x,60],pins,[sx,43.18],reverse=True))
    by_pin={p['pin']:p for p in radio['pins']}
    pin_map={}
    for label,upper,lower,origin,sx in [('A','J3','J4',[45,20],187.96),('B','J5','J6',[75,48],294.64)]:
        function_net={'3V3':'+3V3_RADIO','GND':'GND','DIO11':f'RADIO_{label}_DIO11',
                      'BUSY':f'RADIO_{label}_BUSY','RESET':f'RADIO_{label}_RESET_N',
                      'NSS':f'RADIO_{label}_CS_N','MISO':'SPI_MISO','MOSI':'SPI_MOSI','SCK':'SPI_SCK'}
        for ref,pin_order,offset,sy in [(upper,list(range(8,0,-1)),0,43.18),(lower,list(range(9,17)),15.24,86.36)]:
            pins=[]
            for number in pin_order:
                p=by_pin[number]
                pins.append({'function':p['signal'],'net':function_net.get(p['signal']),
                             'module_pin':str(number),'radio':label})
                pin_map[f'{ref}.{len(pins)}']={'radio':label,'module_pin':number,'function':p['signal'],
                                              'net':function_net.get(p['signal'])}
            components.append(socket(ref,[origin[0],origin[1]+offset],pins,[sx,sy]))
    components += [
        passive('R1','10k',[58,41],['RADIO_A_CS_N','+3V3_RADIO'],[187.96,137.16]),
        passive('R2','10k',[87,70],['RADIO_B_CS_N','+3V3_RADIO'],[294.64,137.16]),
        passive('R3','10k',[48,41],['RADIO_A_RESET_N','+3V3_RADIO'],[187.96,152.4]),
        passive('R4','10k',[76,70],['RADIO_B_RESET_N','+3V3_RADIO'],[294.64,152.4]),
        passive('R5','33R',[36,16.8],['SPI_SCK_HOST','SPI_SCK'],[40.64,119.38]),
        passive('R6','33R',[36,20.2],['SPI_MOSI_HOST','SPI_MOSI'],[106.68,119.38]),
    ]
    cap_bulk='C1206C106K3RACTU'
    cap_hf='C0805C104K5RACTU'
    components += [
        passive('C1','10uF 25V X7R',[43,62],['USB_5V','GND'],[40.64,165.1],True,cap_bulk),
        passive('C2','10uF 25V X7R',[58,62],['+3V3_RADIO','GND'],[106.68,165.1],True,cap_bulk),
        passive('C3','10uF 25V X7R',[43,14],['+3V3_RADIO','GND'],[187.96,172.72],True,cap_bulk),
        passive('C4','100nF 50V X7R',[49,14],['+3V3_RADIO','GND'],[187.96,187.96],False,cap_hf),
        passive('C5','10uF 25V X7R',[73,42],['+3V3_RADIO','GND'],[294.64,172.72],True,cap_bulk),
        passive('C6','100nF 50V X7R',[79,42],['+3V3_RADIO','GND'],[294.64,187.96],False,cap_hf),
    ]
    components.append({'ref':'U1','value':'TLV1117LV33DCYR','mpn':'TLV1117LV33DCYR',
                       'datasheet':'https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf',
                       'at':[51,56.5],'schematic':[106.68,142.24],'footprint':'SOT223_TabPin2',
                       'outlines':[['F.Fab',[-1.85,-3.35,1.85,3.35]],['F.CrtYd',[-4.4,-3.6,4.4,3.6]]],
                       'ref_at':[0,-4.5],
                       'pads':[{'number':'1','function':'GND','pin_type':'power_in','at':[-3.15,-2.3],
                                'size':[2,1.5],'shape':'rect','net':'GND'},
                               {'number':'2','function':'OUT_3V3','pin_type':'power_out','at':[-3.15,0],
                                'size':[2,1.5],'shape':'rect','net':'+3V3_RADIO'},
                               {'number':'3','function':'IN_USB','pin_type':'power_in','at':[-3.15,2.3],
                                'size':[2,1.5],'shape':'rect','net':'USB_5V'},
                               {'number':'2','function':'OUT_3V3','at':[3.15,0],
                                'size':[2,3.8],'shape':'rect','net':'+3V3_RADIO'}]})
    for ref,net,at,sch in [
        ('TP1','USB_5V',[35,9.2],[40.64,203.2]),
        ('TP2','+3V3_RADIO',[63,56.5],[106.68,203.2]),
        ('TP3','GND',[63,62],[187.96,210.82]),
        ('TP4','RADIO_A_DIO11',[65,14],[294.64,210.82]),
        ('TP5','RADIO_B_DIO11',[95,42],[365.76,210.82])]:
        components.append({'ref':ref,'value':net,'at':at,'schematic':sch,'footprint':'TestPoint_1.5mm',
                           'mpn':'PCB copper test pad','ref_at':[0,-1.8],
                           'pads':[{'number':'1','function':'TEST','at':[0,0],'size':[1.5,1.5],
                                    'shape':'circle','net':net}]})
    for i,at in enumerate([[3.5,3.5],[96.5,3.5],[3.5,71.5],[96.5,71.5]],1):
        components.append({'ref':f'H{i}','value':'M3 NPTH','at':at,'board_only':True,
                           'footprint':'MountingHole_3.2mm','ref_at':[0,-2.6],
                           'pads':[{'number':'','at':[0,0],'size':[3.2,3.2],'shape':'circle',
                                    'drill':3.2,'npth':True}]})
    # This ground contact lies beside a power spur. A solid join avoids isolated thermal spokes.
    j3=next(c for c in components if c['ref']=='J3')
    j3['footprint'] += '_SolidGND2'
    next(p for p in j3['pads'] if p['number']=='2')['zone_connect']=2
    labels=[
        {'text':'DUAL LR2021 USB TEST CARRIER','at':[65,3.5],'size':1.25},
        {'text':'REV A  /  ENGINEERING PROTOTYPE','at':[62,7],'size':.85},
        {'text':'USB-C','at':[20.5,3.5],'size':1.0},
        {'text':'RADIO A','at':[54,10],'size':1.2},
        {'text':'RADIO B','at':[84,38],'size':1.2},
        {'text':'3V3','at':[43,24],'size':.8},
        {'text':'3V3','at':[73,52],'size':.8},
        {'text':'2.4G','at':[68,20],'size':.8},
        {'text':'SUB-G','at':[68,35.24],'size':.8},
        {'text':'2.4G','at':[97,48],'size':.8},
        {'text':'SUB-G','at':[97,63.24],'size':.8},
        {'text':'3.3V RADIO SUPPLY','at':[53,48.5],'size':.9},
        {'text':'5V','at':[38,9.2],'size':.8},
        {'text':'3V3','at':[66,56.5],'size':.8},
        {'text':'GND','at':[63,65],'size':.8},
        {'text':'IRQ A','at':[69,14],'size':.8},
        {'text':'IRQ B','at':[94,36.8],'size':.8},
        {'text':'SOCKETS ON THIS SIDE','at':[53,72.5],'size':.9},
    ]
    return {'name':NAME,'revision':'A','size':[100,75],'edge_clearance':.5,
            'components':components,'labels':labels,
            'keepouts':[{'name':'ESP32 ANTENNA NO COPPER','bounds':[11.2,53,29.9,74.4]}],
            'module_outlines':[{'name':'ESP32-S3-DEV-KIT-N8R8-M','bounds':[7.86,1.61,33.26,64.91]},
                               {'name':'Core2021-HF-M A','bounds':[42.39,18,65.4,38]},
                               {'name':'Core2021-HF-M B','bounds':[72.39,46,95.4,66]}],
            'radio_rf_socket_pins':{'J3':['8'],'J4':['8'],'J5':['8'],'J6':['8']},
            'radio_pin_map':pin_map,
            'schematic_notes':[
                {'text':'USB-C CONTROLLER SOCKETS\nJ1 = vendor P1; J2 = vendor P2. USB end faces carrier top.\n22.86 mm between rows. Socket pin 1 is at antenna end.','at':[25.4,20.32]},
                {'text':'RADIO A SOCKETS\nTop view: upper row module pins 8..1 left to right; lower 9..16.\nAntennas connect to module IPEX4 ports at right.','at':[172.72,20.32]},
                {'text':'RADIO B SOCKETS\nSame wiring and orientation as Radio A.\nBoth sockets support either band and modulation.','at':[279.4,20.32]},
                {'text':'POWER\nUSB_5V is controller P1.21, downstream of its D1 diode.\nU1 output is separate from controller 3V3 pins.\nNo external power input. Radio allowance 300 mA.\nValidate USB allowance, controller D1 heat, and voltage drop.','at':[25.4,134.62],'size':1.1},
                {'text':'FIRMWARE\nCS defaults high. Reset and initialize both radios at boot.\nWait for each BUSY low before commands. One CS active at a time.\nStart SPI at 2 MHz. DIO11 is a radio pin name, not ESP32 GPIO11.\nKeep Wi-Fi/Bluetooth off for initial RF tests.','at':[25.4,220.98],'size':1.1},
                {'text':'RADIO CONTACTS\nRF header pins 1 and 16 and NC pin 6 have no carrier traces.\nDIO7 and DIO8 are reserved and unconnected in this revision.\nManufacturer pinout image is an underside view.\nSocket numbering here follows the documented TOP view.','at':[172.72,231.14],'size':1.1},
                {'text':'ENGINEERING PROTOTYPE\nNative KiCad ERC/DRC required; sample socket-fit checks pending.\nNo hardware or radio performance has been validated.\nDo not substitute generic LM/AMS1117 for ceramic-stable TLV1117LV.','at':[279.4,231.14],'size':1.1},
            ]}


def write_project(design):
    data={'meta':{'filename':f'{NAME}.kicad_pro','version':1},
          'board':{'design_settings':{'rules':{'min_clearance':.25,'min_track_width':.25,
                    'min_via_diameter':.65,'min_through_hole_diameter':.3,
                    'min_copper_edge_clearance':.5,'min_hole_clearance':.25,
                    'min_annular_width':.15},'meta':{'version':2}}},
          'net_settings':{'meta':{'version':3},'classes':[
              {'name':'Default','clearance':.25,'track_width':.25,'via_diameter':.65,'via_drill':.3,
               'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},
              {'name':'Power','clearance':.25,'track_width':.65,'via_diameter':.8,'via_drill':.4,
               'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],
              'netclass_assignments':{'/USB_5V':'Power','/+3V3_RADIO':'Power','/GND':'Power'}},
          'schematic':{'meta':{'version':1}},'text_variables':{'REVISION':'A'}}
    (ROOT/f'{NAME}.kicad_pro').write_text(json.dumps(data,indent=2)+'\n')
    (ROOT/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "{NAME}") (type "KiCad") '
                                  f'(uri "${{KIPRJMOD}}/{NAME}.pretty") (options "") (descr "Local carrier footprints")))\n')
    (ROOT/'sym-lib-table').write_text(f'(sym_lib_table (version 7) (lib (name "{NAME}") (type "KiCad") '
                                   f'(uri "${{KIPRJMOD}}/{NAME}.kicad_sym") (options "") (descr "Local carrier symbols")))\n')
    config=PROJECT/'.backplane.json'
    existing=json.loads(config.read_text()) if config.exists() else {}
    existing['project']=str((ROOT/f'{NAME}.kicad_pro').relative_to(PROJECT))
    config.write_text(json.dumps(existing,indent=2)+'\n')
    with (ROOT/'bom.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Reference','Quantity','Value','Manufacturer part number','Footprint','Assembly'])
        for c in design['components']:
            if c.get('board_only') or c['ref'].startswith('TP'):
                continue
            writer.writerow([c['ref'],1,c['value'],c.get('mpn',''),c['footprint'],'Solder to carrier'])
        writer.writerow(['MODULE_MCU',1,'ESP32-S3 controller','ESP32-S3-DEV-KIT-N8R8-M','J1 + J2','Plug in after soldering'])
        writer.writerow(['MODULE_A / MODULE_B',2,'LR2021 dual-band radio','Core2021-HF-M','J3+J4 / J5+J6','Plug in after soldering'])
    controller=json.loads((PROJECT/'extra/references/controller-power/verified-controller.json').read_text())
    with (ROOT/'gpio-map.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Signal','ESP32 GPIO','Controller header','Carrier socket'])
        for s in controller['selected_radio_signals']:
            writer.writerow([s['signal'],s['gpio'],f'{s["header"]}.{s["header_pin"]}',f'J1.{s["header_pin"]}'])
    with (ROOT/'radio-socket-map.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Carrier contact','Radio','Module pin','Function','Net'])
        for contact,p in design['radio_pin_map'].items():
            writer.writerow([contact,p['radio'],p['module_pin'],p['function'],p.get('net') or 'NC'])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--placement-only',action='store_true',help='Do not reuse existing routes')
    args=parser.parse_args()
    design=design_data()
    (ROOT/'design.json').write_text(json.dumps(design,indent=2)+'\n')
    write_project(design)
    write_schematic(design)
    route_file=ROOT/'build'/'routes.json'
    routes=json.loads(route_file.read_text()) if route_file.exists() and not args.placement_only else {}
    write_board(design,routes)
    print(f'Created canonical project in {ROOT}; {len(design["components"])} footprints')
