"""Check the saved PCB and schematic, not the routing program's self-report.

This is an independent geometry/connectivity check, not a replacement for KiCad DRC/ERC.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict

from kiutils.board import Board
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from shapely.geometry import Point, box
from shapely.strtree import STRtree

from cad import NAME, ROOT, filled_zone_geometry, item, items, pad_shape, parse, read_board_geometry, segment_shape


def verify():
    pcb = ROOT / f'{NAME}.kicad_pcb'
    sch = ROOT / f'{NAME}.kicad_sch'
    # Use the independent parser for its supported file versions; native KiCad checks cover newer PCB formats.
    pcb_tree=parse(pcb)
    if item(pcb_tree,'version')[1] <= 20240108:
        Board().from_file(str(pcb))
    parsed_schematic = Schematic().from_file(str(sch))
    SymbolLib().from_file(str(ROOT / f'{NAME}.kicad_sym'))
    tree, pads, segments, vias, holes = read_board_geometry(pcb)
    design = json.loads((ROOT / 'design.json').read_text())
    errors = []
    features = []
    for pad in pads:
        features.append({"shape": pad_shape(pad), "net": pad.get("net"), "layers": pad["layers"],
                         "description": f'{pad["ref"]}.{pad["number"]}', "pad": pad})
        if pad.get("drill") and (min(pad["size"]) - pad["drill"])/2 < 0.15 - 1e-6:
            errors.append(f'Insufficient annulus at {pad["ref"]}.{pad["number"]}')
    for i, segment in enumerate(segments):
        features.append({"shape": segment_shape(segment), "net": segment["net"],
                         "layers": [segment["layer"]], "description": f'track {i}'})
        if segment["width"] < 0.24999:
            errors.append(f'Track {i} below 0.25mm')
    for i, via in enumerate(vias):
        features.append({"shape": Point(via["x"], via["y"]).buffer(via["size"]/2, quad_segs=16),
                         "net": via["net"], "layers": [0, 1], "description": f'via {i}'})
        if via["drill"] < 0.29999 or (via["size"]-via["drill"])/2 < 0.14999:
            errors.append(f'Via {i} below fabrication limits')
    drilled=[{'x':p['x'],'y':p['y'],'drill':p['drill'],'description':f'{p["ref"]}.{p["number"]}'}
             for p in pads+holes if p.get('drill')]
    drilled += [{**v,'description':f'via {i}'} for i,v in enumerate(vias)]
    for i,a in enumerate(drilled):
        for b in drilled[i+1:]:
            gap=math.hypot(a['x']-b['x'],a['y']-b['y'])-(a['drill']+b['drill'])/2
            if gap<.25-.00002:
                errors.append(f'Drill gap {gap:.4f}mm: {a["description"]} / {b["description"]}')
    filled=filled_zone_geometry(tree)
    features.extend(filled)
    parent = list(range(len(features)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        a, b = find(a), find(b)
        parent[a] = b

    minimum_clearance = 1000.0
    clearance_pairs = set()
    for layer in [0, 1]:
        ids = [i for i, f in enumerate(features) if layer in f["layers"]]
        geometries = [features[i]["shape"] for i in ids]
        index = STRtree(geometries)
        for local, a in enumerate(ids):
            fa = features[a]
            for hit in index.query(fa["shape"].buffer(0.251)):
                b = ids[int(hit)]
                if b <= a:
                    continue
                fb = features[b]
                distance = fa["shape"].distance(fb["shape"])
                if fa["net"] and fa["net"] == fb["net"]:
                    if distance < 0.00002:
                        union(a, b)
                else:
                    minimum_clearance = min(minimum_clearance, distance)
                    if distance < 0.25 - 0.00002:
                        pair = (a, b, layer)
                        if pair not in clearance_pairs:
                            errors.append(f'Copper gap {distance:.4f}mm on {layer}: '
                                          f'{fa["description"]} [{fa["net"]}] / '
                                          f'{fb["description"]} [{fb["net"]}]')
                            clearance_pairs.add(pair)
    pad_components = defaultdict(lambda: defaultdict(list))
    for i, feature in enumerate(features):
        if feature.get("pad") and feature["net"]:
            pad_components[feature["net"]][find(i)].append(feature["description"])
    continuity = {}
    for net, components in sorted(pad_components.items()):
        continuity[net] = {"pad_count": sum(map(len, components.values())), "connected_groups": len(components)}
        if len(components) != 1:
            errors.append(f'Open net {net}: {list(components.values())}')
    edge = box(0, 0, *design["size"])
    for f in features:
        if not edge.buffer(-design["edge_clearance"] + 0.00002).covers(f["shape"]):
            errors.append(f'Copper/edge clearance violation at {f["description"]}')
        for h in holes:
            distance = f["shape"].distance(Point(h["x"], h["y"]).buffer(h["drill"]/2))
            if distance < 0.25 - 0.00002:
                errors.append(f'Copper/NPTH gap {distance:.4f} at {f["description"]} / {h["ref"]}')
        for k in design.get("keepouts", []):
            # Native zone fills may share the exact keepout boundary without entering its interior.
            if f["shape"].intersects(box(*k["bounds"]).buffer(-.00001)):
                errors.append(f'Copper in {k["name"]} at {f["description"]}')

    # Reconstruct the schematic net assigned at each physical pin from its actual wires and labels.
    stree = parse(sch)
    libs = {s[1]: s for s in items(item(stree, 'lib_symbols'), 'symbol')}
    labels = {(round(item(l,'at')[1],5), round(item(l,'at')[2],5)): l[1] for l in items(stree,'label')}
    wires = [(tuple(item(w,'pts')[1][1:3]), tuple(item(w,'pts')[2][1:3])) for w in items(stree,'wire')]
    ncs = {tuple(item(n,'at')[1:3]) for n in items(stree,'no_connect')}
    schematic_nets = {}
    for symbol in items(stree,'symbol'):
        ref = next(p[2] for p in items(symbol,'property') if p[1] == 'Reference')
        at = item(symbol,'at')
        lib = libs[item(symbol,'lib_id')[1]]
        for unit in items(lib,'symbol'):
            for pin in items(unit,'pin'):
                number = item(pin,'number')[1]
                loc = item(pin,'at')
                pos = (round(at[1]+loc[1],5), round(at[2]-loc[2],5))
                found = []
                for a,b in wires:
                    if a == pos and b in labels:
                        found.append(labels[b])
                    elif b == pos and a in labels:
                        found.append(labels[a])
                if len(found) != 1:
                    if pos not in ncs:
                        errors.append(f'Schematic pin has no net/NC: {ref}.{number} at {pos}')
                    schematic_nets[(ref,number)] = None
                else:
                    schematic_nets[(ref,number)] = found[0]
    for pad in pads:
        key = (pad['ref'], str(pad['number']))
        if key not in schematic_nets:
            errors.append(f'PCB pad absent from schematic: {key}')
        elif schematic_nets[key] != pad.get('net'):
            errors.append(f'Schematic/PCB mismatch {key}: {schematic_nets[key]} / {pad.get("net")}')
    # Check hard electrical boundaries directly in the saved artifacts.
    controller_3v3 = [p for p in pads if p['ref'] in ('J1','J2') and p.get('net') == '+3V3_RADIO']
    if controller_3v3:
        errors.append('Controller regulator output tied to radio regulator output')
    for p in pads:
        if p['ref'] in ('J3','J4','J5','J6') and str(p['number']) in design.get('radio_rf_socket_pins',{}).get(p['ref'],[]):
            if p.get('net'):
                errors.append(f'RF contact must remain unconnected: {p["ref"]}.{p["number"]}')
    pcb_hash=hashlib.sha256(pcb.read_bytes()).hexdigest()
    sch_hash=hashlib.sha256(sch.read_bytes()).hexdigest()
    native_path=ROOT/'build'/'native-summary.json'
    native=json.loads(native_path.read_text()) if native_path.exists() else {}
    native_current=native.get('pcb_sha256')==pcb_hash and native.get('schematic_sha256')==sch_hash
    report = {
        'status': 'pass' if not errors else 'fail',
        'scope': 'Saved-artifact parsing, copper clearance, routed connectivity, edge/hole/antenna keepout, schematic-PCB equivalence. NOT KiCad ERC/DRC or physical validation.',
        'kicad_erc': ('pass' if native.get('erc_exit_code')==0 else 'fail') if native_current else 'not_run_on_current_files',
        'kicad_drc': native.get('status') if native_current else 'not_run_on_current_files',
        'pcb_sha256':pcb_hash,'schematic_sha256':sch_hash,
        'footprints': len(items(tree,'footprint')), 'schematic_symbols': len(parsed_schematic.schematicSymbols),
        'tracks': len(segments), 'vias': len(vias), 'filled_copper_polygons':len(filled), 'nets': continuity,
        'minimum_clearance_near_threshold_mm': None if minimum_clearance == 1000 else round(minimum_clearance,5),
        'errors': errors,
    }
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build'/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if verify() else 1)
