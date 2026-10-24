"""Render a top inspection image from the saved KiCad PCB geometry."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cad import NAME, ROOT, filled_zone_geometry, item, items, read_board_geometry

SCALE = 14
MARGIN = 50


def main():
    design = json.loads((ROOT/'design.json').read_text())
    tree,pads,segments,vias,holes = read_board_geometry(ROOT/f'{NAME}.kicad_pcb')
    width,height = design['size']
    image = Image.new('RGB',(round(width*SCALE)+MARGIN*2,round(height*SCALE)+MARGIN*2+60),'#111a20')
    draw = ImageDraw.Draw(image)

    def xy(x,y):
        return (round(MARGIN+x*SCALE),round(MARGIN+y*SCALE))

    def bounds(x1,y1,x2,y2):
        return (*xy(x1,y1),*xy(x2,y2))

    fonts = ['/System/Library/Fonts/Supplemental/Arial.ttf','/System/Library/Fonts/Helvetica.ttc']
    font_path = next((p for p in fonts if Path(p).exists()),None)

    def font(size):
        return ImageFont.truetype(font_path,max(8,round(size*SCALE))) if font_path else ImageFont.load_default()

    draw.rectangle(bounds(0,0,width,height), fill='#154e3d',outline='#d6b867',width=2)
    for k in design.get('keepouts',[]):
        x1,y1,x2,y2=k['bounds']
        draw.rectangle(bounds(x1,y1,x2,y2),fill='#24473e',outline='#d8926c',width=2)
        draw.text(xy((x1+x2)/2,(y1+y2)/2),k['name'],font=font(.75),fill='#f7c8a0',anchor='mm')
    overlay=Image.new('RGBA',image.size)
    copper=ImageDraw.Draw(overlay)
    for fill in filled_zone_geometry(tree):
        color=(47,105,84,140) if fill['net']=='GND' else (190,138,77,160)
        shapes=[fill['shape']] if fill['shape'].geom_type=='Polygon' else list(fill['shape'].geoms)
        for shape in shapes:
            copper.polygon([xy(x,y) for x,y in shape.exterior.coords],fill=color)
            for ring in shape.interiors:
                copper.polygon([xy(x,y) for x,y in ring.coords],fill=(0,0,0,0))
    for layer,color in [(1,(70,147,248,180)),(0,(242,114,92,235))]:
        for seg in segments:
            if seg['layer']==layer:
                copper.line([xy(*seg['start']),xy(*seg['end'])],fill=color,width=max(1,round(seg['width']*SCALE)))
                for end in [seg['start'],seg['end']]:
                    r=seg['width']/2
                    copper.ellipse(bounds(end[0]-r,end[1]-r,end[0]+r,end[1]+r),fill=color)
    image=Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')
    draw=ImageDraw.Draw(image)
    for pad in pads:
        x,y=pad['x'],pad['y']
        w,h=pad['size']
        color='#d9bf70' if pad.get('net') else '#b3aa85'
        if pad['shape']=='circle' or pad['shape']=='oval':
            draw.ellipse(bounds(x-w/2,y-h/2,x+w/2,y+h/2),fill=color)
        else:
            draw.rectangle(bounds(x-w/2,y-h/2,x+w/2,y+h/2),fill=color)
        if pad.get('drill'):
            r=pad['drill']/2
            draw.ellipse(bounds(x-r,y-r,x+r,y+r),fill='#101b1d')
    for via in vias:
        x,y=via['x'],via['y']
        for r,color in [(via['size']/2,'#c7af67'),(via['drill']/2,'#142d2b')]:
            draw.ellipse(bounds(x-r,y-r,x+r,y+r),fill=color)
    for hole in holes:
        r=hole['drill']/2
        draw.ellipse(bounds(hole['x']-r,hole['y']-r,hole['x']+r,hole['y']+r),fill='#111a20',outline='#839b96',width=2)
    for module in design.get('module_outlines',[]):
        x1,y1,x2,y2=module['bounds']
        for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
            length=math.dist(a,b)
            for i in range(math.ceil(length/1.5)):
                t1=i*1.5/length
                t2=min((i*1.5+.8)/length,1)
                draw.line([xy(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1),
                           xy(a[0]+(b[0]-a[0])*t2,a[1]+(b[1]-a[1])*t2)],fill='#a9cbc0',width=1)
    for g in items(tree,'gr_text'):
        if item(g,'layer')[1] != 'F.SilkS':
            continue
        at=item(g,'at')
        e=item(g,'effects')
        size=item(item(e,'font'),'size')[1]
        draw.text(xy(at[1],at[2]),g[1],font=font(size),fill='#f0efe0',anchor='mm',align='center')
    for fp in items(tree,'footprint'):
        at=item(fp,'at')
        if at is None:
            at=item(item(fp,'transform'),'translate')
        fields=[g for g in items(fp,'fp_text') if str(g[1])=='reference']
        fields += [g for g in items(fp,'property') if g[1]=='Reference']
        for g in fields:
            loc=item(g,'at')
            draw.text(xy(at[1]+loc[1],at[2]+loc[2]),g[2],font=font(.8),fill='#f0efe0',anchor='mm')
    draw.text((MARGIN,18),'DUAL LR2021 USB TEST CARRIER  |  REV A',font=font(1.1),fill='#ecf1ee')
    draw.text((MARGIN,image.height-45),f'{width:g} x {height:g} mm  |  Top inspection view  |  Red: front copper  Blue: back copper',font=font(.9),fill='#c6d5d0')
    report_path=ROOT/'build'/'native-summary.json'
    passed=report_path.exists() and json.loads(report_path.read_text()).get('status')=='pass'
    status='KiCad ERC/DRC passed; physical validation pending.' if passed else 'KiCad ERC/DRC pending.'
    draw.text((MARGIN,image.height-25),'Dashed outlines show plug-in module bodies. '+status,font=font(.8),fill='#c6d5d0')
    output=ROOT/'build'/'carrier-top.png'
    output.parent.mkdir(exist_ok=True)
    image.save(output)
    print(output)


if __name__=='__main__':
    main()
