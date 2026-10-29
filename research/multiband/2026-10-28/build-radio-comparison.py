from pathlib import Path
import os
import json
import math
import csv
import zipfile

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'plot-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

packet = json.loads((ROOT / 'packet-radio-points.json').read_text())
wifi = json.loads((ROOT / 'wifi-radio-points.json').read_text())
points = packet['points'] + wifi['points']
for p in points:
    if p['family'] in ('LoRa', 'FLRC'):
        band = '915 MHz' if p['frequency_mhz'] < 1000 else '2.4 GHz'
        p['family'] = band + ' ' + p['family']
    p['frequency_penalty_db'] = 20 * math.log10(p['frequency_mhz'] / 915)
    p['conducted_budget_db'] = p['tx_dbm'] - p['sensitivity_dbm']
    p['normalized_budget_db'] = p['conducted_budget_db'] - p['frequency_penalty_db']

families = [
    '5 GHz Wi-Fi', '2.4 GHz Wi-Fi', '2.4 GHz FLRC', '2.4 GHz LoRa',
    '915 MHz HaLow', '915 MHz FLRC', '915 MHz LoRa'
]
colors = ['#2563eb', '#0891b2', '#ea580c', '#be123c', '#7c3aed', '#16a34a', '#14532d']
markers = ['s', 's', '^', 'o', 'D', '^', 'o']
frontiers = {}
for family in families:
    group = [p for p in points if p['family'] == family]
    out = []
    for p in group:
        dominated = any(
            q['rate_kbps'] >= p['rate_kbps'] and
            q['normalized_budget_db'] >= p['normalized_budget_db'] and
            (q['rate_kbps'] > p['rate_kbps'] or q['normalized_budget_db'] > p['normalized_budget_db'])
            for q in group
        )
        p['on_sampled_family_frontier'] = not dominated
        if not dominated:
            out.append(p)
    frontiers[family] = sorted(out, key=lambda p: p['normalized_budget_db'])

plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'axes.labelsize':12,
                     'axes.spines.top':False, 'axes.spines.right':False, 'figure.facecolor':'white'})
fig, ax = plt.subplots(figsize=(12.6, 8.1), dpi=180)
fig.subplots_adjust(left=.105, right=.975, bottom=.225, top=.77)
fig.text(.105,.95,'The useful handoff points overlap',fontsize=20,weight='bold',color='#14243a')
fig.text(.105,.91,'Selected datasheet profiles: maximum nominal rate versus tolerated path loss',fontsize=12,color='#46556a')
xmin = 60
xmax = 167
for family,color,marker in zip(families,colors,markers):
    fp = frontiers[family]
    xs = [xmin] + [p['normalized_budget_db'] for p in fp]
    ys = [fp[0]['rate_kbps']] + [p['rate_kbps'] for p in fp]
    style = '--' if 'LoRa' in family else '-'
    ax.step(xs,ys,where='pre',color=color,lw=2.1,ls=style,label=family,zorder=3)
    ax.scatter([p['normalized_budget_db'] for p in fp],[p['rate_kbps'] for p in fp],
               s=19,marker=marker,color=color,zorder=4)

ax.set_yscale('log')
ax.set_xlim(xmin,xmax)
ax.set_ylim(.18,700000)
ax.set_yticks([.3,1,10,100,1000,10000,100000])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: f'{v/1000:g} Mb/s' if v>=1000 else f'{v:g} kb/s'))
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.grid(axis='both',which='major',color='#dbe1e8',lw=.7,zorder=0)
ax.set_ylabel('PHY / nominal rate (packet overhead excluded)')
ax.set_xlabel('Required path budget referred to 915 MHz (dB) — weaker paths to the right',labelpad=10)
ax.tick_params(colors='#314158')
ax.spines['left'].set_color('#9aa6b5')
ax.spines['bottom'].set_color('#9aa6b5')
ax.axhline(1000,color='#6b7280',lw=.8,ls=':',zorder=1)
ax.text(166,1120,'1 Mb/s PHY reference',ha='right',va='bottom',fontsize=9,color='#596579')

ref_5mi = 32.45 + 20*math.log10(915) + 20*math.log10(5*1.609344) + 15
ax.axvline(ref_5mi,color='#94a3b8',lw=1,ls=':',zorder=1)
ax.annotate('Illustration only: 5 miles in free space\n+ 15 dB reserve, 0 dBi antennas',
            xy=(ref_5mi,90000),xytext=(132,140000),fontsize=9,color='#596579',
            arrowprops={'arrowstyle':'-','color':'#94a3b8','lw':.8},ha='left')
fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.1,.875),
           ncol=4,frameon=False,fontsize=10,handlelength=2.6,columnspacing=1.8)
fig.text(.105,.135,'How to read: at a chosen path budget, each line gives the fastest qualifying profile in this sample.',
         fontsize=10,color='#314158')
fig.text(.105,.103,'Budget = TX power − RX sensitivity − 20 log10(f / 915 MHz). Equal antenna gain assumed; power varies by mode.',
         fontsize=9.2,color='#596579')
fig.text(.105,.078,'Not measured range or application goodput. No board losses, interference or regulatory power reductions are included.',
         fontsize=9.2,color='#596579')
fig.text(.105,.053,'Different receiver test criteria apply. Wi-Fi / HaLow use long GI; LoRa rates are nominal. Curves cover selected settings only.',
         fontsize=9.2,color='#596579')
fig.text(.105,.027,'Sources: Semtech LR20xx rev 2.1 • Morse Micro MM8108-MF15457 v4 • Infineon CYW43455 rev *O.  Analysis: 28 Oct 2026.',
         fontsize=8.6,color='#596579')
fig.savefig(ROOT/'radio-range-rate-comparison.png',facecolor='white')
plt.close(fig)

fields=['family','chip','mode','frequency_mhz','rate_kbps','bandwidth_khz','tx_dbm',
        'sensitivity_dbm','conducted_budget_db','frequency_penalty_db','normalized_budget_db',
        'on_sampled_family_frontier','rate_basis','tx_basis','source_url']
with (ROOT/'radio-profile-data.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
    w.writeheader()
    for p in points:
        row=dict(p)
        for key in ['conducted_budget_db','frequency_penalty_db','normalized_budget_db']:
            row[key]=round(row[key],4)
        w.writerow(row)

metadata={
 'analysis_date':'2026-10-28',
 'formula':'B_ref915 = P_TX - S_RX - 20*log10(f_MHz/915)',
 'meaning':'Free-space frequency-normalized conducted link-budget proxy. Equal antenna gains; no loss or fade margin is subtracted from individual curves.',
 'frontier':'Fastest nominal rate among sampled settings satisfying B_ref915 >= required path budget. Within each family only; spectrum occupancy and energy are not optimization dimensions in this plot.',
 'line_interpretation':'Step transitions select among sampled settings. They do not interpolate nonexistent modes or claim the sample is exhaustive.',
 'packet_metadata':packet['metadata'],
 'wifi_metadata':wifi['metadata'],
 'five_mile_reference':{'miles':5,'free_space_loss_915_db':ref_5mi-15,'reserve_db':15,'required_budget_db':ref_5mi,
   'caution':'Illustrative unobstructed free-space geometry with 0 dBi antennas and no additional loss. Not a range guarantee, propagation survey or radio-horizon model.'}
}
(ROOT/'radio-profile-assumptions.json').write_text(json.dumps(metadata,indent=2))

summary={'points':len(points),'family_frontiers':{},'ideal_5mi_reference_db':ref_5mi}
for family in families:
    summary['family_frontiers'][family]=[
      {'mode':p['mode'],'rate_kbps':p['rate_kbps'],'budget_db':round(p['normalized_budget_db'],2)}
      for p in frontiers[family]
    ]
(ROOT/'radio-profile-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

package_files=['radio-range-rate-comparison.png','radio-profile-data.csv','radio-profile-assumptions.json',
               'radio-profile-summary.json','packet-radio-points.json','wifi-radio-points.json',
               'radio-comparison-notes.txt','build-radio-comparison.py']
with zipfile.ZipFile(ROOT/'radio-profile-analysis.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for name in package_files:
        p=ROOT/name
        if not p.is_file():
            raise FileNotFoundError(p)
        z.write(p,name)
print('Wrote PNG, CSV, metadata and reproducible ZIP.')
