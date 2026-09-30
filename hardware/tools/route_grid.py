#!/usr/bin/env python3
"""Raster clearance search for the bounded, explicit endpoints from repair_routes.
This is an aid to native DRC, not a replacement for electrical/return-path review.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,math,json,sys,heapq,itertools
job=Path(sys.argv[1]);data=json.loads(job.read_text());STEP=.05;results=[]
x0,y0,x1,y1=data['outline'];W=round((x1-x0)/STEP)+1;H=round((y1-y0)/STEP)+1
point=lambda a:(round((a[0]-x0)/STEP),round((a[1]-y0)/STEP))
for task in data['tasks']:
 net=task['net'];radius=task['width']/2+.16
 ims=[Image.new('1',(W,H)) for _ in range(2)];ds=[ImageDraw.Draw(i) for i in ims]
 for sh in data['shapes']:
  if sh['net']==net:continue
  for layer in sh['layers']:
   d=ds[layer]
   if sh['type']=='pad':
    a,b,c,e=sh['box'];d.rectangle([point((a-radius,b-radius)),point((c+radius,e+radius))],fill=1)
   else:
    r=sh['width']/2+radius;a=sh['a'];ends=[a]
    if sh['type']=='track':d.line([point(a),point(sh['b'])],fill=1,width=math.ceil(2*r/STEP));ends.append(sh['b'])
    for e in ends:d.ellipse([point((e[0]-r,e[1]-r)),point((e[0]+r,e[1]+r))],fill=1)
 for pts in data['keepouts']:
  for d in ds:d.polygon([point(a) for a in pts],fill=1);d.line([point(a) for a in pts+[pts[0]]],fill=1,width=math.ceil(2*radius/STEP))
 for d in ds:d.rectangle((0,0,W-1,H-1),outline=1,width=math.ceil((.31+task['width']/2)/STEP))
 occ=np.stack([np.asarray(i,dtype=np.bool_) for i in ims])
 via=np.stack([np.asarray(i.filter(ImageFilter.MaxFilter(13)),dtype=np.bool_) for i in ims]);via=via[0]|via[1]
 for sh in data['shapes']:
  if sh['type']=='via':
   cx,cy=point(sh['a']);r=math.ceil(.6/STEP)
   for dy in range(-r,r+1):
    for dx in range(-r,r+1):
     if dx*dx+dy*dy<=r*r and 0<=cy+dy<H and 0<=cx+dx<W:via[cy+dy,cx+dx]=True
  if sh['type']=='pad' and sh.get('drill',0)>0:
   cx,cy=point(sh['center']);r=math.ceil((sh['drill']/2+.15+.26)/STEP)
   for dy in range(-r,r+1):
    for dx in range(-r,r+1):
     if dx*dx+dy*dy<=r*r and 0<=cy+dy<H and 0<=cx+dx<W:via[cy+dy,cx+dx]=True
 ends=task['ends'];start=[];goal=[];exact={}
 for idx,end in enumerate(ends):
  for pos in end['points']:
   gx,gy=point(pos)
   for l in end['layers']:
    q=(gx,gy,l)
    if not occ[l,gy,gx]:
     (start if idx==0 else goal).append(q);exact[q]=pos
 if not start or not goal:
  print(net,'blocked endpoint',start,goal,flush=True);continue
 goals=set(goal);counter=itertools.count();cost={q:0 for q in start};prev={};heap=[]
 def heuristic(q):return min(math.hypot(q[0]-g[0],q[1]-g[1]) for g in goal)
 for q in start:heapq.heappush(heap,(heuristic(q),next(counter),q))
 found=None;visited=0;settled=set()
 while heap:
  _,_,q=heapq.heappop(heap)
  if q in settled:continue
  settled.add(q);x,y,l=q;g=cost[q];visited+=1
  if q in goals:found=q;break
  if visited>2500000:break
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   xx,yy=x+dx,y+dy
   if xx<0 or yy<0 or xx>=W or yy>=H or occ[l,yy,xx]:continue
   if dx and dy and (occ[l,y,xx] or occ[l,yy,x]):continue
   n=(xx,yy,l);ng=g+(1.414214 if dx and dy else 1)*(1 if l==0 else 1.5)
   if ng<cost.get(n,float('inf')):cost[n]=ng;prev[n]=q;heapq.heappush(heap,(ng+heuristic(n),next(counter),n))
  if not via[y,x]:
   n=(x,y,1-l);ng=g+10/STEP
   if ng<cost.get(n,float('inf')):cost[n]=ng;prev[n]=q;heapq.heappush(heap,(ng+heuristic(n),next(counter),n))
 if found is None:print(net,'no path',visited,flush=True);continue
 route=[found]
 while route[-1] in prev:route.append(prev[route[-1]])
 route.reverse();reduced=[route[0]]
 for i in range(1,len(route)-1):
  a,b,c=route[i-1:i+2]
  if tuple(b[k]-a[k] for k in range(3))!=tuple(c[k]-b[k] for k in range(3)):reduced.append(b)
 reduced.append(route[-1]);pts=[[round(x0+x*STEP,4),round(y0+y*STEP,4),l] for x,y,l in reduced]
 pts[0]=exact[route[0]]+[route[0][2]];pts[-1]=exact[found]+[found[2]]
 results.append(dict(net=net,width=task['width'],points=pts));print(net,'routed',len(pts),'vertices',visited,'searches',flush=True)
 for a,b in zip(pts,pts[1:]):
  if a[2]!=b[2]:data['shapes'].append(dict(type='via',a=a[:2],net=net,width=.65,layers=[0,1]))
  else:data['shapes'].append(dict(type='track',a=a[:2],b=b[:2],net=net,width=task['width'],layers=[a[2]]))
job.with_suffix('.routes.json').write_text(json.dumps(results,indent=2)+'\n')
