"""Render the Markdown review as a readable ReportLab PDF."""
from pathlib import Path
import re,html
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Preformatted,KeepTogether,PageBreak,Image
ROOT=Path(__file__).resolve().parent
FONT=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('Review','DejaVuSans.ttf'),('Review-Bold','DejaVuSans-Bold.ttf'),('Review-Italic','DejaVuSans-Oblique.ttf'),('ReviewMono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Review',normal='Review',bold='Review-Bold',italic='Review-Italic',boldItalic='Review-Bold')
green=colors.HexColor('#2e493b');ink=colors.HexColor('#202b27');muted=colors.HexColor('#53615b')
styles={
 'body':ParagraphStyle('body',fontName='Review',fontSize=9.7,leading=13.4,textColor=ink,spaceAfter=6),
 'h1':ParagraphStyle('h1',fontName='Review-Bold',fontSize=24,leading=29,textColor=green,spaceAfter=16,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='Review-Bold',fontSize=14,leading=17,textColor=green,spaceBefore=10,spaceAfter=5,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='Review-Bold',fontSize=11.8,leading=16,textColor=green,spaceBefore=10,spaceAfter=5,keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='Review',fontSize=8.6,leading=12.1,textColor=ink),
 'headcell':ParagraphStyle('headcell',fontName='Review-Bold',fontSize=8.6,leading=12.1,textColor=colors.white),
 'code':ParagraphStyle('code',fontName='ReviewMono',fontSize=7.8,leading=11,textColor=ink,spaceAfter=9,leftIndent=10),
 'bullet':ParagraphStyle('bullet',fontName='Review',fontSize=9.7,leading=13.4,textColor=ink,spaceAfter=3.0,leftIndent=11,firstLineIndent=-9),
}
def inline(s):
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:'<link href="'+m.group(2)+'" color="#2e493b"><u>'+m.group(1)+'</u></link>',s)
    s=re.sub(r'`([^`]+)`',lambda m:'<font name="ReviewMono" size="8.1">'+m.group(1)+'</font>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',s)
    return s
def footer(canvas,doc):
    canvas.saveState();w,h=letter
    canvas.setStrokeColor(colors.HexColor('#b8c6bc'));canvas.line(46,39,w-46,39)
    canvas.setFont('Review',7.2);canvas.setFillColor(muted)
    canvas.drawString(46,27,'Force 136 Digital Deck v1.0.0 | App audit | 21 November 2026')
    canvas.drawRightString(w-46,27,str(doc.page));canvas.restoreState()
lines=(ROOT/'REPORT.md').read_text().splitlines();story=[];i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line.startswith('```'):
        code=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
        story.append(Preformatted('\n'.join(code),styles['code']));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            bits=[x.strip() for x in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+',x) for x in bits):rows.append(bits)
            i+=1
        n=len(rows[0]);widths={2:[167,353],3:[160,100,260],4:[80,108,180,152],5:[104,104,92,100,120]}[n]
        if rows[0][0]=='J13 policy/position':widths=[175,65,280]
        data=[[Paragraph(inline(c),styles['headcell' if ri==0 else 'cell']) for c in r] for ri,r in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),green),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.7,green),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#c5d0c8')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f5f1'),colors.white])]))
        group=[t,Spacer(1,10)]
        if story and isinstance(story[-1],Paragraph) and story[-1].style.name in ('h2','h3'):
            group.insert(0,story.pop())
        story.extend(group);continue
    if line.startswith('#'):
        level=len(line)-len(line.lstrip('#'));story.append(Paragraph(inline(line[level:].strip()),styles[f'h{min(level,3)}']));i+=1;continue
    if line.startswith('- ') or re.match(r'^\d+\. ',line):
        story.append(Paragraph(inline(line),styles['bullet']));i+=1;continue
    p=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ')):
        p.append(lines[i]);i+=1
    story.append(Paragraph(inline(' '.join(p)),styles['body']))
out=ROOT/'Force_136_Digital_Deck_v1.0.0_Audit.pdf'
doc=SimpleDocTemplate(str(out),pagesize=letter,leftMargin=46,rightMargin=46,topMargin=40,bottomMargin=48,title='Force 136 Digital Deck v1.0.0 - Comprehensive Audit',author='Astra / Codex',pageCompression=1)
story.append(PageBreak())
story.append(Paragraph('Browser evidence',styles['h2']))
story.append(Paragraph('F1 - Live production readback after changing the inputs, retained in evidence/browser-evidence.json:',styles['body']))
story.append(Preformatted('Resistance: 0\nFinal Propaganda: false\nResult: Force 136 wins. Japan loses.',styles['code']))
from PIL import Image as PILImage
for name,maxw,maxh in [('F3-mobile-detail.jpg',230,480)]:
    if name.startswith('F3'):story.append(Paragraph('F3 - Exact release in a narrow frame: Raid opens partway down, with its heading and first restriction above the visible area.',styles['body']))
    p=ROOT/'evidence'/name
    w,h=PILImage.open(p).size
    scale=min(maxw/w,maxh/h)
    im=Image(str(p),width=w*scale,height=h*scale);im.hAlign='LEFT'
    story.extend([im,Spacer(1,12)])
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
