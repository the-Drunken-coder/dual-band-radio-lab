"""Rev A installed-view placement coordinates, in millimetres.
Daughtercard origins are slot A1. Carrier coordinates are board coordinates.
"""
SLOTS={1:(20,25),2:(155,125),3:(20,125),4:(155,25)}
BOARDS={
 'e22-900m30s-rev-a':dict(outline=(-12,-12,72,68),parts={
 'J1':(0,0,0),'J2':(30.48,0,0),'H1':(7.62,5.08,0),'U1':(39,0,0),
 'R5':(35.6,12.77,180),'C1':(53,49,0),'C2':(69,9,0),'C3':(69,4,0),
 'R1':(36,20,90),'R2':(36,24,90),'R3':(69,20,90),'R4':(69,24,90)}),
 'e28-2g4m27s-rev-a':dict(outline=(-12,-12,72,68),parts={
 'J1':(0,0,0),'J2':(30.48,0,0),'H1':(7.62,5.08,0),'U1':(43,0,0),'R5':(39.6,5.23,180),
 'U2':(8,42,0),'L1':(13.5,41.6,0),'C4':(9.4,37.5,0),
 'C1':(6.8,45.5,0),'C8':(6.8,49.1,0),'C2':(13.5,47,180),'C3':(13.5,50.5,180),'C7':(13.5,54,180),
 'C5':(6,61.5,0),'C6':(39.5,1.5,90),'R1':(36,15,90),'R2':(61.5,9,90),'R3':(65,13,90),'R4':(39.5,11,90)}),
 'core2021-hf-m-rev-a':dict(outline=(-12,-12,72,68),parts={
 'J1':(0,0,0),'J2':(30.48,0,0),'H1':(7.62,5.08,0),
 'J3':(43,2,0),'J4':(58.24,19.78,180),'R3':(62.8,14.7,0),
 'U2':(8,42,0),'C1':(3.5,38,0),'C2':(12.5,38,180),'C4':(43,25,0),'C3':(48,24,0),
 'R1':(62,7,90),'R2':(62,20,90)})}
cp={'J9':(119,195,180),'J10':(106,12,0),'J11':(123.78,60.26,180),
 'U2':(113,181,0),'Q1':(131,18,0),'U3':(115,155,0),
 'U4':(111,112,0),'U5':(112,82,0),'U6':(130,82,0),'U7':(122,95,0),
 'R20':(118,80.375,0),'R21':(120,82,0),'R22':(103.3,120.255,180),
 'R1':(109,177,90),'R2':(107,177,90),'R3':(109,183,90),'R4':(107,183,90),
 'R5':(120,173.5,90),'R19':(117,183,0),'C1':(120,183,0),'C2':(105,188,180),
 'C3':(125,167,0),'C4':(110.5,158,90),'C5':(119.5,158,90),'C6':(102.5,116.5,0),
 'C7':(107,75,90),'C8':(117,75,90),'C9':(125,75,90),'C10':(135,75,90),
 'C11':(118,92,90),'C12':(125,92,90),'R6':(105,73,90),'R7':(135,18,90),
 'R8':(119,105,90),'R9':(102,112,0),'R10':(132,110,90),'R11':(116,170,90),'R12':(124,154,90),
 'R13':(102,66,90),'R14':(102,30,90),'R15':(102,50,90),'R16':(102,42,90),'R17':(128,30,90),'R18':(102,56,90)}
for s,(x,y) in SLOTS.items():
 cp['J'+str(2*s-1)]=(x,y,0);cp['J'+str(2*s)]=(x+30.48,y,0);cp['H'+str(s)]=(x+7.62,y+5.08,0)
BOARDS['carrier-rev-a']=dict(outline=(0,0,250,210),parts=cp)
# Each tuple: readable label, net, x, y, fitted ground clip versus bare probe pad.
for name,b in BOARDS.items():
 tp=[]
 def add(label,net,x,y,clip=False):tp.append(dict(label=label,net=net,x=x,y=y,clip=clip))
 if name=='carrier-rev-a':
  for s,(x,y) in SLOTS.items():
   # Outside installed card silhouette, with clip access from the central corridor.
   tx=97 if x==20 else 138
   add(f'S{s}_5V','RADIO_5V',tx,y+1)
   for i,n in enumerate(['CS_N','BUSY','IRQ','RESET_N']+([] if s==2 else ['TX_EN','RX_EN'])):add(f'S{s}_{n}',f'S{s}_{n}',tx,y+8+5*i)
   add(f'S{s}_GND','GND',tx,y+44,True)
  for label,net,x,y in [('IN_5V','EXT_5V',104,195),('BUS_5V','RADIO_5V',130,181),('VBUS','USB_VBUS',136,12),('VSYS','PICO_VSYS',136,24),('PICO_3V3','PICO_3V3',132,58),('IOREF_3V3','IOREF_3V3',126,158),('UVLO','UVLO',103,175),('OVLO','OVLO',103,183),('DVDT','DVDT',123,184),('ILIM','ILIM',124,175),('EXP_CS','EXP_CS_N',103,106),('EXP_RST','EXP_RESET_N',122,105),('OE_N','P_IO_OE_N',102,72),('P_SCK','P_SPI_SCK',104,78),('P_MOSI','P_SPI_MOSI',104,82),('P_MISO','P_SPI_MISO',118,96),('SCK','SPI_SCK',124,80.375),('MOSI','SPI_MOSI',124,83.375),('MISO','SPI_MISO',126,96)]:add(label,net,x,y)
  add('ENTRY_GND','GND',135,195,True);add('U3_GND','GND',113,162)
 else:
  for i,n in enumerate(['SPI_SCK','SPI_MOSI','SPI_MISO','CS_N','RESET_N']):add(n,n,(-2 if name.startswith('e22') else 2) if i<3 else -4,10.16+2.54*i)
  for i,n in enumerate(['BUSY','IRQ']+([] if name.startswith('core') else ['TX_EN','RX_EN'])):add(n,n,34.5,i*2.54)
  add('IN_5V','SLOT_5V',-4,3);add('CLIP_GND','GND',-4,60,True)
  add('AUX0','AUX0',34.5,37)
  if name.startswith('e22'):
   add('MOD_5V','SLOT_5V',66.5,0);add('MOD_GND','GND',70,-3)
   add('IOREF','IOREF_3V3',34.5,30)
  else:
   add('OUT_3V3','RADIO_3V3',17,51 if name.startswith('e28') else 47)
   add('REG_GND','GND',17,54 if name.startswith('e28') else 50)
   add('EN_5V','SLOT_5V',3.5,41)
   if name.startswith('e28'):
    add('SW','SW',10.1,39.7);add('FB','RADIO_3V3',5,38.7)
    add('MOD_3V3','RADIO_3V3',39.5,-2);add('MOD_GND','GND',36,-2);add('SW_GND','GND',12.8,36.5)
   else:add('MOD_3V3','RADIO_3V3',48,26);add('MOD_GND','GND',51,26)
 b['testpoints']={f'TP{i}':t for i,t in enumerate(tp,1)}
 for r,t in b['testpoints'].items():b['parts'][r]=(t['x'],t['y'],0)
