"""Cache clearance-clipped ground and regulator heat-spreading zones in the PCB.

KiCad should refill and check these native zones before manufacturing export.
All connections are also routed explicitly, so connectivity does not depend on this cache.
"""

from __future__ import annotations

import json

from shapely import constrained_delaunay_triangles, union_all
from shapely.geometry import Point, box

from cad import NAME, ROOT, flatten_pads, pad_shape, segment_shape, write_board

CLEARANCE=.275


def polygons(shape):
    if shape.is_empty:
        return []
    return [shape] if shape.geom_type=='Polygon' else [p for p in shape.geoms if p.geom_type=='Polygon']


def fill_zone(design,routes,net,layer,bounds,extra_obstacles=()):
    pads=flatten_pads(design)
    allowed=box(*bounds)
    obstacles=list(extra_obstacles)
    contacts=[]
    for p in pads:
        if layer not in p['layers']:
            continue
        geom=pad_shape(p)
        if p.get('net')==net:
            contacts.append(geom)
        else:
            gap=.5 if p['ref'] in ('J3','J4','J5','J6') and str(p['number'])=='8' else CLEARANCE
            obstacles.append(geom.buffer(gap,quad_segs=12))
    for s in routes['segments']:
        if s['layer']!=layer:
            continue
        geom=segment_shape(s)
        if s['net']==net:
            contacts.append(geom)
        else:
            obstacles.append(geom.buffer(CLEARANCE,quad_segs=12))
    for v in routes['vias']:
        geom=Point(v['x'],v['y']).buffer(v['size']/2,quad_segs=12)
        if v['net']==net:
            contacts.append(geom)
        else:
            obstacles.append(geom.buffer(CLEARANCE,quad_segs=12))
    for k in design['keepouts']:
        obstacles.append(box(*k['bounds']).buffer(.025))
    plane=allowed.difference(union_all(obstacles)).simplify(.002,preserve_topology=True)
    if net=='GND':
        # Actual thermal gaps and spokes are cached as geometry, not merely declared.
        for p in pads:
            if p.get('net')!='GND' or not p.get('drill') or layer not in p['layers']:
                continue
            x,y=p['x'],p['y']
            radius=max(p['size'])/2+.7
            spokes=box(x-radius,y-.2,x+radius,y+.2).union(box(x-.2,y-radius,x+.2,y+radius))
            previous=plane
            plane=plane.difference(pad_shape(p).buffer(.3,quad_segs=12)).union(spokes.intersection(previous))
    conductive=union_all(contacts)
    keep=[p for p in polygons(plane) if p.area>=1 and p.intersects(conductive)]
    return union_all(keep)


def zone_record(name,net,layer,bounds,shape,priority=0):
    filled=[]
    for polygon in polygons(shape):
        triangles=constrained_delaunay_triangles(polygon)
        total=sum(t.area for t in triangles.geoms)
        if abs(total-polygon.area)>0.0001:
            raise ValueError(f'Zone triangulation changed area for {name}')
        for triangle in triangles.geoms:
            points=[[round(x,5),round(y,5)] for x,y in list(triangle.exterior.coords)[:-1]]
            if triangle.area>.0000001:
                filled.append(points)
    x1,y1,x2,y2=bounds
    return {'name':name,'net':net,'layer':layer,'priority':priority,
            'boundary':[[x1,y1],[x2,y1],[x2,y2],[x1,y2]],'area_mm2':round(shape.area,2),'filled':filled}


if __name__=='__main__':
    design=json.loads((ROOT/'design.json').read_text())
    route_file=ROOT/'build'/'routes.json'
    routes=json.loads(route_file.read_text())
    heat_bounds=[50,50,65,61.5]
    heat=fill_zone(design,routes,'+3V3_RADIO',0,heat_bounds)
    if heat.area<60:
        raise ValueError('Regulator heat-spreading copper too fragmented')
    w,h=design['size']
    ground_bounds=[.51,.51,w-.51,h-.51]
    ground_front=fill_zone(design,routes,'GND',0,ground_bounds,[heat.buffer(CLEARANCE)])
    ground_back=fill_zone(design,routes,'GND',1,ground_bounds)
    routes['zones']=[zone_record('RADIO_3V3_HEAT_SPREAD','+3V3_RADIO',0,heat_bounds,heat,1),
                     zone_record('GND_FRONT','GND',0,ground_bounds,ground_front),
                     zone_record('GND_BACK','GND',1,ground_bounds,ground_back)]
    route_file.write_text(json.dumps(routes,indent=2)+'\n')
    write_board(design,routes)
    for z in routes['zones']:
        print(f'{z["name"]}: {z["area_mm2"]}mm2, {len(z["filled"])} cached polygons')
