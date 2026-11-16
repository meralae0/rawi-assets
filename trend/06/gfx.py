import sys; sys.path.insert(0,'/home/claude/rawi-assets/tools')
import reportage_gfx as g
from PIL import Image, ImageDraw, ImageFilter
g.badge.__defaults__=('ترند',)
_st=g.source_tag; g.source_tag=lambda c,s: _st(c,s) if s else None
W,H=1920,1080
g.calendar(17,'نوفمبر',2026,'الثلاثاء').save('g/cal17.png')
g.calendar(16,'سبتمبر',2026,'إعلانٌ رسمي').save('g/cal16sep.png')
g.calendar(4,'أكتوبر',2023,'آخر اختبار وطني').save('g/cal2023.png')
g.calendar(13,'نوفمبر',2026,'الجمعة').save('g/cal13.png')
# social posts in several languages
bg=g.kraft(); posts=[('GLOBAL BLACKOUT — NOVEMBER 17','No power. No internet. No banks.',False),
 ('Apagón mundial el 17 de noviembre','Sin luz, sin internet, sin bancos',False),
 ('انقطاع عالمي يوم 17 نوفمبر!','الكهرباء… الإنترنت… البنوك',True),
 ('Panne mondiale le 17 novembre ?','Électricité, internet, banques…',False)]
for i,(a,b,ar) in enumerate(posts):
    c=Image.new('RGB',(900,190),(255,255,255)); d=ImageDraw.Draw(c)
    d.ellipse((24,24,84,84),fill=(180,180,190)); d.rounded_rectangle((100,34,330,52),8,fill=(225,225,230))
    fa=g.F(g.FB,40); fb=g.F(g.FR,32)
    if ar:
        g.text(d,(870,100),a,fa,g.RED,anchor='rm'); g.text(d,(870,150),b,fb,(90,90,90),anchor='rm')
    else:
        d.text((30,90),a,font=fa,fill=g.RED); d.text((30,140),b,font=fb,fill=(90,90,90))
    x=[140,880,180,860][i]; y=[110,300,520,740][i]
    g.shadow_paste(bg,c,(x,y),angle=[-2,1.5,-1,2][i])
g.sticker(bg,'شائعة',(1560,150),angle=6,color=g.RED,fg=(255,255,255),size=60)
g.badge(bg).save('g/posts.png')
g.title_card('BLACKOUT','كلمةٌ واحدة… تكفي').save('g/word.png')
doc=g.doc_card('docs.fcc.gov — DA 26-989',['PUBLIC SAFETY AND HOMELAND SECURITY BUREAU ANNOUNCES','NATIONWIDE TEST OF THE EMERGENCY ALERT SYSTEM (EAS)','ON NOVEMBER 17, 2026'],['اختبارٌ وطني لنظام الإنذار','في حالات الطوارئ — 17 نوفمبر 2026'],'')
doc.save('g/doc.png'); doc.filter(ImageFilter.GaussianBlur(14)).save('g/doc_blur.png')
im=g.bignum('14:20','بتوقيت نيويورك'); im.save('g/t_ny.png')
g.bignum('19:20','بتوقيت المغرب',color=(20,110,60)).save('g/t_ma.png')
g.doc_card('Emergency Alert System — FEMA',['"This is a nationwide test of the Emergency Alert System…','This is only a test. No action is required by the public."'],['هذا مجرد اختبار.','لا يُطلب من الجمهور أي إجراء.'],'').save('g/msg.png')
g.list_card('ما الذي لن يحدث غدًا؟',['لا انقطاع للكهرباء','لا توقف للإنترنت','لا رسائل على الهواتف']).save('g/list.png')
g.bignum('3','مرةً كل 3 سنوات على الأقل').save('g/every3.png')
g.title_card('ابحث عن المصدر','قبل أن تشارك أي تحذير').save('g/source.png')
g.title_card('اشتركوا في القناة','ترند | الراوي').save('g/end.png')
print('ok')
