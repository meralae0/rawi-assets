# New graphics: real-map journey, real topo map schemes, portrait grid
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import build as B
W,H=1920,1080
_cache={}
def sverd_dark():
    if 'sv' in _cache: return _cache['sv']
    im=Image.open('maps/sverd.png').convert('L')
    a=ImageOps.autocontrast(im)
    # light fill -> navy, lines -> light steel
    lut=[int(v) for v in range(256)]
    navy=Image.new('RGB',im.size,(16,28,52)); line=Image.new('RGB',im.size,(110,140,185))
    mask=a.point(lambda v:255 if v<170 else 0).filter(ImageFilter.MaxFilter(3))
    out=Image.composite(line,navy,mask)
    # outside region (very light grey bg ~ 247) -> darker
    bgm=a.point(lambda v:255 if v>=246 else 0)
    out=Image.composite(Image.new('RGB',im.size,(16,28,52)),out,bgm)
    can=Image.new('RGB',(out.width+1600,out.height+1500),(16,28,52)); can.paste(out,(800,1500))
    _cache['sv']=can; return can
PTS=[(2127,5184,'سفيردلوفسك','قطار'),(2061,2435,'إيفديل','شاحنة'),(2042,2050,'فيجاي','زلاجات'),(1704,1675,'خولات سياخل',''),(1627,1600,'أوتورتن','')]
def g_map(t,D):
    sv=sverd_dark()
    k=B.ease(t/(D*0.75))
    segs=len(PTS)-1; pos=k*segs; i=min(int(pos),segs-1); f=pos-i
    hx=PTS[i][0]+(PTS[i+1][0]-PTS[i][0])*f; hy=PTS[i][1]+(PTS[i+1][1]-PTS[i][1])*f
    hm=2600-1250*k; wm=hm*16/9
    cx=min(max(hx,wm/2),sv.width-wm/2); cy=min(hy-0.12*hm,sv.height-hm/2)
    box=(int(cx-wm/2),int(cy-hm/2),int(cx+wm/2),int(cy+hm/2))
    im=sv.crop(box).resize((W,H),Image.BILINEAR)  # crop pads beyond edges with black
    sc=W/(box[2]-box[0])
    P=lambda x,y:((x-box[0])*sc,(y-box[1])*sc)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    path=[P(*PTS[j][:2]) for j in range(i+1)]+[P(hx,hy)]
    for wdt,col in ((26,(255,190,0,70)),(10,(255,206,0,255))):
        d.line(path,fill=col,width=wdt,joint='curve')
    hp=P(hx,hy); r=14+4*math.sin(t*6)
    d.ellipse([hp[0]-r-10,hp[1]-r-10,hp[0]+r+10,hp[1]+r+10],fill=(255,206,0,60)); d.ellipse([hp[0]-r,hp[1]-r,hp[0]+r,hp[1]+r],fill=(255,206,0,255))
    for j,(x,y,n,mode) in enumerate(PTS):
        if pos+0.02<j: continue
        p=P(x,y); c=(210,30,45,255) if j>=3 else (255,255,255,255)
        d.ellipse([p[0]-15,p[1]-15,p[0]+15,p[1]+15],fill=c,outline=(0,0,0,255),width=3)
        f2=B.ca(50); tw=f2.getlength(n)
        lx=p[0]+34 if j<3 else p[0]-34
        if j<3: d.rounded_rectangle([lx-10,p[1]-38,lx+tw+20,p[1]+36],10,fill=(0,0,0,170)); d.text((lx+tw+5,p[1]),n,font=f2,fill=(255,255,255,255),anchor='rm',direction='rtl')
        else: d.rounded_rectangle([lx-tw-20,p[1]-38,lx+10,p[1]+36],10,fill=(0,0,0,170)); d.text((lx-5,p[1]),n,font=f2,fill=c,anchor='rm',direction='rtl')
    im=im.convert('RGBA'); im.alpha_composite(ov)
    d=ImageDraw.Draw(im)
    B.gtext(d,(1590,110),'الرحلة: من سفيردلوفسك إلى الجبال',64,B.Y,font=B.ca(64))
    if i<3 and PTS[i][3]:
        B.gtext(d,(1590,190),'المرحلة: '+PTS[i][3],46,B.ICE)
    if t>D*0.7: 
        d.rounded_rectangle([1590-640,170,1590,250],14,fill=(0,0,0,180)); B.gtext(d,(1565,210),'≈ 300 كم على الزلاجات في الجبال',44,B.WH)
    return im.convert('RGB')
# --- topo map (tent -> cedar), coordinates from the 1280x748 preview, x3 for full res
S3=3.0
TENT=(272,490); CEDAR=(1045,290); RAV=(1010,282)
BODIES=[((871,357),'dyatlov','دياتلوف — 300 م'),((823,389),'slobodin','سلوبودين — 480 م'),((711,392),'kolmogorova','كولموغوروفا — 630 م')]
def topo_base():
    if 'tp' in _cache: return _cache['tp']
    im=Image.open('maps/fancy.png').convert('RGB')
    box=(int(70*S3),int(52*S3),int(1210*S3),int(693*S3))
    for r in ((170,398,280,452),(925,312,1080,362),(900,260,1018,296)):
        rr=tuple(int(v*S3) for v in r); patch=im.crop((rr[0]-60,rr[1]-60,rr[2]+60,rr[3]+60)).filter(ImageFilter.GaussianBlur(45))
        im.paste(patch.crop((60,60,60+rr[2]-rr[0],60+rr[3]-rr[1])),rr[:2])
    im=im.crop(box)
    im=ImageEnhance.Color(im).enhance(0.55); im=ImageEnhance.Brightness(im).enhance(0.62)
    _cache['tp']=(im,box); return _cache['tp']
def portrait(name,size=150):
    p=Image.open(f'real/f_{name}.jpg').convert('RGB').resize((size,int(size*1.31)))
    m=Image.new('L',p.size,0); ImageDraw.Draw(m).ellipse([4,4,p.width-4,p.height-4],fill=255)
    o=Image.new('RGBA',(p.width+12,p.height+12),(0,0,0,0)); d=ImageDraw.Draw(o); d.ellipse([0,0,o.width-1,o.height-1],fill=(255,255,255,255))
    o.paste(p,(6,6),m); return o
def g_topo(name,t,D):
    base,box=topo_base()
    z=1.0+0.08*B.ease(t/D)
    zx,zy={'scheme1':(0.55,0.5),'scheme2':(0.68,0.45),'scheme3':(0.86,0.4)}[name]
    wv=base.width/z; hv=base.height/z
    cx=base.width*zx; cy=base.height*zy
    cx=min(max(cx,wv/2),base.width-wv/2); cy=min(max(cy,hv/2),base.height-hv/2)
    b2=(cx-wv/2,cy-hv/2,cx+wv/2,cy+hv/2)
    im=base.crop(tuple(int(v) for v in b2)).resize((W,H),Image.BILINEAR).convert('RGBA')
    sc=W/(b2[2]-b2[0])
    def P(xy):
        x=(xy[0]*S3-box[0]-b2[0])*sc; y=(xy[1]*S3-box[1]-b2[1])*sc; return (x,y)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # cover english labels: tent label, cedar label, raving
    for xy,wh in (((225,428),(140,60)),((1000,340),(160,55)),((958,278),(120,35))):
        p=P(xy); d.rectangle([p[0]-wh[0]*sc*S3/2/1.0*0+(-wh[0]*S3*sc/2),p[1]-wh[1]*S3*sc/2,p[0]+wh[0]*S3*sc/2,p[1]+wh[1]*S3*sc/2],fill=(0,0,0,0))
    tp=P(TENT); cp=P(CEDAR)
    k=B.ease(t/2.2) if name=='scheme1' else 1.0
    # footprint trail tent -> cedar
    n=int(40*k)
    for s in range(n):
        f=s/40; x=tp[0]+(cp[0]-tp[0])*f; y=tp[1]+(cp[1]-tp[1])*f+math.sin(f*20)*6
        d.ellipse([x-5,y-5,x+5,y+5],fill=(255,206,0,230))
    def pin(p,txt,col,lp):
        d.ellipse([p[0]-18,p[1]-18,p[0]+18,p[1]+18],fill=col,outline=(255,255,255,255),width=4)
        f=B.tj(42); tw=f.getlength(txt)
        d.rounded_rectangle([lp[0]-tw/2-22,lp[1]-34,lp[0]+tw/2+22,lp[1]+34],10,fill=(0,0,0,215))
        d.text(lp,txt,font=f,fill=(255,255,255,255),anchor='mm',direction='rtl')
    pin(tp,'الخيمة',(90,110,200,255),P((225,425))); pin(cp,'شجرة الصنوبر',(40,140,70,255),P((1003,337)))
    if name!='scheme3':
        lp=P((958,278)); f=B.tj(34); d.rounded_rectangle([lp[0]-70,lp[1]-26,lp[0]+70,lp[1]+26],8,fill=(0,0,0,200)); d.text(lp,'الوادي',font=f,fill=(255,255,255,255),anchor='mm',direction='rtl')
    im.alpha_composite(ov); d=ImageDraw.Draw(im)
    title={'scheme1':'من الخيمة إلى الشجرة','scheme2':'أين وُجد الآخرون على المنحدر','scheme3':'الوادي — 4 مايو 1959'}[name]
    d.rounded_rectangle([1590-B.ca(60).getlength(title)-50,70,1610,160],14,fill=(0,0,0,170))
    B.gtext(d,(1590,115),title,60,B.Y,font=B.ca(60))
    if name=='scheme1':
        if t>1.6:
            m=((tp[0]+cp[0])/2,(tp[1]+cp[1])/2-70); f=B.ca(70)
            d.rounded_rectangle([m[0]-170,m[1]-50,m[0]+170,m[1]+50],14,fill=(210,30,45))
            d.text(m,'≈ 1.5 كم',font=f,fill=(255,255,255),anchor='mm',direction='rtl')
        for j,nm in enumerate(('krivonishenko','doroshenko')):
            if t>3.0+j*0.6:
                pr=portrait(nm,130); im.alpha_composite(pr,(int(cp[0]-420+j*150),int(cp[1]+150)))
    if name=='scheme2':
        for j,(xy,nm,lab) in enumerate(BODIES):
            if t<0.6+j*1.6: continue
            p=P(xy); d.ellipse([p[0]-16,p[1]-16,p[0]+16,p[1]+16],fill=(210,30,45),outline=(255,255,255),width=4)
            pr=portrait(nm,110); px=int(p[0]-pr.width/2); py=int(p[1]+40) if j%2==0 else int(p[1]-40-pr.height-60)
            im.alpha_composite(pr,(px,py)); d=ImageDraw.Draw(im)
            f=B.tj(36); tw=f.getlength(lab); d.rounded_rectangle([p[0]-tw/2-12,py+pr.height+6,p[0]+tw/2+12,py+pr.height+56],8,fill=(0,0,0,200))
            d.text((p[0],py+pr.height+31),lab,font=f,fill=(255,255,255),anchor='mm',direction='rtl')
    if name=='scheme3':
        rp=P(RAV)
        if t>0.8:
            d.ellipse([rp[0]-70,rp[1]-40,rp[0]+70,rp[1]+40],outline=(210,30,45),width=8)
            f=B.tj(44); txt='الوادي — 75 م من الشجرة'; tw=f.getlength(txt); lp=P((958,278))
            d.rounded_rectangle([lp[0]+70-tw-40,lp[1]-34,lp[0]+70,lp[1]+34],10,fill=(0,0,0,215)); d.text((lp[0]+50,lp[1]),txt,font=f,fill=(255,255,255),anchor='rm',direction='rtl')
        for j,nm in enumerate(('thibeaux','dubinina','zolotaryov','kolevatov')):
            if t>2.0+j*0.5:
                pr=portrait(nm,115); im.alpha_composite(pr,(int(760+j*150),780))
        if t>2.0:
            d=ImageDraw.Draw(im); B.gtext(d,(1060,1020),'الأربعة الأخيرون — تحت 4 أمتار من الثلج',44,B.WH,anchor='mm')
    return im.convert('RGB')
NM=[('dyatlov','إيغور دياتلوف',23),('kolmogorova','زينايدا كولموغوروفا',22),('dubinina','لودميلا دوبينينا',20),('doroshenko','يوري دوروشينكو',21),('krivonishenko','يوري كريفونيشينكو',23),('slobodin','روستم سلوبودين',23),('kolevatov','ألكسندر كوليفاتوف',24),('thibeaux','نيكولاي تيبو-بريينول',23),('zolotaryov','سيميون زولوتاريوف',38)]
HL={'kolmogorova':(0.36,0.5),'dubinina':(0.45,0.6),'zolotaryov':(0.62,0.95)}
def g_members(t,D):
    im=B.BG.copy().convert('RGBA'); d=ImageDraw.Draw(im)
    B.gtext(d,(1590,105),'المجموعة: 9 متسلّقين… والعاشر عاد',64,B.Y,font=B.ca(64))
    for i,(k,n,a) in enumerate(NM):
        e=B.eob((t-0.2-i*0.18)/0.5)
        if e<=0: continue
        col,row=i%5,i//5
        cx=1580-col*330; cy=370+row*400
        hl=k in HL and HL[k][0]*D<=t<=HL[k][1]*D
        size=int((150 if not hl else 180)*min(1,e))
        if size<10: continue
        pr=portrait(k,size)
        if hl:
            g=Image.new('RGBA',(pr.width+60,pr.height+60),(0,0,0,0)); ImageDraw.Draw(g).ellipse([0,0,g.width-1,g.height-1],fill=(255,206,0,150)); g=g.filter(ImageFilter.GaussianBlur(14))
            im.alpha_composite(g,(int(cx-g.width/2),int(cy-g.height/2)))
        im.alpha_composite(pr,(int(cx-pr.width/2),int(cy-pr.height/2)))
        d=ImageDraw.Draw(im); f=B.tj(30 if not hl else 34)
        d.text((cx,cy+pr.height/2+34),n,font=f,fill=B.Y if hl else B.WH,anchor='mm',direction='rtl')
        d.text((cx,cy+pr.height/2+76),f'{a} عامًا',font=B.tj(30),fill=(170,180,200),anchor='mm',direction='rtl')
    # Yudin card (no photo)
    if t>2.0:
        cx,cy=1580-4*330,770
        d.ellipse([cx-78,cy-100,cx+78,cy+100],fill=(30,40,60),outline=(120,130,150),width=4)
        d.text((cx,cy),'؟',font=B.ca(110),fill=(120,130,150),anchor='mm')
        d.text((cx,cy+134),'يوري يودين',font=B.tj(34),fill=(150,150,150),anchor='mm',direction='rtl')
        d.text((cx,cy+176),'عاد في 28 يناير',font=B.tj(30),fill=(150,150,150),anchor='mm',direction='rtl')
    return im.convert('RGB')
