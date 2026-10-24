"""Small KiCad writer shared by the carrier generator and geometry checker."""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

import sexpdata
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
NAME = "dual-radio-carrier"
NS = uuid.UUID("942776c8-0f9b-4828-874a-716f9bff7930")


def uid(name):
    return str(uuid.uuid5(NS, str(name)))


def q(value):
    return json.dumps(str(value), ensure_ascii=False)


def board_net_name(component, pin):
    if pin.get('npth'):
        return None
    if pin.get('net'):
        return '/' + pin['net']
    return f'unconnected-({component["ref"]}-{pin.get("function",pin["number"])}-Pad{pin["number"]})'


def logical_net(name):
    if not name or name.startswith('unconnected-('):
        return None
    return name.removeprefix('/')


def num(value):
    return f"{value:.5f}".rstrip("0").rstrip(".") if value else "0"


def items(node, key):
    return [i for i in node[1:] if isinstance(i, list) and i and str(i[0]) == key]


def item(node, key, default=None):
    found = items(node, key)
    return found[0] if found else default


def parse(path):
    return sexpdata.loads(Path(path).read_text())


def effects(size=1, thickness=0.15, justify="", hide=False):
    return (
        f"(effects (font (size {num(size)} {num(size)}) (thickness {num(thickness)}))"
        f"{' (justify ' + justify + ')' if justify else ''}{' hide' if hide else ''})"
    )


def transform(x, y, angle, dx, dy):
    a = math.radians(angle)
    return (round(x + dx * math.cos(a) - dy * math.sin(a), 5),
            round(y + dx * math.sin(a) + dy * math.cos(a), 5))


def pad_shape(pad):
    x, y = pad["x"], pad["y"]
    w, h = pad["size"]
    shape = pad.get("shape", "circle")
    if shape == "circle":
        return Point(x, y).buffer(w / 2, quad_segs=16)
    result = box(-w / 2, -h / 2, w / 2, h / 2)
    if shape in ("oval", "roundrect"):
        radius = min(w, h) / 2 if shape == "oval" else min(w, h) * 0.2
        result = box(-w / 2 + radius, -h / 2 + radius,
                     w / 2 - radius, h / 2 - radius).buffer(radius, quad_segs=12)
    result = affinity.rotate(result, pad.get("angle", 0))
    return affinity.translate(result, x, y)


def segment_shape(segment):
    return LineString([segment["start"], segment["end"]]).buffer(
        segment["width"] / 2, quad_segs=12
    )


def flatten_pads(design):
    result = []
    for component in design["components"]:
        for pin in component["pads"]:
            x, y = transform(*component["at"], component.get("angle", 0), *pin["at"])
            result.append({**pin, "ref": component["ref"], "x": x, "y": y,
                           "angle": component.get("angle", 0),
                           "layers": [0, 1] if pin.get("drill") else [0]})
    return result


def line(x1, y1, x2, y2, layer="F.SilkS", width=0.15, fp=False):
    tag = "fp_line" if fp else "gr_line"
    return (f"({tag} (start {num(x1)} {num(y1)}) (end {num(x2)} {num(y2)}) "
            f"(stroke (width {num(width)}) (type default)) (layer {q(layer)}))")


def rect(x1, y1, x2, y2, layer="F.SilkS", width=0.15, fp=False):
    return "\n".join(line(*a, *b, layer, width, fp) for a, b in [
        ((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
        ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))])


def footprint(component, net_ids, library=False):
    ref = component["ref"]
    name = component["footprint"]
    x, y = component["at"]
    angle = component.get("angle", 0)
    top = f'(footprint {q(name if library else NAME + ":" + name)}'
    if library:
        top += ' (version 20221018) (generator dual_radio_carrier)'
    top += ' (layer "F.Cu") (tedit 0)'
    if not library:
        top += (f' (tstamp {uid(ref)}) (at {num(x)} {num(y)} {num(angle)})'
                f' (path "/{uid("schematic")}/{uid("symbol-" + ref)}")')
    top += f'\n (descr {q(component.get("description", component["value"]))})'
    if not library and component.get('mpn'):
        top += f'\n (property "MPN" {q(component["mpn"])})'
    if not library and component.get('datasheet'):
        top += f'\n (property "Datasheet" {q(component["datasheet"])})'
    if component.get("board_only"):
        top += '\n (attr board_only exclude_from_pos_files exclude_from_bom)'
    else:
        top += f'\n (attr {"through_hole" if component.get("socket") else "smd"})'
    rx, ry = component.get("ref_at", [0, -2.5])
    top += (f'\n (fp_text reference {q("REF**" if library else ref)} '
            f'(at {num(rx)} {num(ry)} {num(-angle)}) (layer "F.SilkS") {effects(0.9, 0.14)})')
    top += (f'\n (fp_text value {q(name if library else component["value"])} (at 0 0) '
            f'(layer "F.Fab") {effects(0.8, 0.12, hide=True)})')
    for layer, bounds in component.get("outlines", []):
        top += "\n" + rect(*bounds, layer, 0.1 if layer.endswith("Fab") else 0.12, True)
    if component.get("socket"):
        top += "\n" + line(-1.33, -1.33, 0, -1.33, fp=True)
        top += "\n" + line(-1.33, -1.33, -1.33, 0, fp=True)
    for pin in component["pads"]:
        pnum = str(pin["number"])
        px, py = pin["at"]
        sx, sy = pin["size"]
        drill = pin.get("drill")
        kind = "np_thru_hole" if pin.get("npth") else "thru_hole" if drill else "smd"
        layers = '"*.Cu" "*.Mask"' if drill else '"F.Cu" "F.Paste" "F.Mask"'
        top += (f'\n (pad {q(pnum)} {kind} {pin.get("shape", "circle")} '
                f'(at {num(px)} {num(py)}) (size {num(sx)} {num(sy)})')
        if drill:
            top += f' (drill {num(drill)})'
        top += f' (layers {layers})'
        if pin.get("shape") == "roundrect":
            top += ' (roundrect_rratio 0.2)'
        net = board_net_name(component,pin)
        if net and not library:
            top += f' (net {net_ids[net]} {q(net)})'
        if pin.get('zone_connect') is not None:
            top += f' (zone_connect {pin["zone_connect"]})'
        top += ')'
    return top + '\n)'


def write_board(design, routes):
    nets = sorted({board_net_name(c,p) for c in design['components'] for p in c['pads'] if not p.get('npth')})
    net_ids = {n: i + 1 for i, n in enumerate(nets)}
    width, height = design["size"]
    text = ('(kicad_pcb (version 20221018) (generator dual_radio_carrier)\n'
            ' (general (thickness 1.6))\n (paper "A4")\n'
            ' (title_block (title "Dual LR2021 USB test carrier") (date "2026-10-24") '
            '(rev "A") (comment 1 "ENGINEERING PROTOTYPE - KiCad ERC/DRC required before fabrication"))\n'
            ' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) '
            '(34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user) (37 "F.SilkS" user) '
            '(38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user) (41 "Cmts.User" user) '
            '(44 "Edge.Cuts" user) (46 "B.CrtYd" user) (47 "F.CrtYd" user) '
            '(48 "B.Fab" user) (49 "F.Fab" user))\n'
            ' (setup (pad_to_mask_clearance 0.05) (solder_mask_min_width 0.1))\n'
            ' (net 0 "")\n')
    text += '\n'.join(f' (net {i} {q(n)})' for n, i in net_ids.items()) + '\n'
    written_libraries=set()
    for component in design["components"]:
        text += footprint(component, net_ids) + '\n'
        library_path = ROOT / f'{NAME}.pretty' / f'{component["footprint"]}.kicad_mod'
        if component['footprint'] not in written_libraries:
            library_path.write_text(footprint(component, net_ids, True) + '\n')
            written_libraries.add(component['footprint'])
    text += rect(0, 0, width, height, "Edge.Cuts", 0.05) + '\n'
    for label in design.get("labels", []):
        x, y = label["at"]
        text += (f'(gr_text {q(label["text"])} (at {num(x)} {num(y)} '
                 f'{num(label.get("angle", 0))}) (layer {q(label.get("layer", "F.SilkS"))}) '
                 f'{effects(label.get("size", 1), 0.15)})\n')
    for outline in design.get("module_outlines", []):
        text += rect(*outline["bounds"], "Dwgs.User", 0.15) + '\n'
    for keepout in design.get("keepouts", []):
        x1, y1, x2, y2 = keepout["bounds"]
        xy = ' '.join(f'(xy {num(x)} {num(y)})' for x, y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
        text += (f'(zone (net 0) (net_name "") (layers "F.Cu" "B.Cu") '
                 f'(tstamp {uid("keepout-" + keepout["name"])}) (name {q(keepout["name"])}) '
                 '(hatch edge 0.5) (connect_pads (clearance 0.25)) (min_thickness 0.25) '
                 '(keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) '
                 '(copperpour not_allowed) (footprints allowed)) '
                 f'(fill (thermal_gap 0.3) (thermal_bridge_width 0.3)) (polygon (pts {xy})))\n')
    for i, segment in enumerate(routes.get("segments", [])):
        x1, y1 = segment["start"]
        x2, y2 = segment["end"]
        text += (f'(segment (start {num(x1)} {num(y1)}) (end {num(x2)} {num(y2)}) '
                 f'(width {num(segment["width"])}) (layer "{["F.Cu", "B.Cu"][segment["layer"]]}") '
                 f'(net {net_ids["/"+segment["net"]]}) (tstamp {uid("track-" + str(i))}))\n')
    for i, via in enumerate(routes.get("vias", [])):
        text += (f'(via (at {num(via["x"])} {num(via["y"])}) (size {num(via["size"])}) '
                 f'(drill {num(via["drill"])}) (layers "F.Cu" "B.Cu") '
                 f'(net {net_ids["/"+via["net"]]}) (tstamp {uid("via-" + str(i))}))\n')
    for z in routes.get('zones', []):
        layer=['F.Cu','B.Cu'][z['layer']]
        xy=' '.join(f'(xy {num(x)} {num(y)})' for x,y in z['boundary'])
        text += (f'(zone (net {net_ids["/"+z["net"]]}) (net_name {q("/"+z["net"])}) '
                 f'(layer {q(layer)}) (tstamp {uid(z["name"])}) (name {q(z["name"])}) '
                 f'(hatch edge 0.5) (priority {z.get("priority",0)}) '
                 '(connect_pads (clearance 0.25)) (min_thickness 0.2) (filled_areas_thickness no) '
                 '(fill yes (thermal_gap 0.3) (thermal_bridge_width 0.4)) '
                 f'(polygon (pts {xy}))\n')
        for polygon in z['filled']:
            points=' '.join(f'(xy {num(x)} {num(y)})' for x,y in polygon)
            text += f'(filled_polygon (layer {q(layer)}) (pts {points}))\n'
        text += ')\n'
    text += ')\n'
    path = ROOT / f'{NAME}.kicad_pcb'
    if path.exists() and path.read_text() != text:
        backup = ROOT / 'build' / 'backups'
        backup.mkdir(parents=True, exist_ok=True)
        import hashlib
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        (backup / f'{NAME}-{digest}.kicad_pcb').write_bytes(path.read_bytes())
    path.write_text(text)


def symbol_definition(name, pins, reference="J"):
    """Every component has pins on the right, with labeled wires in the sheet."""
    h = max(5.08, 2.54 * len(pins))
    s = (f'(symbol {q(name)} (pin_names (offset 0.7)) (in_bom yes) (on_board yes)\n'
         f'(property "Reference" {q(reference)} (at 0 2.54 0) {effects(1.27)})\n'
         f'(property "Value" {q(name)} (at 0 -2.54 0) {effects(1.27)})\n'
         '(property "Footprint" "" (at 0 0 0) ' + effects(1.27, hide=True) + ')\n'
         '(property "Datasheet" "" (at 0 0 0) ' + effects(1.27, hide=True) + ')\n'
         f'(symbol {q(name.split(":")[-1] + "_0_1")} '
         f'(rectangle (start -12.7 1.27) (end 0 {num(-h+1.27)}) '
         '(stroke (width 0.254) (type default)) (fill (type background))))\n')
    s += f'(symbol {q(name.split(":")[-1] + "_1_1")}\n'
    for i, pin in enumerate(pins):
        s += (f'(pin {pin.get("type", "passive")} line (at 5.08 {num(-2.54*i)} 180) '
              f'(length 5.08) (name {q(pin["name"])} {effects(0.9)}) '
              f'(number {q(pin["number"])} {effects(0.9)}))\n')
    return s + '))\n'


def write_schematic(design):
    libs, instances, wires, notes = [], [], [], []
    for component in design["components"]:
        if component.get("board_only"):
            continue
        ref = component["ref"]
        lib_id = f'{NAME}:{ref}_socket' if component.get("socket") else f'{NAME}:{ref}'
        pins = []
        seen = set()
        for pad in component["pads"]:
            number = str(pad["number"])
            if number in seen:
                continue
            seen.add(number)
            pins.append({"number": number, "name": pad.get("function", number), "type": pad.get("pin_type", "passive")})
        libs.append(symbol_definition(lib_id, pins, ref.rstrip('0123456789')))
        x, y = component["schematic"]
        props = (f'(property "Reference" {q(ref)} (at {num(x-6.35)} {num(y-5.08)} 0) {effects(1.27)})\n'
                 f'(property "Value" {q(component["value"])} (at {num(x-6.35)} {num(y-2.54)} 0) {effects(0.9)})\n'
                 f'(property "Footprint" {q(NAME + ":" + component["footprint"])} (at {num(x)} {num(y)} 0) {effects(1.27, hide=True)})\n'
                 f'(property "Datasheet" {q(component.get("datasheet", ""))} (at {num(x)} {num(y)} 0) {effects(1.27, hide=True)})\n'
                 f'(property "MPN" {q(component.get("mpn", ""))} (at {num(x)} {num(y)} 0) {effects(1.27, hide=True)})\n')
        inst = (f'(symbol (lib_id {q(lib_id)}) (at {num(x)} {num(y)} 0) (unit 1) '
                f'(in_bom yes) (on_board yes) (dnp no) (uuid {uid("symbol-" + ref)})\n' + props)
        for i, pin in enumerate(pins):
            inst += f'(pin {q(pin["number"])} (uuid {uid(ref + "pin" + pin["number"])}))\n'
            pad = next(p for p in component["pads"] if str(p["number"]) == pin["number"])
            px, py = x + 5.08, y + 2.54 * i
            net = pad.get("net")
            if net:
                ex = px + 10.16
                wires.append(f'(wire (pts (xy {num(px)} {num(py)}) (xy {num(ex)} {num(py)})) '
                             f'(stroke (width 0) (type default)) (uuid {uid(ref + "wire" + pin["number"])}))')
                wires.append(f'(label {q(net)} (at {num(ex)} {num(py)} 0) '
                             f'{effects(0.9, justify="left bottom")} (uuid {uid(ref + "label" + pin["number"])}))')
            else:
                wires.append(f'(no_connect (at {num(px)} {num(py)}) (uuid {uid(ref + "nc" + pin["number"])}))')
        inst += (f'(instances (project {q(NAME)} (path "/{uid("schematic")}" '
                 f'(reference {q(ref)}) (unit 1)))))')
        instances.append(inst)
    for i, note in enumerate(design.get("schematic_notes", [])):
        x, y = note["at"]
        notes.append(f'(text {q(note["text"])} (at {num(x)} {num(y)} 0) '
                     f'{effects(note.get("size", 1.27), justify="left top")} (uuid {uid("note-" + str(i))}))')
    header = ('(kicad_sch (version 20230121) (generator dual_radio_carrier)\n'
              f'(uuid {uid("schematic")}) (paper "A3")\n'
              '(title_block (title "Dual LR2021 USB test carrier") (date "2026-10-24") '
              '(rev "A") (comment 1 "ENGINEERING PROTOTYPE - ERC/DRC and bench verification required"))\n')
    (ROOT / f'{NAME}.kicad_sch').write_text(header + '(lib_symbols\n' + '\n'.join(libs) + ')\n'
                + '\n'.join(wires + notes + instances) + f'\n(sheet_instances (path "/" (page "1")))\n)\n')
    library = '(kicad_symbol_lib (version 20220914) (generator dual_radio_carrier)\n'
    for lib in libs:
        library += lib.replace(f'"{NAME}:', '"', 1)
    (ROOT / f'{NAME}.kicad_sym').write_text(library + ')\n')


def read_board_geometry(path):
    tree = parse(path)
    pads, segments, vias, holes = [], [], [], []
    nets = {int(n[1]): n[2] for n in items(tree, "net") if len(n)==3}

    def resolve_net(node):
        n=item(node,'net')
        if n is None:
            return None
        name=n[2] if len(n)==3 else n[1]
        if isinstance(name,int):
            name=nets.get(name,'')
        return logical_net(name)

    for fp in items(tree, "footprint"):
        change=item(fp,'transform')
        if change:
            translation=item(change,'translate')
            at=[None,translation[1],translation[2],item(change,'rotate',[None,0])[1]]
        else:
            at = item(fp, "at", [None, 0, 0])
        angle = at[3] if len(at) > 3 else 0
        references=[t[2] for t in items(fp,'fp_text') if str(t[1])=='reference']
        if not references:
            references=[p[2] for p in items(fp,'property') if p[1]=='Reference']
        ref=references[0]
        for p in items(fp, "pad"):
            loc = item(p, "at", [None, 0, 0])
            x, y = transform(at[1], at[2], angle, loc[1], loc[2])
            size = item(p, "size")[1:3]
            net = item(p, "net")
            drill = item(p, "drill")
            npth = str(p[2]) == "np_thru_hole"
            record = {"ref": ref, "number": p[1], "x": x, "y": y,
                      "size": size, "shape": str(p[3]), "angle": angle,
                      "net": resolve_net(p), "drill": drill[1] if drill else None,
                      "layers": [0, 1] if drill else [0], "npth": npth}
            (holes if npth else pads).append(record)
    for s in items(tree, "segment"):
        segments.append({"start": item(s,"start")[1:3], "end": item(s,"end")[1:3],
                         "width": item(s,"width")[1], "net": resolve_net(s),
                         "layer": 0 if item(s,"layer")[1] == "F.Cu" else 1})
    for v in items(tree, "via"):
        at = item(v,"at")
        vias.append({"x": at[1], "y": at[2], "size": item(v,"size")[1],
                     "drill": item(v,"drill")[1], "net": resolve_net(v)})
    return tree, pads, segments, vias, holes


def filled_zone_geometry(tree):
    result=[]
    for zone in items(tree,'zone'):
        net=logical_net(item(zone,'net_name',item(zone,'net',[None,'']))[1])
        if not net:
            continue
        for fill in items(zone,'filled_polygon'):
            layer=0 if item(fill,'layer')[1]=='F.Cu' else 1
            points=[p[1:3] for p in item(fill,'pts')[1:]]
            shape=Polygon(points)
            if not shape.is_valid:
                # KiCad fractures polygon holes with touching bridge edges.
                shape=shape.buffer(0)
            if shape.is_empty or shape.area <= 0:
                raise ValueError(f'Invalid saved fill polygon in {net}')
            result.append({'shape':shape,'net':net,'layers':[layer],
                           'description':f'{item(zone,"name",[None,net])[1]} polygon {len(result)}'})
    return result
