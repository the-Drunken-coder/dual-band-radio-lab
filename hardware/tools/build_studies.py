#!/usr/bin/env python3
"""Build editable electrical studies. These are not fabrication-ready designs."""

import csv
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = {}
BOARDS = []


def uid(text):
    return str(uuid5(NAMESPACE_URL, "dual-band-radio-lab/rev-a-study/" + text))


def q(text):
    return json.dumps(str(text), ensure_ascii=False)


def symbol(name, pins):
    """Pins are physical pin numbers, names and KiCad electrical types."""
    SYMBOLS[name] = pins
    return name


def symbol_text(name, library=False):
    pins = SYMBOLS[name]
    title = name if library else "RadioLab:" + name
    rows = (len(pins) + 1) // 2
    height = (rows + 1) * 2.54
    body = [f'(symbol {q(title)} (pin_names (offset 0.762)) (in_bom yes) (on_board yes)',
            '(property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))',
            f'(property "Value" {q(name)} (at 0 2.54 0) (effects (font (size 1.27 1.27))))',
            '(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            f'(symbol {q(name + "_0_1")} (rectangle (start -15.24 0) (end 15.24 {-height})'
            ' (stroke (width 0.254) (type default)) (fill (type background))))',
            f'(symbol {q(name + "_1_1")}']
    for i, (number, pname, ptype) in enumerate(pins):
        left = i < rows
        row = i if left else i - rows
        x, angle = (-20.32, 0) if left else (20.32, 180)
        y = -(row + 1) * 2.54
        body.append(f'(pin {ptype} line (at {x} {y} {angle}) (length 5.08) '
                    f'(name {q(pname)} (effects (font (size 1.016 1.016)))) '
                    f'(number {q(number)} (effects (font (size 1.016 1.016)))))')
    return "\n".join(body) + "))"


E22 = symbol("E22_900M30S", [(str(i), name, typ) for i, name, typ in [
    (1, "GND", "power_in"), (2, "GND", "power_in"), (3, "GND", "power_in"),
    (4, "GND", "power_in"), (5, "GND", "power_in"), (6, "RXEN", "input"),
    (7, "TXEN", "input"), (8, "DIO2", "bidirectional"), (9, "VCC", "power_in"),
    (10, "VCC", "power_in"), (11, "GND", "power_in"), (12, "GND", "power_in"),
    (13, "DIO1", "bidirectional"), (14, "BUSY", "output"), (15, "NRST", "input"),
    (16, "MISO", "output"), (17, "MOSI", "input"), (18, "SCK", "input"),
    (19, "NSS", "input"), (20, "GND", "power_in"), (21, "ANT", "passive"),
    (22, "GND", "power_in")]])
E28 = symbol("E28_2G4M27S", [(str(i), name, typ) for i, name, typ in [
    (1, "VCC", "power_in"), (2, "GND", "power_in"), (3, "MISO_TX", "output"),
    (4, "MOSI_RX", "input"), (5, "SCK_RTSN", "input"), (6, "NSS_CTS", "input"),
    (7, "GND", "power_in"), (8, "RX_EN", "input"), (9, "TX_EN", "input"),
    (10, "GND", "power_in"), (11, "NRESET", "input"), (12, "BUSY", "output"),
    (13, "DIO1", "bidirectional"), (14, "DIO2", "bidirectional"),
    (15, "DIO3", "bidirectional"), (16, "GND", "power_in")]])
CORE = symbol("Core2021_HF_M", [(str(i), name, typ) for i, name, typ in [
    (1, "ANT_2G4", "passive"), (2, "GND", "power_in"), (3, "DIO11", "bidirectional"),
    (4, "DIO8", "bidirectional"), (5, "DIO7", "bidirectional"), (6, "NC", "no_connect"),
    (7, "GND", "power_in"), (8, "3V3", "power_in"), (9, "BUSY", "output"),
    (10, "RESET", "input"), (11, "MISO", "tri_state"), (12, "MOSI", "input"),
    (13, "SCK", "input"), (14, "NSS", "input"), (15, "GND", "power_in"),
    (16, "ANT_SUBG", "passive")]])

PICO_NAMES = ["GP0", "GP1", "GND", "GP2", "GP3", "GP4", "GP5", "GND", "GP6", "GP7",
              "GP8", "GP9", "GND", "GP10", "GP11", "GP12", "GP13", "GND", "GP14", "GP15",
              "GP16", "GP17", "GND", "GP18", "GP19", "GP20", "GP21", "GND", "GP22", "RUN",
              "GP26", "GP27", "AGND", "GP28", "ADC_VREF", "3V3_OUT", "3V3_EN", "GND", "VSYS", "VBUS"]
PICO = symbol("Pico_2_header_map", [(str(i), n, "bidirectional" if n.startswith("GP") else
    "power_out" if n == "3V3_OUT" else "power_out" if n == "VBUS" else "power_in" if n in ["GND", "AGND", "VSYS"]
    else "input" if n in ["RUN", "3V3_EN"] else "passive") for i, n in enumerate(PICO_NAMES, 1)])
BUCK = symbol("AP63203WU_7", [("1", "FB", "input"), ("2", "EN", "input"),
    ("3", "VIN", "power_in"), ("4", "GND", "power_in"), ("5", "SW", "power_out"), ("6", "BST", "passive")])
LDO = symbol("AP2112K_3_3TRG1", [("1", "VIN", "power_in"), ("2", "GND", "power_in"),
    ("3", "EN", "input"), ("4", "NC", "no_connect"), ("5", "VOUT", "power_out")])
for count in [2, 8, 10]:
    symbol(f"Header_1x{count}", [(str(i), str(i), "passive") for i in range(1, count + 1)])
for name in ["Capacitor_value_only", "Resistor_value_only", "Inductor_value_only"]:
    symbol(name, [("1", "1", "passive"), ("2", "2", "passive")])
symbol("External_power_declaration", [("1", "POWER", "power_out")])

# Proposed interface. Its numbering is a design choice, not a vendor pin assignment.
SLOT_A = ["GND", "SLOT_5V", "SLOT_5V", "GND", "SPI_SCK", "SPI_MOSI", "SPI_MISO", "CS_N", "RESET_N", "GND"]
SLOT_B = ["BUSY", "IRQ", "TX_EN", "RX_EN", "AUX0", "AUX1", "IOREF_3V3", "GND"]
GPIO = {0: "S1_IRQ", 1: "S1_BUSY", 2: "S2_IRQ", 3: "S2_BUSY", 4: "SPI_MISO", 5: "S1_CS_N",
        6: "SPI_SCK", 7: "SPI_MOSI", 8: "S3_IRQ", 9: "S3_BUSY", 10: "S4_IRQ", 11: "S4_BUSY",
        12: "S2_CS_N", 13: "S3_CS_N", 14: "S4_CS_N", 15: "EXP_CS_N", 16: "EXP_RESET_N", 17: "IO_OE_N"}
EXPANDER = symbol("MCP23S17_SO", [(str(i), n, t) for i,n,t in
    [(i+1, "GPB"+str(i), "bidirectional") for i in range(8)] +
    [(9,"VDD","power_in"),(10,"VSS","power_in"),(11,"CS_N","input"),(12,"SCK","input"),
     (13,"SI","input"),(14,"SO","tri_state"),(15,"A0","input"),(16,"A1","input"),(17,"A2","input"),
     (18,"RESET_N","input"),(19,"INTB","open_collector"),(20,"INTA","open_collector")] +
    [(21+i,"GPA"+str(i),"bidirectional") for i in range(8)]])
TRANS = symbol("SN74LVC8T245_PW", [(str(i),n,t) for i,n,t in
    [(1,"VCCA","power_in"),(2,"DIR","input")] + [(3+i,"A"+str(i+1),"bidirectional") for i in range(8)] +
    [(11,"GND","power_in"),(12,"GND","power_in"),(13,"GND","power_in")] +
    [(14+i,"B"+str(8-i),"bidirectional") for i in range(8)] +
    [(22,"OE_N","input"),(23,"VCCB","power_in"),(24,"VCCB","power_in")]])
TRANS1 = symbol("SN74LVC1T45_DBV", [("1","VCCA","power_in"),("2","GND","power_in"),
    ("3","A","bidirectional"),("4","B","bidirectional"),("5","DIR","input"),("6","VCCB","power_in")])
EFUSE = symbol("TPS259470L_RPW", [(str(i),n,t) for i,n,t in [(1,"EN_UVLO","input"),(2,"OVLO","input"),
    (3,"AUXOFF","open_collector"),(4,"FLT_N","open_collector"),(5,"IN","power_in"),(6,"OUT","power_out"),
    (7,"DVDT","passive"),(8,"GND","power_in"),(9,"ILM","passive"),(10,"ITIMER","passive")]])
MOS = symbol("DMG2305UX", [("1","G","input"),("2","S","passive"),("3","D","passive")])
symbol("Mechanical", [])
symbol("Probe_point", [("1", "PROBE", "passive")])
symbol("Capacitor_polarized", [("1", "+", "passive"), ("2", "-", "passive")])
symbol("Header_1x20", [(str(i), str(i), "passive") for i in range(1,21)])

# Each entry is a selected orderable part, not a value-only placeholder.
PASSIVES = {
 "22": ("RC0603FR-0722RL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 22 ohm 1% 0.1 W; yageo-rc.pdf"),
 "100nF": ("GRM188R71H104KA93D", "Capacitor_SMD:C_0603_1608Metric", "Murata; 100 nF 50 V X7R 10%"),
 "10nF": ("GRM188R71H103KA01D", "Capacitor_SMD:C_0603_1608Metric", "Murata; 10 nF 50 V X7R 10%"),
 "1uF": ("GRM21BR71C105KA01L", "Capacitor_SMD:C_0805_2012Metric", "Murata; 1 uF 16 V X7R 10%"),
 "10uF": ("GRM32ER61C106KA12L", "Capacitor_SMD:C_1210_3225Metric", "Murata; 10 uF 16 V X5R 10%"),
 "22uF": ("C3225X7R1E226M250AB", "Capacitor_SMD:C_1210_3225Metric", "TDK; 22 uF 25 V X7R 20%; sources/online-evidence.md"),
 "220uF": ("EEEFK1A221P", "RadioLab:Panasonic_FK_E_8x6.2", "Panasonic; 220 uF 10 V 20%; panasonic-fk.pdf"),
 "4.7uH": ("XAL5030-472MEC", "Inductor_SMD:L_Coilcraft_XAL5030-XXX", "Coilcraft; 4.7 uH 20%, 6.7 A Isat, 40 mOhm max; xal50xx.pdf"),
 "100": ("RC0603FR-07100RL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "1k": ("RC0603FR-071KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "10k": ("RC0603FR-0710KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "100k": ("RC0603FR-07100KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "267k": ("RC0603FR-07267KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "715": ("RC0603FR-07715RL", "Resistor_SMD:R_0603_1608Metric", "Yageo RC0603; 1% 0.1 W"),
 "340k 0.1%": ("RT0603BRD07340KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RT0603; 0.1% 25 ppm/K"),
 "100k 0.1%": ("RT0603BRD07100KL", "Resistor_SMD:R_0603_1608Metric", "Yageo RT0603; 0.1% 25 ppm/K"),
}
FOOTPRINTS = {"AP63203WU-7":"Package_TO_SOT_SMD:TSOT-23-6", "AP2112K-3.3TRG1":"Package_TO_SOT_SMD:SOT-23-5",
 "DMG2305UX-7":"Package_TO_SOT_SMD:SOT-23", "MCP23S17-E/SO":"Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm",
 "SN74LVC8T245PWR":"Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "SN74LVC1T45DBVR":"Package_TO_SOT_SMD:SOT-23-6",
 "TPS259470LRPWR":"RadioLab:TPS25947_RPW0010A", "E22-900M30S":"RadioLab:E22_900M30S",
 "E28-2G4M27S":"RadioLab:E28_2G4M27S", "1757242":"Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal"}



class Study:
    def __init__(self, path, title):
        self.path = ROOT / path
        self.name = self.path.name
        self.title = title
        self.parts = []
        self.items = []
        self.uuid = uid(self.name)
        self.notes = []
        self.used = set()
        BOARDS.append(self)

    def text(self, text, x, y, size=1.27):
        self.items.append(f'(text {q(text)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left bottom)) (uuid {q(uid(self.name+text))}))')

    def part(self, ref, sym, value, x, y, nets, mpn="UNSELECTED", supplier="", purpose="", assembly="factory", source="", footprint=None, on_board=True):
        if footprint is None:
            footprint = FOOTPRINTS.get(mpn, "")
        x, y = round(round(x / 1.27) * 1.27, 5), round(round(y / 1.27) * 1.27, 5)
        self.used.add(sym)
        part_id = uid(self.name + ref)
        props = [f'(property "Reference" {q(ref)} (at {x} {y-5.08} 0) (effects (font (size 1.27 1.27))))',
                 f'(property "Value" {q(value)} (at {x} {y-2.54} 0) (effects (font (size 1.27 1.27))))']
        for name, val in [("Footprint", footprint), ("MPN", mpn), ("Supplier", supplier), ("Status", "UNRELEASED"), ("Source", source), ("Assembly", assembly)]:
            props.append(f'(property {q(name)} {q(val)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
        self.items.append(f'(symbol (lib_id {q("RadioLab:"+sym)}) (at {x} {y} 0) (unit 1) (in_bom {"no" if mpn in ["MECH-NPTH-3.4","PCB-PROBE-PAD"] else "yes"}) (on_board {"yes" if on_board else "no"}) (dnp no) '
            f'(uuid {q(part_id)}) {" ".join(props)} '
            f'(instances (project {q(self.name)} (path {q("/"+self.uuid)} (reference {q(ref)}) (unit 1)))))')
        rows = (len(SYMBOLS[sym]) + 1) // 2
        for i, (number, pname, typ) in enumerate(SYMBOLS[sym]):
            left = i < rows
            row = i if left else i-rows
            px, py = round(x + (-20.32 if left else 20.32), 5), round(y+(row+1)*2.54, 5)
            net = nets.get(number)
            if net is None:
                self.items.append(f'(no_connect (at {px} {py}) (uuid {q(uid(part_id+number+"nc"))}))')
            else:
                ex = round(px + (-7.62 if left else 7.62), 5)
                self.items.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid {q(uid(part_id+number+"wire"))}))')
                angle, just = (0, "right") if left else (0, "left")
                self.items.append(f'(label {q(net)} (at {ex} {py} {angle}) (effects (font (size 1.016 1.016)) (justify {just} bottom)) (uuid {q(uid(part_id+number+"label"))}))')
        self.parts.append(dict(reference=ref, value=value, symbol=sym, mpn=mpn, supplier=supplier,
                               quantity=1, purpose=purpose, assembly=assembly, source=source,
                               footprint=footprint, nets=nets))

    def passive(self, ref, sym, value, x, y, a, b, purpose):
        key=value.split(",")[0].split(" reference")[0].split(" candidate")[0]
        mpn, footprint, source=PASSIVES[key]
        self.part(ref, "Capacitor_polarized" if key=="220uF" else sym+"_value_only", key, x, y, {"1": a, "2": b}, mpn=mpn,
                  purpose=purpose, source=source, footprint=footprint)

    def socket(self, ref, count, x, y, nets, purpose, male=False):
        mpn = f"TSW-1{count:02d}-07-G-S" if male else f"SSQ-1{count:02d}-01-G-S"
        fp = f"RadioLab:{'TSW' if male else 'SSQ'}_1x{count}"
        self.part(ref, f"Header_1x{count}", mpn, x, y, nets, mpn=mpn, purpose=purpose,
                  source="Samtec tsw/ssq-drawing.pdf and footprint.pdf", footprint=fp)

    def series(self, ref, x, y, source_net, bus_net, location):
        mpn, footprint, source = PASSIVES['22']
        self.part(ref, 'Resistor_value_only', '22', x, y, {'1': source_net, '2': bus_net},
                  mpn=mpn, footprint=footprint, source=source,
                  purpose='Source-series termination; place immediately at '+location+' before any bus branch; no long stubs',
                  assembly='Initially 22 ohm; configurable 0 ohm alternate RC0603JR-070RL in same footprint; verify by oscilloscope/IBIS during bring-up; DNP opens signal')

    def power_declaration(self, ref, net, x, y):
        before = len(self.items)
        self.part(ref, "External_power_declaration", "POWER DECLARATION: " + net, x, y, {"1": net}, purpose="ERC power-source model")
        self.items[before] = self.items[before].replace('(in_bom yes) (on_board yes)', '(in_bom no) (on_board no)')
        self.parts.pop()

    def slots(self, kind):
        self.socket("J1", 10, 65, 45, {str(i):n for i,n in enumerate(SLOT_A,1)}, "Slot A", male=True)
        unused = {"core": {"TX_EN", "RX_EN", "IOREF_3V3"}, "e22": {"AUX1"}, "e28": {"IOREF_3V3"}}[kind]
        self.socket("J2", 8, 65, 85, {str(i): None if n in unused or n=="AUX1" else n for i,n in enumerate(SLOT_B,1)}, "Slot B", male=True)
        self.power_declaration("#FLG01", "SLOT_5V", 65, 115)
        self.power_declaration("#FLG02", "GND", 185, 115)

    def finish(self):
        from layout_plan import BOARDS as LAYOUTS
        for i, (ref, t) in enumerate(LAYOUTS[self.name]['testpoints'].items()):
            carrier = self.name == 'carrier-rev-a'
            x = 70 + (i % 8)*130 if carrier else 440 + (i % 2)*105
            y = 615 + (i // 8)*25 if carrier else 45 + (i // 2)*32
            self.part(ref, 'Probe_point', t['label'], x, y, {'1':t['net']},
                mpn='5011' if t['clip'] else 'PCB-PROBE-PAD',
                footprint='TestPoint:TestPoint_Keystone_5010-5014_Multipurpose' if t['clip'] else 'RadioLab:Probe_Pad_D0.6mm' if t['net']=='SW' else 'RadioLab:Probe_Pad_D1.0mm',
                purpose='Accessible ground clip' if t['clip'] else 'Inline probe pad, no source-side stub',
                assembly='Factory fitted' if t['clip'] else 'Bare copper PCB feature; no purchased component',
                source='Keystone 5011 drawing and manufacturer category 748' if t['clip'] else ('0.6 mm round exposed copper pad on the local switch node' if t['label']=='SW' else '1 mm round exposed copper pad'))
        self.path.mkdir(parents=True, exist_ok=True)
        self.text("REV A LAYOUT REVIEW. NOT FOR FABRICATION.", 20.32, 15.24, 2)
        self.text(self.title, 20.32, 22.86, 1.6)
        self.text("Local labels connect equal names. NC marks deliberate unused module pins.\nSelected parts: see BOM, FOOTPRINT_REVIEW.md and ASSEMBLY_NOTES.md.", 20.32, 30.48)
        text = f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(self.uuid)}) (paper {q("A0" if self.name=="carrier-rev-a" else "A2")}) '
        text += f'(title_block (title {q(self.title)}) (date "2026-09-17") (rev "A-schematic") (comment 1 "SCHEMATIC REVIEW - NOT FOR FABRICATION")) '
        text += '(lib_symbols ' + "\n".join(symbol_text(n) for n in sorted(self.used)) + ')\n'
        text += "\n".join(self.items) + '\n(embedded_fonts no))\n'
        (self.path / (self.name + '.kicad_sch')).write_text(text)
        project = self.path / (self.name + '.kicad_pro')
        settings = json.loads(project.read_text()) if project.exists() else {}
        settings['meta'] = {'filename':self.name+'.kicad_pro','version':1}
        project.write_text(json.dumps(settings, indent=2)+'\n')
        rel = '../libraries' if self.path.parent == ROOT else '../../libraries'
        (self.path / 'sym-lib-table').write_text(f'(sym_lib_table (version 7) (lib (name "RadioLab") (type "KiCad") (uri "${{KIPRJMOD}}/{rel}/RadioLab.kicad_sym") (options "") (descr "Unreleased electrical study symbols")))\n')
        (self.path / 'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "RadioLab") (type "KiCad") (uri "${{KIPRJMOD}}/{rel}/RadioLab.pretty") (options "") (descr "Schematic footprint selections")))\n')
        fp_entries = [f'(lib (name "RadioLab") (type "KiCad") (uri "${{KIPRJMOD}}/{rel}/RadioLab.pretty") (options "") (descr "Rev A"))']
        for family in sorted({p['footprint'].split(':')[0] for p in self.parts if p['footprint'] and not p['footprint'].startswith('RadioLab:')}):
            fp_entries.append(f'(lib (name "{family}") (type "KiCad") (uri "${{KICAD10_FOOTPRINT_DIR}}/{family}.pretty") (options "") (descr "KiCad standard library"))')
        (self.path / 'fp-lib-table').write_text('(fp_lib_table (version 7) '+ ' '.join(fp_entries)+')\n')
        columns = ['reference', 'value', 'mpn', 'supplier', 'quantity', 'purpose', 'assembly', 'footprint', 'source']
        with (self.path / 'BOM.csv').open('w', newline='') as f:
            w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(p for p in self.parts if p["mpn"] not in ["MECH-NPTH-3.4","PCB-PROBE-PAD"])
        (self.path / 'connectivity.json').write_text(json.dumps(self.parts,indent=2)+'\n')
        (self.path / 'fabrication').mkdir(exist_ok=True)
        (self.path / 'fabrication' / 'DO_NOT_FABRICATE.md').write_text('# No fabrication release\n\nPCB layout review only. No Gerbers, drills, placement files or ordering release. See `hardware/DESIGN_REVIEW.md`.\n')


def adapter(kind):
    names = {"e22":"e22-900m30s-rev-a", "core":"core2021-hf-m-rev-a", "e28":"e28-2g4m27s-rev-a"}
    b=Study('adapters/'+names[kind], {'e22':'915 MHz LoRa card', 'core':'915 MHz FLRC socket adapter', 'e28':'2.4 GHz LoRa or FLRC card, same hardware'}[kind])
    b.slots(kind)
    if kind == 'e22':
        nets = {str(i): 'GND' for i in [1,2,3,4,5,11,12,20,22]}
        nets.update({'6':'RX_EN','7':'TX_EN','8':'AUX0','9':'SLOT_5V','10':'SLOT_5V','13':'IRQ','14':'BUSY','15':'RESET_N','16':'SPI_MISO_SRC','17':'SPI_MOSI','18':'SPI_SCK','19':'CS_N'})
        b.part('U1',E22,'E22-900M30S',185,45,nets,'E22-900M30S','C411294',purpose='915 MHz LoRa',source='E22-M manual section 3.3, PDF pages 10-11')
        b.passive('C1','Capacitor','220uF',65,140,'SLOT_5V','GND','Local TX transient reservoir; 10 V polarized')
        b.passive('C2','Capacitor','22uF',185,140,'SLOT_5V','GND','Local supply decoupling')
        b.passive('C3','Capacitor','100nF',305,140,'SLOT_5V','GND','Local ceramic decoupling')
        b.text('Module pad 21 ANT: NC, use module IPEX. Both pads 9 and 10 are VCC. H1 is the mandatory alignment-post hole.\nDIO2 is AUX0 for a local test point only; do not connect it to a Pico GPIO.\nAUX1 is reserved. DIO3 is internal TCXO control, configured to 2.2 V.',140,100)
    elif kind == 'e28':
        nets={'1':'RADIO_3V3','2':'GND','3':'SPI_MISO_SRC','4':'SPI_MOSI','5':'SPI_SCK','6':'CS_N','7':'GND','8':'RX_EN','9':'TX_EN','10':'GND','11':'RESET_N','12':'BUSY','13':'IRQ','14':'AUX0','16':'GND'}
        b.part('U1',E28,'E28-2G4M27S',185,45,nets,'E28-2G4M27S','C411312',purpose='2.4 GHz lane; mandatory IPEX antenna variant',assembly='Factory: populate IPEX; selector link in manual 9.2 IPEX position, PCB-antenna branch open; no user rework',source='E28 manual section 3, PDF page 5')
        b.part('U2',BUCK,'AP63203WU-7',305,45,{'1':'RADIO_3V3','2':'SLOT_5V','3':'SLOT_5V','4':'GND','5':'SW','6':'BST'},'AP63203WU-7',purpose='5 V to 3.3 V buck, 2 A part rating',source='DS41326 Rev 3-2, pages 2, 13, 15, 17')
        b.power_declaration('#FLG03', 'RADIO_3V3', 305, 115)
        b.passive('L1','Inductor','4.7uH',65,140,'SW','RADIO_3V3','6.7 A saturation, 40 mOhm maximum DCR')
        b.passive('C1','Capacitor','22uF',185,140,'SLOT_5V','GND','Buck input capacitor')
        b.passive('C2','Capacitor','22uF',305,140,'RADIO_3V3','GND','Buck output capacitor 1')
        b.passive('C3','Capacitor','22uF',65,170,'RADIO_3V3','GND','Buck output capacitor 2')
        b.passive('C4','Capacitor','100nF',185,170,'BST','SW','Bootstrap capacitor')
        b.passive('C5','Capacitor','220uF',305,170,'SLOT_5V','GND','Local slot input bulk; eFuse controlled ramp on carrier')
        b.passive('C6','Capacitor','100nF',305,200,'RADIO_3V3','GND','Module ceramic decoupling')
        b.passive('C7','Capacitor','22uF',65,185,'RADIO_3V3','GND','Buck output capacitor 3; DC-bias margin')
        b.passive('C8','Capacitor','22uF',185,185,'SLOT_5V','GND','Buck input capacitor 2; DC-bias margin')
        b.text('ASSEMBLY VARIANT: IPEX ONLY. Selector MUST match manual section 9.2 right image.\nMCP23S17 controls TX_EN/RX_EN before RF commands. No automatic RX/TX modes.\nBuck PCB layout must follow figure 25, 2 oz copper on both layers.',140,100)
    else:
        nets={'2':'GND','3':'IRQ','4':'AUX0','7':'GND','8':'RADIO_3V3','9':'BUSY','10':'RESET_N','11':'SPI_MISO_SRC','12':'SPI_MOSI','13':'SPI_SCK','14':'CS_N','15':'GND'}
        b.part('U1',CORE,'Core2021-HF-M plug-in',185,45,nets,'Core2021-HF-M','Waveshare SKU 34523',purpose='915 MHz FLRC',assembly='User plugs into factory-soldered sockets',source='Waveshare Core2021-HF schematic, sheet 1, U2', on_board=False)
        b.socket('J3',8,65,165,{str(i):nets.get(str(i)) for i in range(1,9)},'Core socket pins 1-8')
        b.socket('J4',8,185,165,{str(i):nets.get(str(i+8)) for i in range(1,9)},'Core socket pins 9-16')
        b.part('U2',LDO,'AP2112K-3.3TRG1',305,45,{'1':'SLOT_5V','2':'GND','3':'SLOT_5V','5':'RADIO_3V3'},'AP2112K-3.3TRG1',purpose='Local 3.3 V supply',source='DS39724 Rev 2-2, pages 1-3')
        for ref,val,x,y,rail in [('C1','22uF',65,140,'SLOT_5V'),('C2','22uF',185,140,'RADIO_3V3'),('C3','100nF',305,140,'RADIO_3V3'),('C4','22uF',305,170,'RADIO_3V3')]:
            b.passive(ref,'Capacitor',val,x,y,rail,'GND','LDO/module ceramic decoupling')
        b.text('U1 represents the plug-in module, not a soldered module footprint.\nSocket contacts for module pins 1, 5, 6 and 16 are isolated.\nTX_EN/RX_EN slot contacts unused. No external RF switch added.\nJ3/J4: 15.24 mm row spacing; top/bottom numbering in FOOTPRINT_REVIEW.md.',140,100)
    source_location={'e22':'U1 MISO pad 16', 'e28':'U1 MISO pad 3', 'core':'J4 pin 3, nearest accessible Core U1 MISO pin 11'}[kind]
    b.series('R3' if kind=='core' else 'R5',305,75,'SPI_MISO_SRC','SPI_MISO',source_location)
    b.text('MISO: source -> 22R -> slot A7. Fit 0R option; scope/IBIS verify.\nPlace at module output/socket, before shared bus. No long stubs.',20.32,252,1.1)
    pull_rail='IOREF_3V3' if kind=='e22' else 'RADIO_3V3'
    b.passive('R1','Resistor','10k',65,210,pull_rail,'CS_N','Default deselected, radio-domain pull-up')
    b.passive('R2','Resistor','10k',185,210,pull_rail,'RESET_N','Default released; PA/LNA stay disabled and CS stays high until host initializes')
    if kind in ['e22','e28']:
        for ref,net,x in [('R3','TX_EN',65),('R4','RX_EN',185)]:
            b.passive(ref,'Resistor','10k',x,235,net,'GND','Default PA/LNA inactive')
    if kind=='e22': b.power_declaration('#FLG03','IOREF_3V3',305,115)
    b.text('KEYED SLOT: H1 engages the carrier M3 x 25 post before electrical contact.\nAll headers and passives factory fitted. No user soldering or antenna-selector rework.\nPower declarations describe power arriving through the slot and buck output after L1.\nLayout authorized; no fabrication release. See DESIGN_REVIEW.md.',20.32,267)
    b.part('H1','Mechanical','M3 alignment hole',305,235,{},'MECH-NPTH-3.4',purpose='Required daughtercard post clearance; 3.4 mm NPTH, 7 mm keepout',source='radio-slot-v0.1.md; Accu SSCF-M3-25-A2 dimensions',footprint='RadioLab:Alignment_M3_3.4mm')
    b.finish()


def carrier():
    b=Study('carrier-rev-a','Four-slot carrier: protected external 5 V / 4 A, isolated GPIO')
    nets={}
    for i,name in enumerate(PICO_NAMES,1):
        if name.startswith('GP'):
            signal=GPIO.get(int(name[2:]))
            nets[str(i)] = 'P_'+signal if signal else None
        elif name in ['GND','AGND']: nets[str(i)]='GND'
        elif name=='3V3_OUT': nets[str(i)]='PICO_3V3'
        elif name=='VSYS': nets[str(i)]='PICO_VSYS'
        elif name=='VBUS': nets[str(i)]='USB_VBUS'
    b.part('U1',PICO,'Pico 2 with headers, SC1632',65,45,nets,'SC1632',purpose='Removable controller',assembly='User plug-in',source='Pico 2 datasheet sections 5.2 and 5.5',on_board=False)
    b.socket('J10',20,65,115,{str(i):nets.get(str(i)) for i in range(1,21)},'Pico left socket, physical pins 1-20')
    b.socket('J11',20,65,165,{str(i):nets.get(str(i+20)) for i in range(1,21)},'Pico right socket, physical pins 21-40')
    for slot,x,y in [(1,185,45),(2,305,45),(3,185,135),(4,305,135)]:
        def net(n):
            if n=='SLOT_5V': return 'RADIO_5V'
            if n in ['GND','IOREF_3V3'] or n.startswith('SPI_'): return n
            if slot==2 and n in ['TX_EN','RX_EN']: return None
            if n in ['AUX0','AUX1']: return None
            return f'S{slot}_{n}'
        b.socket('J'+str(slot*2-1),10,x,y,{str(i):net(n) for i,n in enumerate(SLOT_A,1)},f'S{slot} slot A')
        b.socket('J'+str(slot*2),8,x,y+38.1,{str(i):net(n) for i,n in enumerate(SLOT_B,1)},f'S{slot} slot B')
    b.part('J9','Header_1x2','5 V / 4 A INPUT',425,45,{'1':'EXT_5V','2':'GND'},'1757242',purpose='12 A keyed input header; mating 1757019 plug',source='Phoenix Contact 1757242 manufacturer page')
    b.part('U2',EFUSE,'TPS259470LRPWR',545,45,{'1':'UVLO','2':'OVLO','5':'EXT_5V','6':'RADIO_5V','7':'DVDT','8':'GND','9':'ILIM'},'TPS259470LRPWR',purpose='Reverse polarity/current, OV/UV, current limit and inrush; latch off',source='SLVSFC9C May 2026 sections 5,7,8')
    b.part('Q1',MOS,'DMG2305UX-7',665,45,{'1':'USB_VBUS','2':'PICO_VSYS','3':'RADIO_5V'},'DMG2305UX-7',purpose='Pico documented external-source ORing: D=external, S=VSYS, G=VBUS',source='Pico 2 figure 9; DMG2305UX DS36196')
    b.part('U3',LDO,'AP2112K-3.3TRG1',425,105,{'1':'RADIO_5V','2':'GND','3':'RADIO_5V','5':'IOREF_3V3'},'AP2112K-3.3TRG1',purpose='External-only radio interface and expander supply',source='AP2112 DS39724')
    exp={'9':'IOREF_3V3','10':'GND','11':'EXP_CS_N','12':'SPI_SCK','13':'SPI_MOSI','14':'EXP_MISO_SRC','15':'GND','16':'GND','17':'GND','18':'EXP_RESET_N'}
    exp.update({str(i):f'S{i}_RESET_N' for i in range(1,5)})
    exp.update({str(21+i):net for i,net in enumerate(['S1_TX_EN','S1_RX_EN','S3_TX_EN','S3_RX_EN','S4_TX_EN','S4_RX_EN'])})
    b.part('U4',EXPANDER,'MCP23S17-E/SO',545,120,exp,'MCP23S17-E/SO',purpose='Noncritical reset and pre-command RF-switch state',source='Microchip DS20001952C; SOIC pin table')
    for ref,x,direction,signals in [('U5',185,'PICO_3V3',['SPI_SCK','SPI_MOSI','S1_CS_N','S2_CS_N','S3_CS_N','S4_CS_N','EXP_CS_N','EXP_RESET_N']),
        ('U6',305,'GND',['S1_BUSY','S1_IRQ','S2_BUSY','S2_IRQ','S3_BUSY','S3_IRQ','S4_BUSY','S4_IRQ'])]:
        ns={'1':'PICO_3V3','2':direction,'11':'GND','12':'GND','13':'GND','22':'P_IO_OE_N','23':'IOREF_3V3','24':'IOREF_3V3'}
        for i,n in enumerate(signals):
            ns[str(3+i)]='P_'+n
            ns[str(21-i)]=n+'_SRC' if ref=='U5' and n in ['SPI_SCK','SPI_MOSI'] else n
        b.part(ref,TRANS,'SN74LVC8T245PWR',x,250,ns,'SN74LVC8T245PWR',purpose='Dual-supply power-off isolation; fixed direction',source='SCES584D May 2026 sections 4,7.3.3,8.3')
    b.part('U7',TRANS1,'SN74LVC1T45DBVR',425,250,{'1':'PICO_3V3','2':'GND','3':'P_SPI_MISO','4':'SPI_MISO','5':'GND','6':'IOREF_3V3'},'SN74LVC1T45DBVR',purpose='MISO radio-to-Pico power-off isolation',source='SCES515N June 2024 sections 4 and 7')
    b.series('R20',185,305,'SPI_SCK_SRC','SPI_SCK','U5 B1 pin 21')
    b.series('R21',305,305,'SPI_MOSI_SRC','SPI_MOSI','U5 B2 pin 20')
    b.series('R22',665,135,'EXP_MISO_SRC','SPI_MISO','U4 SO pin 14')
    b.text('R20/R21: immediately after U5 SCK/MOSI outputs. R22: at U4 SO before shared MISO.\n22R initial; 0R population option. Verify by oscilloscope/IBIS. No long stubs.\nEach radio card has its own MISO source resistor before slot A7.',425,300)
    b.power_declaration('#FLG01','EXT_5V',425,190)
    b.power_declaration('#FLG02','GND',545,190)
    b.power_declaration('#FLG03','PICO_VSYS',665,190)
    # Decoupling and bias networks occupy a regular schematic grid, never a PCB placement.
    parts=[('R1','Resistor','267k','EXT_5V','UVLO','UVLO upper'),('R2','Resistor','100k','UVLO','GND','UVLO lower'),
        ('R3','Resistor','340k 0.1%','EXT_5V','OVLO','OVLO upper'),('R4','Resistor','100k 0.1%','OVLO','GND','OVLO lower'),
        ('R5','Resistor','715','ILIM','GND','4.66 A nominal current limit'),('C1','Capacitor','10nF','DVDT_C','GND','25 ms nominal 5 V ramp'),
        ('C2','Capacitor','1uF','EXT_5V','GND','Input HF bypass'),('C3','Capacitor','220uF','RADIO_5V','GND','Protected bus bulk'),
        ('C4','Capacitor','22uF','RADIO_5V','GND','U3 input bypass'),('C5','Capacitor','22uF','IOREF_3V3','GND','U3 output bypass'),
        ('C6','Capacitor','100nF','IOREF_3V3','GND','U4 bypass'),('C7','Capacitor','100nF','PICO_3V3','GND','U5 VCCA bypass'),
        ('C8','Capacitor','100nF','IOREF_3V3','GND','U5 VCCB bypass'),('C9','Capacitor','100nF','PICO_3V3','GND','U6 VCCA bypass'),
        ('C10','Capacitor','100nF','IOREF_3V3','GND','U6 VCCB bypass'),('C11','Capacitor','100nF','PICO_3V3','GND','U7 VCCA bypass'),
        ('C12','Capacitor','100nF','IOREF_3V3','GND','U7 VCCB bypass'),('R6','Resistor','10k','PICO_3V3','P_IO_OE_N','Interface disabled during Pico reset'),
        ('R7','Resistor','100k','USB_VBUS','GND','P-MOS gate discharge with USB absent'),('R8','Resistor','10k','EXP_RESET_N','GND','Expander held reset if interface disabled'),
        ('R9','Resistor','10k','IOREF_3V3','EXP_CS_N','Expander deselect default'),('R10','Resistor','100k','SPI_MISO','GND','Defined idle shared MISO'),
        ('R11','Resistor','1k','RADIO_5V','GND','Bus discharge: 5 mA at 5 V'),('R12','Resistor','1k','IOREF_3V3','GND','Logic discharge: 3.3 mA'),
        ('R13','Resistor','10k','P_EXP_RESET_N','GND','Boot-safe expander reset')]
    for i,(ref,sym,val,a,c,purpose) in enumerate(parts):
        b.passive(ref,sym,val,65+(i%7)*110,340+(i//7)*32,a,c,purpose)
    for i,n in enumerate(['S1_CS_N','S2_CS_N','S3_CS_N','S4_CS_N','EXP_CS_N']):
        b.passive('R'+str(14+i),'Resistor','10k',65+i*110,480,'PICO_3V3','P_'+n,'Pico-side deselect before enabling U5')
    b.passive('R19','Resistor','100',615,480,'DVDT','DVDT_C','TI recommended series damping for CdVdt above 10 nF including tolerance')
    b.text('18/26 GPIO used; eight spare including GP26-28, all physically NC.\nBUSY/IRQ/CS are direct GPIO through fixed-direction isolation, not expander GPIO.\nKEY: captive M3 x 25 alignment post, see radio-slot-v0.1.md.\nU4 GPA0..5 = S1/S3/S4 TX,RX pairs; GPB0..3 = S1..4 RESET_N.\nNo autonomous duty-cycled RX or automatic TX/RX transitions on Ebyte cards.',20.32,535)
    b.text('USB-only: Q1 off; RADIO_5V and IOREF_3V3 unpowered. External power: U2 -> radios and Q1 -> VSYS.\nQ1 orientation is intentional: body diode from RADIO_5V toward VSYS. Pico onboard D1 blocks USB backfeed.\n#FLG01/#FLG02 model the external supply; #FLG03 models real Q1/onboard USB-D1 ORing output.\nU2 AUXOFF/FLT/ITIMER unused per datasheet. Leave ITIMER open for fastest current limiting.',425,535)
    for i in range(4):
        b.part('H'+str(i+1),'Mechanical','Captive M3 x 25 alignment post',65+i*150,565,{},'SSCF-M3-25-A2',purpose='S'+str(i+1)+' anti-offset and anti-reversal post, installed from below',source='Accu product datasheet 642039; radio-slot-v0.1.md',footprint='RadioLab:Alignment_M3_3.4mm')
        b.part('MP'+str(i+1),'Mechanical','M3 captive-post clamp nut',665,245+i*18,{},'HPN-M3-A2',purpose='Factory threadlocked clamp nut for H'+str(i+1),source='Accu HPN-M3-A2, 5.5 mm AF, 2.4 mm thick',on_board=False)
    b.part('MP5','Mechanical','External cable mating plug',665,320,{},'1757019',purpose='Mates J9; 18 AWG or larger supply pair, factory terminated',source='Phoenix Contact manufacturer mating table',on_board=False)
    b.finish()


def main():
    carrier()
    for kind in ['e22','core','e28']: adapter(kind)
    (ROOT/'libraries').mkdir(exist_ok=True)
    (ROOT/'libraries'/'RadioLab.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n' + '\n'.join(symbol_text(n, True) for n in sorted(SYMBOLS)) + ')\n')
    (ROOT/'gpio-map.json').write_text(json.dumps({str(k):{'net':v,'pico_pin':PICO_NAMES.index('GP'+str(k))+1} for k,v in GPIO.items()},indent=2)+'\n')
    (ROOT/'radio-slot-v0.1.json').write_text(json.dumps({'status':'LAYOUT_REVIEW_NO_FABRICATION','A':dict(enumerate(SLOT_A,1)),'B':dict(enumerate(SLOT_B,1))},indent=2)+'\n')
    print('Created four Rev-A schematics. No PCB/fabrication generation.')


if __name__=='__main__':
    main()
