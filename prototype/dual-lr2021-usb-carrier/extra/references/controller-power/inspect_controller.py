"""Inspect the downloaded vendor STEP without changing or modeling geometry.

Run with Python 3. Reads STEP vertices, assembly placements, and board holes.
The output records source geometry, not machining tolerances.
"""

import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = (ROOT / "sources/controller-3d.step").read_text()
entities = {
    int(key): value.replace("\n", "")
    for key, value in re.findall(r"#(\d+)\s*=\s*(.*?);", source, re.S)
}


def refs(value):
    return [int(key) for key in re.findall(r"#(\d+)", value)]


def vector(key):
    values = re.search(r"\(([^()]*)\)\)$", entities[key])[1]
    return tuple(float(value) for value in values.split(","))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit(a):
    length = math.sqrt(dot(a, a))
    return tuple(x / length for x in a)


def frame(key):
    origin_key, z_key, x_key = refs(entities[key])
    origin, z, x = vector(origin_key), unit(vector(z_key)), unit(vector(x_key))
    return origin, (x, cross(z, x), z)


def place(point, source_frame, destination_frame):
    source_origin, source_axes = source_frame
    destination_origin, destination_axes = destination_frame
    delta = tuple(point[i] - source_origin[i] for i in range(3))
    local = tuple(dot(delta, axis) for axis in source_axes)
    return tuple(destination_origin[i] + sum(local[j] * destination_axes[j][i] for j in range(3)) for i in range(3))


children = defaultdict(list)
for value in entities.values():
    if value.startswith("(REPRESENTATION_RELATIONSHIP("):
        child, parent, transform = refs(value)
        source_frame, destination_frame = (frame(key) for key in refs(entities[transform]))
        children[parent].append((child, source_frame, destination_frame))


def vertices(key):
    seen = set()
    pending = [key]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        value = entities[current]
        if value.startswith("VERTEX_POINT("):
            yield vector(refs(value)[0])
        else:
            pending.extend(refs(value))


def assembly_vertices(key):
    if entities[key].startswith("ADVANCED_BREP_SHAPE_REPRESENTATION("):
        yield from vertices(key)
    for child, source_frame, destination_frame in children[key]:
        for point in assembly_vertices(child):
            yield place(point, source_frame, destination_frame)


def bounds(points):
    points = list(points)
    return {axis: [min(p[i] for p in points), max(p[i] for p in points)] for i, axis in enumerate("xyz")}


def shape_for(product_name):
    product_key = next(key for key, value in entities.items() if value.startswith(f"PRODUCT('{product_name}',"))
    formation_key = next(key for key, value in entities.items() if value.startswith("PRODUCT_DEFINITION_FORMATION_") and product_key in refs(value))
    definition_key = next(key for key, value in entities.items() if value.startswith("PRODUCT_DEFINITION(") and formation_key in refs(value))
    shape_key = next(key for key, value in entities.items() if value.startswith("PRODUCT_DEFINITION_SHAPE('','SHAPE FOR ") and definition_key in refs(value))
    representation = next(refs(value)[1] for value in entities.values() if value.startswith("SHAPE_DEFINITION_REPRESENTATION(") and refs(value)[0] == shape_key)
    return representation


board_shape = shape_for("BOARD")
usb_shape = shape_for("H1_ASM")
board_bounds = bounds(assembly_vertices(board_shape))
usb_bounds = bounds(assembly_vertices(usb_shape))
board_keys = set()
pending = [board_shape]
while pending:
    key = pending.pop()
    if key in board_keys:
        continue
    board_keys.add(key)
    pending.extend(refs(entities[key]))

holes = set()
for key in board_keys:
    value = entities[key]
    if value.startswith("CYLINDRICAL_SURFACE("):
        radius = float(value.rsplit(",", 1)[1].rstrip(")"))
        if abs(radius - 0.45) < 0.0001:
            holes.add(vector(refs(entities[refs(value)[0]])[0]))

x_rows = sorted(set(round(point[0], 7) for point in holes))
y_positions = sorted(set(round(point[1], 7) for point in holes))
assert len(holes) == 44 and len(x_rows) == 2 and len(y_positions) == 22
pitch = [b - a for a, b in zip(y_positions, y_positions[1:])]
assert all(abs(value - 2.54) < 0.0001 for value in pitch)
result = {
    "source": "sources/controller-3d.step",
    "method": "STEP assembly frame transforms and BREP vertices; no geometry modifications",
    "board_shape_entity": board_shape,
    "usb_H1_shape_entity": usb_shape,
    "board_vertex_bounds_mm_in_board_frame": board_bounds,
    "usb_H1_vertex_bounds_mm_in_assembly_frame": usb_bounds,
    "board_header_holes_count": len(holes),
    "board_header_x_rows_mm": x_rows,
    "board_header_y_positions_mm": y_positions,
    "header_row_spacing_mm": x_rows[1] - x_rows[0],
    "header_pitch_mm": sum(pitch) / len(pitch),
    "usb_projection_beyond_USB_end_board_edge_mm": board_bounds["y"][0] - usb_bounds["y"][0],
    "notes": ["Board STEP placement subtracts 1.59999934 mm from z; x and y unchanged.", "BREP vertex bounds can differ slightly from nominal drawing dimensions.", "Header x-row identity and pin order come from the schematic plus pinout image, not STEP geometry."],
}
(ROOT / "extracted/step-measurements.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
