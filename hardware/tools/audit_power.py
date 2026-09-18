#!/usr/bin/env python3
"""Trace-only power resistance and a conservative filled-ground return bound.
Pours parallel to power traces can only improve this trace-only estimate.
"""
import pcbnew as p
import json,math,heapq,collections
from pathlib import Path
from audit_layouts import NetGraph
ROOT=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(ROOT/'carrier-rev-a/carrier-rev-a.kicad_pcb'))
g=NetGraph(b,'/RADIO_5V')
def route(start,end):
 start=g.pads[start];end=g.pads[end];heap=[(0,start,[])];seen=set()
 while heap:
  cost,n,path=heapq.heappop(heap)
  if n==end:return path
  if n in seen:continue
  seen.add(n)
  for nn,ll,rr in g.graph[n]:
   if nn not in seen:heapq.heappush(heap,(cost+rr,nn,path+[(n,nn,ll,rr)]))
 raise RuntimeError(('no power path',end))
loads={'S1':(('J1','2'),.85),'S2':(('J3','2'),.15),'S3':(('J5','2'),.9375),'S4':(('J7','2'),.9375),'Pico':(('Q1','3'),.3),'logic':(('U3','1'),.05)}
paths={n:route(('U2','6'),dest) for n,(dest,current) in loads.items()};currents=collections.defaultdict(float)
for n,path in paths.items():
 for a,c,ll,r in path:currents[tuple(sorted([a,c]))]+=loads[n][1]
poly=[z.GetFilledPolysList(p.B_Cu) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='/GND' and z.IsOnLayer(p.B_Cu)]
corridors={
 'entry':[(113.92,198),(113.92,205)],
 'left_main':[(113.92,203.5),(10,203.5),(10,25)],
 'right_main':[(113.92,203.5),(233,203.5),(233,60)],
 'S1':[(10,25),(17.5,25)],'S3':[(10,125),(17.5,125)],
 'S2':[(233,142.78),(188,142.78)],
 'S4':[(233,60),(190,60),(190,42.78),(188,42.78)]}
checks={}
for name,pts in corridors.items():
 missing=[];length=0;width=10 if name.endswith('main') else 4
 for a,c in zip(pts,pts[1:]):
  d=math.dist(a,c);length+=d;dx,dy=(c[0]-a[0])/d,(c[1]-a[1])/d
  for i in range(math.ceil(d/.25)+1):
   t=min(1,i*.25/d)
   for j in range(round(width/.25)+1):
    offset=-width/2+j*.25;x=a[0]+(c[0]-a[0])*t-dy*offset;y=a[1]+(c[1]-a[1])*t+dx*offset
    q=p.VECTOR2I(p.FromMM(x),p.FromMM(y))
    if not any(pp.Contains(q) for pp in poly):missing.append((round(x,3),round(y,3)))
 checks[name]={'centerline':pts,'width_mm':width,'length_mm':round(length,3),'missing_samples':missing[:10],'missing_count':len(missing)}
assert all(row['missing_count']==0 for row in checks.values()),{name:row for name,row in checks.items() if row['missing_count']}
# Corridor lengths bound the geometric return distance; shared-segment currents are applied below.
return_lengths={'S1':7+103.92+180+7.5+2.5,'S3':7+103.92+80+7.5+2.5,'S2':7+119.08+62.22+45+2.52,'S4':7+119.08+145+43+17.22+2+2.52}
r_per_mm=.01724*.001/(4*.07)*1.1572
input_r=NetGraph(b,'/EXT_5V').path(('J9','1'),('U2','5'),True)['resistance_60C_ohm'];audit=json.loads((ROOT/'validation/layout-audit.json').read_text())
result={'method':'70 um copper at 60 C; routed trace graph; shared segment currents; 10 mm main ground corridors and 4 mm terminal branches, load-weighted returns plus all 0.35 A auxiliary current on every main corridor; 20 mOhm per header contact engineering allowance (2 supply, 4 return); 45 mOhm eFuse maximum','ground_sampling_mm':.25,'ground_corridors':checks,'input_trace_ohm':input_r,'loads':{}}
for n,(dest,current) in loads.items():
 path=paths[n];drop=sum(r*currents[tuple(sorted([a,c]))] for a,c,ll,r in path)
 row={'current_A':current,'positive_length_mm':round(sum(ll for a,c,ll,r in path),3),'shared_positive_drop_V':round(drop,4)}
 if n.startswith('S'):
  board={'S1':'e22-900m30s-rev-a','S2':'core2021-hf-m-rev-a','S3':'e28-2g4m27s-rev-a','S4':'e28-2g4m27s-rev-a'}[n];adapter_r=audit[board]['power']['slot_to_load']['resistance_60C_ohm']
  # 80 mm x 4 mm local return allowance, in addition to the extracted positive trace.
  adapter_return_r=80*r_per_mm
  # Ground routes share only the trunk sections before each branch. Assign the
  # entire auxiliary load to every main segment for a conservative upper bound.
  main_segments={
   'S1':[(103.92+80,1.7875),(100,.85)],
   'S3':[(103.92+80,1.7875)],
   'S2':[(119.08+62.22,1.0875)],
   'S4':[(119.08+62.22,1.0875),(82.78,.9375)]}[n]
  branch_length={'S1':10,'S3':10,'S2':47.52,'S4':64.74}[n]
  ground_drop=3.225*(7*r_per_mm+.005)+sum(length*(amps+.35)*r_per_mm*4/10 for length,amps in main_segments)+current*branch_length*r_per_mm
  ground_drop4=4*(7*r_per_mm+.005)+sum(length*(amps+.35+.775)*r_per_mm*4/10 for length,amps in main_segments)+current*branch_length*r_per_mm
  contact_drop=current*.015
  total=3.225*(input_r+.045)+drop+ground_drop+contact_drop+current*(adapter_r+adapter_return_r)
  total4=4*(input_r+.045)+drop*4/3.225+ground_drop4+contact_drop+current*(adapter_r+adapter_return_r)
  row.update(return_length_bound_mm=round(return_lengths[n],3),return_drop_bound_V=round(ground_drop,4),return_drop_4A_stress_V=round(ground_drop4,4),contact_drop_allowance_V=round(contact_drop,4),adapter_positive_ohm=adapter_r,module_input_floor_at_J9_4_75V=round(4.75-total,3),floor_with_4A_shared_trunk_stress=round(4.75-total4,3))
 result['loads'][n]=row
(ROOT/'validation/power-route-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
# E22 output-power decision, using the actual routed network rather than 5 V
# at J9 as a proxy for the module voltage. Typical eFuse R is not a guarantee.
nominal={'S1':.650,'S2':.105,'S3':3.3*.580/(.85*5),'S4':3.3*.580/(.85*5),'Pico':.120,'logic':.030}
ni=sum(nominal.values());nc=collections.defaultdict(float)
for n,path in paths.items():
 for a,c,ll,r in path:nc[tuple(sorted([a,c]))]+=nominal[n]
rtemp=1.1572
positive_nom=sum(r/rtemp*nc[tuple(sorted([a,c]))] for a,c,ll,r in paths['S1'])
return_nom=ni*(7*r_per_mm/rtemp+.005)+(103.92+80)*(nominal['S1']+nominal['S3']+.15)*r_per_mm/rtemp*4/10+100*(nominal['S1']+.15)*r_per_mm/rtemp*4/10+nominal['S1']*10*r_per_mm/rtemp
adapter_r=audit['e22-900m30s-rev-a']['power']['slot_to_load']['resistance_60C_ohm']
nom_drop=ni*(input_r/rtemp+.0283)+positive_nom+return_nom+nominal['S1']*(.015+adapter_r/rtemp+80*r_per_mm/rtemp)
result['E22_decision']={'supply_architecture_changed':False,'nominal_J9_voltage_V':5,'nominal_total_input_A':round(ni,4),'nominal_E22_current_A':.65,'nominal_copper_temperature_C':20,'nominal_efuse_ohm':.0283,'estimated_nominal_module_voltage_V':round(5-nom_drop,3),'conservative_J9_voltage_V':4.75,'conservative_total_input_A':3.225,'conservative_E22_current_A':.85,'conservative_copper_temperature_C':60,'conservative_module_voltage_V':result['loads']['S1']['module_input_floor_at_J9_4_75V'],'four_amp_stress_module_voltage_V':result['loads']['S1']['floor_with_4A_shared_trunk_stress'],'module_at_least_5V_guaranteed':False,'full_30dBm_guaranteed':False,'decision':'Accept reduced/unspecified maximum RF output for Rev A. Do not raise the shared input or redesign power solely for 30 dBm. Nominal model assumes 5.000 V at J9; upstream cable/source drop further reduces it. Transient droop, thermal and RF output require measurement.'}
(ROOT/'validation/power-route-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['E22_decision'],indent=2))
