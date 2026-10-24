"""Route this carrier on a clearance-aware two-layer grid, without KiCad installed."""

from __future__ import annotations

import heapq
import json
import math
import time
from collections import defaultdict

import numpy as np
from shapely import contains_xy
from shapely.geometry import Point, box

from cad import ROOT, flatten_pads, pad_shape, segment_shape, write_board

GRID = 0.2
CLEARANCE = 0.25
MARGIN = 0.045
VIA_SIZE = 0.65
VIA_DRILL = 0.3


class Router:
    def __init__(self, design):
        self.design = design
        self.pads = flatten_pads(design)
        w, h = design["size"]
        self.nx, self.ny = round(w / GRID) + 1, round(h / GRID) + 1
        self.count = self.nx * self.ny
        self.features = []
        for pad in self.pads:
            self.features.append((pad_shape(pad), pad.get("net"), pad["layers"]))
        for keepout in design.get("keepouts", []):
            self.features.append((box(*keepout["bounds"]), None, [0, 1]))
        self.segments, self.vias = [], []

    def raster(self, mask, shape, layers):
        x1, y1, x2, y2 = shape.bounds
        ix1, iy1 = max(0, math.floor(x1 / GRID)), max(0, math.floor(y1 / GRID))
        ix2, iy2 = min(self.nx-1, math.ceil(x2 / GRID)), min(self.ny-1, math.ceil(y2 / GRID))
        if ix1 > ix2 or iy1 > iy2:
            return
        xs = np.arange(ix1, ix2 + 1) * GRID
        ys = np.arange(iy1, iy2 + 1) * GRID
        xx, yy = np.meshgrid(xs, ys)
        hit = contains_xy(shape, xx, yy)
        for layer in layers:
            mask[layer, iy1:iy2+1, ix1:ix2+1] |= hit

    def masks(self, net, width):
        blocked = np.zeros((2, self.ny, self.nx), dtype=bool)
        via_blocked = blocked.copy()
        edge = self.design["edge_clearance"]
        for mask, radius in [(blocked, width/2), (via_blocked, VIA_SIZE/2)]:
            steps = math.ceil((edge + radius + MARGIN) / GRID)
            mask[:, :steps, :] = True
            mask[:, -steps:, :] = True
            mask[:, :, :steps] = True
            mask[:, :, -steps:] = True
        for shape, feature_net, layers in self.features:
            if feature_net == net:
                continue
            extra = CLEARANCE + MARGIN
            self.raster(blocked, shape.buffer(width / 2 + extra), layers)
            self.raster(via_blocked, shape.buffer(VIA_SIZE / 2 + extra), layers)
        return blocked.ravel(), via_blocked.ravel()

    def state(self, x, y, layer):
        return layer * self.count + round(y / GRID) * self.nx + round(x / GRID)

    def position(self, state):
        layer, index = divmod(state, self.count)
        y, x = divmod(index, self.nx)
        return round(x * GRID, 5), round(y * GRID, 5), layer

    def astar(self, start, end, blocked, via_blocked):
        gx, gy = round(end["x"] / GRID), round(end["y"] / GRID)
        goals = {self.state(end["x"], end["y"], layer) for layer in end["layers"]}
        starts = [self.state(start["x"], start["y"], layer) for layer in start["layers"]]

        def estimate(state):
            layer, index = divmod(state, self.count)
            y, x = divmod(index, self.nx)
            return abs(gx - x) + abs(gy - y) + (0 if layer in end["layers"] else 18)

        queue, costs, previous = [], {}, {}
        for state in starts:
            if not blocked[state]:
                costs[state] = 0
                heapq.heappush(queue, (estimate(state), 0, state))
        popped = 0
        while queue:
            _, cost, state = heapq.heappop(queue)
            if cost != costs.get(state):
                continue
            if state in goals:
                path = [state]
                while state in previous:
                    state = previous[state]
                    path.append(state)
                return list(reversed(path))
            popped += 1
            if popped > 650000:
                break
            layer, index = divmod(state, self.count)
            iy, ix = divmod(index, self.nx)
            neighbors = []
            if ix > 0:
                neighbors.append((state-1, 1.0 if layer == 0 else 1.25))
            if ix+1 < self.nx:
                neighbors.append((state+1, 1.0 if layer == 0 else 1.25))
            if iy > 0:
                neighbors.append((state-self.nx, 1.0 if layer == 1 else 1.25))
            if iy+1 < self.ny:
                neighbors.append((state+self.nx, 1.0 if layer == 1 else 1.25))
            other = state + (self.count if layer == 0 else -self.count)
            if not via_blocked[state] and not via_blocked[other]:
                neighbors.append((other, 18.0))
            for neighbor, extra in neighbors:
                if blocked[neighbor]:
                    continue
                new_cost = cost + extra
                if new_cost < costs.get(neighbor, math.inf):
                    costs[neighbor] = new_cost
                    previous[neighbor] = state
                    heapq.heappush(queue, (new_cost + estimate(neighbor), new_cost, neighbor))
        raise RuntimeError(f'No route after {popped} states: {start["ref"]}.{start["number"]} -> '
                           f'{end["ref"]}.{end["number"]}, net {start["net"]}')

    def add_segment(self, start, end, layer, net, width):
        if math.dist(start, end) < 0.00001:
            return
        segment = {"start": list(start), "end": list(end), "layer": layer, "net": net, "width": width}
        self.segments.append(segment)
        self.features.append((segment_shape(segment), net, [layer]))

    def commit(self, path, start, end, net, width):
        points = [self.position(s) for s in path]
        # The small pad-center escapes stay inside the connected pad wherever possible.
        self.add_segment((start["x"], start["y"]), points[0][:2], points[0][2], net, width)
        chain = [points[0]]
        for point in points[1:]:
            if point[2] != chain[-1][2]:
                for a, b in zip(chain, chain[1:]):
                    self.add_segment(a[:2], b[:2], a[2], net, width)
                x, y, layer = point
                on_through_pad = any(p.get("drill") and p.get("net") == net
                                     and pad_shape(p).covers(Point(x, y)) for p in self.pads)
                if not on_through_pad:
                    via = {"x": x, "y": y, "size": VIA_SIZE, "drill": VIA_DRILL, "net": net}
                    # Reuse overlapping same-net copper instead of drilling two adjacent holes.
                    if not any(v['net']==net and math.hypot(v['x']-x,v['y']-y)
                               <= v['size']/2+width/2-.02 for v in self.vias):
                        self.vias.append(via)
                        self.features.append((Point(x,y).buffer(VIA_SIZE/2), net, [0, 1]))
                chain = [point]
                continue
            if len(chain) >= 2:
                a, b = chain[-2], chain[-1]
                if ((a[0] == b[0] == point[0]) or (a[1] == b[1] == point[1])):
                    chain[-1] = point
                    continue
            chain.append(point)
        for a, b in zip(chain, chain[1:]):
            self.add_segment(a[:2], b[:2], a[2], net, width)
        self.add_segment(points[-1][:2], (end["x"], end["y"]), points[-1][2], net, width)

    def route_net(self, net, pads, width):
        connected = [pads[0]]
        remaining = pads[1:]
        while remaining:
            _, start, end = min(((math.hypot(a["x"]-b["x"], a["y"]-b["y"]), a, b)
                                 for a in connected for b in remaining), key=lambda edge: edge[0])
            blocked, via_blocked = self.masks(net, width)
            path = self.astar(start, end, blocked, via_blocked)
            self.commit(path, start, end, net, width)
            connected.append(end)
            remaining.remove(end)

    def run(self):
        nets = defaultdict(list)
        for pad in self.pads:
            if pad.get("net"):
                nets[pad["net"]].append(pad)
        priority = ["USB_5V", "+3V3_RADIO", "GND", "SPI_SCK_HOST", "SPI_MOSI_HOST",
                    "SPI_SCK", "SPI_MOSI", "SPI_MISO"]
        order = sorted(nets, key=lambda n: (priority.index(n) if n in priority else len(priority), n))
        for net in order:
            width = 0.65 if net in ("USB_5V", "+3V3_RADIO", "GND") else 0.25
            before = time.monotonic()
            self.route_net(net, nets[net], width)
            print(f'{net}: {len(nets[net])} pads in {time.monotonic()-before:.1f}s', flush=True)
        return {"grid_mm": GRID, "clearance_mm": CLEARANCE, "segments": self.segments, "vias": self.vias}


if __name__ == "__main__":
    design = json.loads((ROOT / "design.json").read_text())
    router = Router(design)
    routes = router.run()
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build" / "routes.json").write_text(json.dumps(routes, indent=2) + '\n')
    write_board(design, routes)
    print(f'Wrote canonical board: {len(routes["segments"])} segments, {len(routes["vias"])} vias', flush=True)
