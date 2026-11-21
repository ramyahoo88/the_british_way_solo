"""Build the Force 136 v1.0 print package: rules, reference sheet, cards, combined PDF.

Usage: python3 build.py [outdir]
Needs: python-markdown, Google Chrome (headless), pypdf.
"""
import json,subprocess,sys,html,re
from pathlib import Path
import markdown
from pypdf import PdfWriter,PdfReader

HERE=Path(__file__).resolve().parent
OUT=(Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'out').resolve()
OUT.mkdir(parents=True,exist_ok=True)
CARDS=json.loads((HERE/'cards.json').read_text())
VERSION='1.0';DATE='21 November 2026'

BASE_CSS="""
@page{size:Letter;margin:0.6in 0.65in 0.65in 0.65in}
*{box-sizing:border-box}
body{font-family:'Inter','DejaVu Sans',sans-serif;font-size:9.6pt;line-height:1.42;color:#1e1f1a;margin:0}
h1,h2,h3{font-family:'Bitter','Lora','DejaVu Serif',serif;color:#2f3a22;margin:0}
strong{color:#14170f}
.muted{color:#5d6152}
"""

RULES_CSS=BASE_CSS+"""
.cover{border-bottom:3px solid #2f3a22;padding-bottom:10pt;margin-bottom:12pt}
.cover h1{font-size:30pt;letter-spacing:.5pt}
.cover .sub{font-family:'Bitter',serif;font-size:13pt;color:#7a2618;margin-top:3pt}
.cover .meta{font-size:8.5pt;color:#5d6152;margin-top:4pt;text-transform:uppercase;letter-spacing:1pt}
.cols{column-count:2;column-gap:20pt}
h2{font-size:12.5pt;margin:12pt 0 4pt;padding-bottom:2pt;border-bottom:1px solid #b9b49a;break-after:avoid;column-span:none}
h3{font-size:10.5pt;margin:8pt 0 2pt;break-after:avoid}
p{margin:0 0 5pt}
ul,ol{margin:0 0 5pt;padding-left:15pt}
li{margin:0 0 2pt}
table{border-collapse:collapse;width:100%;margin:4pt 0 6pt;font-size:8.8pt;break-inside:avoid}
th,td{border:1px solid #b9b49a;padding:3pt 4pt;text-align:left;vertical-align:top}
th{background:#e9e5d3}
em{color:#3c4130}
.goal{break-inside:avoid}
"""

REF_CSS=BASE_CSS+"""
@page{size:Letter;margin:0.45in 0.5in}
body{font-size:9.2pt;line-height:1.32}
.hdr{display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #2f3a22;padding-bottom:3pt;margin-bottom:6pt}
.hdr h1{font-size:17pt}
.hdr .tag{font-size:7.5pt;text-transform:uppercase;letter-spacing:1pt;color:#7a2618}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:6pt}
.box{border:1.2px solid #2f3a22;border-radius:3pt;padding:5pt 6pt;break-inside:avoid}
.box h2{font-size:10.5pt;text-transform:uppercase;letter-spacing:.8pt;margin-bottom:3pt;color:#7a2618}
.turn ol{margin:0;padding-left:13pt}
.turn li{margin-bottom:2pt}
table{border-collapse:collapse;width:100%;font-size:9pt}
th,td{border:1px solid #b9b49a;padding:2pt 3pt;text-align:left;vertical-align:top}
th{background:#e9e5d3}
.full{grid-column:1 / span 2}
p{margin:0 0 5pt}
.k{font-weight:700;color:#14170f}
.chip{display:inline-block;padding:0 3pt;border-radius:2pt;font-weight:700;font-size:8.2pt;color:#fff}
"""

CARD_CSS=BASE_CSS+"""
@page{size:Letter;margin:0.2in 0.5in}
.sheet{display:grid;grid-template-columns:repeat(3,2.5in);grid-auto-rows:3.5in;gap:0;justify-content:center;margin-top:0.05in}
.card{width:2.5in;height:3.5in;border:0.6pt dashed #9a9a9a;padding:0.09in;position:relative}
.inner{width:100%;height:100%;border:2pt solid #2f3a22;border-radius:7pt;background:#f6f2e2;display:flex;flex-direction:column;overflow:hidden}
.top{background:#2f3a22;color:#efe9cf;padding:4pt 7pt 3pt;display:flex;justify-content:space-between;align-items:baseline}
.top .unit{font-family:'Bitter',serif;font-weight:700;font-size:8.5pt;letter-spacing:1.2pt}
.top .num{font-size:7.5pt;letter-spacing:.5pt}
.name{font-family:'Bitter',serif;font-weight:700;font-size:12.5pt;color:#7a2618;padding:5pt 7pt 2pt;line-height:1.1}
.lbl{font-size:6.8pt;text-transform:uppercase;letter-spacing:1pt;color:#5d6152;padding:3pt 7pt 1pt}
ol.goals{list-style:none;margin:0;padding:0 7pt}
ol.goals li{display:flex;align-items:center;margin:1.6pt 0;font-size:9.4pt;font-weight:700}
ol.goals li .n{width:12pt;height:12pt;border-radius:6pt;background:#2f3a22;color:#fff;font-size:7pt;display:inline-flex;align-items:center;justify-content:center;margin-right:5pt}
ol.goals li.fixed{color:#8a8b7c;font-weight:600}
ol.goals li.fixed .n{background:#a9a896}
.g{padding:1pt 5pt;border-radius:3pt;color:#fff;letter-spacing:.4pt}
.lim{margin:2pt 7pt 0;font-size:8.6pt;font-weight:700}
.foot{margin-top:auto;font-size:6.3pt;color:#5d6152;padding:3pt 7pt 5pt;border-top:1px solid #cfc8a6;line-height:1.25}
.stamp{position:absolute;right:15pt;top:40pt;font-family:'Bitter',serif;font-size:6.5pt;color:#7a2618;border:1pt solid #7a2618;padding:1pt 3pt;transform:rotate(8deg);letter-spacing:1pt;opacity:.8}
"""
GOAL_COL={'AMBUSH':'#8c2a1c','INTEL':'#24476b','SUPPLY':'#3d6b2a','TRAIN':'#8a6a12','PLACE':'#4c4c44','CONTACT':'#4c4c44'}

def chrome_pdf(html_text,pdf_path):
    tmp=pdf_path.with_suffix('.html');tmp.write_text(html_text,encoding='utf-8')
    subprocess.run(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--no-pdf-header-footer',
                    '--run-all-compositor-stages-before-draw','--virtual-time-budget=4000',
                    f'--print-to-pdf={pdf_path}',tmp.as_uri()],check=True,capture_output=True)
    return pdf_path

def page(css,body,title):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title><style>{css}</style></head><body>{body}</body></html>"

def build_rules():
    md=(HERE/'Force_136_v1_Rules.md').read_text(encoding='utf-8')
    # drop the markdown title block; render our own cover
    body_md=md.split('## 1. Overview',1)[1]
    body=markdown.markdown('## 1. Overview'+body_md,extensions=['tables'])
    cover=(f"<div class='cover'><h1>Force 136</h1><div class='sub'>A card-driven British opponent for "
           f"<em>The British Way: Japanese Occupation 1942–1945</em></div>"
           f"<div class='meta'>Unofficial fan variant · version {VERSION} · {DATE}</div></div>")
    return page(RULES_CSS,cover+f"<div class='cols'>{body}</div>",'Force 136 v1.0 Rules')

def chip(g):return f"<span class='chip' style='background:{GOAL_COL[g]}'>{g}</span>"

def build_reference():
    pre="""<p class='muted' style='margin:0 0 4pt'>Each card's MPAJA icon, then any Mandatory Event, is resolved once when the card is revealed, before either player acts; British choices use <span class='k'>Between turns</span>.</p>"""
    turn="""<div class='box turn'><h2>Force 136's turn</h2><ol>
<li><span class='k'>Draw</span> a Directive card (reshuffle the discards when empty); discard it after the turn.</li>
<li><span class='k'>Never</span> choose the Event box.</li>
<li><span class='k'>Op &amp; SA box free:</span> take it. First goal that qualifies: """+chip('PLACE')+""" → the goals on the card → """+chip('CONTACT')+""".</li>
<li><span class='k'>Otherwise Limited Operation:</span> """+chip('PLACE')+""" → the card's Limited choice → the other of AMBUSH/TRAIN → """+chip('CONTACT')+""". No Special Activity.</li>
<li><span class='k'>Nothing qualifies:</span> Pass in the leftmost free box (no Contact).</li>
</ol><p class='muted'>"Would" = test on the visible board first. Concealed chits count; never look at them. Later rolls count as successes. "Gather 2+" = 2 or more chits in total.</p></div>"""
    goals="""<div class='box full'><h2>Goals</h2><table>
<tr><th>Goal</th><th>Qualifies if</th><th>Do</th><th>Then (Op &amp; SA only; choose after the Operation is resolved)</th></tr>
<tr><td>"""+chip('PLACE')+"""</td><td>a F136 marker is Available</td><td>Contact: place it</td><td>Gather 2+ › Supply › Raid › Gather</td></tr>
<tr><td>"""+chip('AMBUSH')+"""</td><td>Ambush useful in a F136 space</td><td>Ambush in every useful F136 space</td><td>Gather 2+ › Raid › Gather</td></tr>
<tr><td>"""+chip('INTEL')+"""</td><td>Op &amp; SA only: the first of Ambush (every useful space) › Sabotage › Contact that would do something and then let Gather reveal 2+</td><td>that Operation</td><td>Gather</td></tr>
<tr><td>"""+chip('SUPPLY')+"""</td><td>Op &amp; SA only (Directive 9): Train places 1+ and Supply then converts a Camp</td><td>Train</td><td>Supply</td></tr>
<tr><td>"""+chip('TRAIN')+"""</td><td>Train would place 1+ guerrilla</td><td>Train</td><td>Supply › Raid</td></tr>
<tr><td>"""+chip('CONTACT')+"""</td><td>Contact would place or move a marker</td><td>Contact</td><td>Supply › Gather › Raid</td></tr>
</table></div>"""
    procs="""<div class='box full'><h2>Procedures</h2><div class='grid'><div>
<p><span class='k'>Place F136:</span> a Province without F136. No Kempeitai › no Cache (while a Cache is Available) › no cubes › most guerrillas › highest Population › map order. Add a Camp if none.</p>
<p><span class='k'>Move F136</span> (none Available): the first <em>exposed</em> marker in map order that can reach an adjacent Province without F136 or Kempeitai (placement preferences). Takes 1 blue (Underground first) if the destination has no red and another guerrilla stays.</p>
<p><span class='k'>Camp from the map</span> (none Available): prefer a Province without F136 › with a Cache › smallest Population › reverse map order.</p>
<p><span class='k'>Train:</span> every non-EC F136 space in map order; 1 guerrilla, 2 at a Cache. The colour the space has more of (tie red). Empty: red if Camp/Cache and red Available, else blue. Red needs a Camp or Cache, else skip. None of that colour Available: take one from a space without F136 that keeps a guerrilla at its Cache and keeps its majority. Source: has an Active of that colour › most cubes › map order; take an Active one if it can. None qualifies: stop training that space.</p>
<p><span class='k'>Ambush</span> (F136 space, or Raid destination, with an Underground guerrilla): good shot with Kempeitai or Troops → roll to move the Kempeitai, else a Troop (die + Caches &gt; cubes: +1 Resistance) › else Police → remove 1. Kuala Lumpur: Police only. Red before blue; spaces in map order.</p>
</div><div>
<p><span class='k'>Good shot:</span> cubes − Caches in and adjacent ≤ 3. <span class='k'>Exposed:</span> F136 with Kempeitai and no Camp (any F136 with Kempeitai under Japanese J22). <span class='k'>Majority:</span> more guerrillas than cubes.</p>
<p><span class='k'>Sabotage:</span> F136 spaces in map order; at each, if it still has an Underground guerrilla next to a clear railway, activate one (red first) and sabotage the first such railway on the Railway list.</p>
<p><span class='k'>Gather:</span> the F136 space revealing most chits (each needs an Underground guerrilla in its own space) › map order; reveal all, red first; then the next space (2; 3 with British J19; Japanese J19: later spaces reveal only their own chit).</p>
<p><span class='k'>Supply:</span> choose Provinces with F136 + Camp, no Cache (2; 3 at Zipper 12+; no more than Caches Available): no Kempeitai › most guerrillas › highest Population › map order; then convert. British J8: +1 Province without F136. Japanese J8: roll each, 1–2 not converted. Japanese J27: remove Opposition from the chosen Province with lowest Population.</p>
<p><span class='k'>Raid</span> (2 different destinations; 3 at Zipper 20; never at Recruit): next to a Cache source; source keeps 1 guerrilla and its majority; one colour, never into the other colour. ① Sabotage with 1 Underground ② Ambush with 1 Underground ③ Majority with the fewest (1–2, one source). Ties: destination map order › source most guerrillas › source map order › red.</p>
</div></div></div>"""
    between="""<div class='box full'><h2>Between turns</h2>
<p><span class='k'>Mobilize Population:</span> Camp Province, no Terror or Opposition: highest Population › map order. <span class='k'>Kill Traitors:</span> space with red and Police: exactly 1 Police › F136 › map order.</p>
<p><span class='k'>Forced losses</span> (J6, Clashes): Active › minority colour › blue; in J6 a Cache only if the space has no guerrilla. <span class='k'>Zipper</span> past a Cache box, none Available: remove the Cache with fewest guerrillas › most Troops › reverse map order.</p>
<p><span class='k'>Every Propaganda:</span> red short at Mobilize → map order. <span class='k'>Nonfinal:</span> each sabotaged railway (Railway-list order) → Opposition in an adjacent space without Terror/Opposition, highest Population › map order. Supply. Redeploy only <em>exposed</em> markers → Camp Province without F136/Kempeitai, most guerrillas. J25 return: Camp Province, no Kempeitai › no F136 › most guerrillas.</p>
<p><span class='k'>Events Japan plays:</span> card text; British choices use these procedures. A British capability side in play: take every optional benefit.</p>
</div>"""
    orders="""<div class='box'><h2>Orders &amp; levels</h2>
<p><span class='k'>Map order:</span> Kedah, Perak, Kelantan, Trengganu, Pahang, Selangor, Kuala Lumpur, Negri Sembilan, Johore, N. EC, S. EC.</p>
<p><span class='k'>Railway list:</span> Perak–Pahang–Selangor, N. Sembilan–Pahang, Perak–Kelantan, Thailand–Perak, Thailand–Kelantan★, N. Sembilan–Johore★, Pahang–Johore★, Thailand–Kedah★.</p>
<table><tr><th>Level</th><th>Change</th></tr>
<tr><td>Recruit</td><td>never Raids</td></tr><tr><td>Agent</td><td>standard</td></tr>
<tr><td>Veteran</td><td>Resistance starts at 4</td></tr><tr><td>Legend</td><td>starts at 4; +1 Resistance after each nonfinal Propaganda's Resistance phase (does not move the Zipper)</td></tr></table>
</div>"""
    hdr=f"<div class='hdr'><h1>Force 136 · Reference</h1><span class='tag'>v{VERSION} · British bot for Japanese Occupation</span></div>"
    win="""<div class='box full'><h2>Winning and Propaganda</h2><div class='grid'><div>
<p><span class='k'>Final Propaganda only.</span> Resistance 20, or 18–19 with fewer Jungle Camps than Force 136 markers → Force 136 wins. 18–19 otherwise → MPAJA wins (both lose). Below 18 → Japan wins.</p></div><div>
<p><span class='k'>Resistance phase:</span> + revealed Intel, + Supply Caches, + spaces with a majority; − 1 per 4 Japanese Resources, − 1 per 5 Neutral Population, − 1 per 3 spaces with Police.</p></div></div></div>"""
    hdr2=f"<div class='hdr' style='break-before:page'><h1>Force 136 · Procedures</h1><span class='tag'>v{VERSION} · reverse side</span></div>"
    return page(REF_CSS,hdr+pre+f"<div class='grid'>{turn}{orders}{goals}{win}</div>"+hdr2+f"<div class='grid'>{procs}{between}</div>",'Force 136 Reference')

def card_html(c):
    goals=[('PLACE',True)]+[(g,False) for g in c['goals']]+[('CONTACT',True)]
    lis=''
    for i,(g,fixed) in enumerate(goals,1):
        label=f"<span class='g' style='background:{GOAL_COL[g]}'>{g}</span>" if not fixed else g
        extra=' <span style="font-weight:500;font-size:7pt">if Available</span>' if g=='PLACE' else (' <span style="font-weight:500;font-size:7pt">fallback</span>' if g=='CONTACT' else '')
        lis+=f"<li class='{'fixed' if fixed else ''}'><span class='n'>{i}</span>{label}{extra}</li>"
    other='TRAIN' if c['limited_first']=='AMBUSH' else 'AMBUSH'
    lim=(f"PLACE › <span class='g' style='background:{GOAL_COL[c['limited_first']]}'>{c['limited_first']}</span> › {other} › CONTACT")
    return (f"<div class='card'><div class='inner'><div class='top'><span class='unit'>FORCE 136</span><span class='num'>DIRECTIVE {c['id']}/9</span></div>"
            f"<div class='name'>{html.escape(c['name'])}</div>"
            f"<div class='lbl'>Op &amp; Special Activity</div><ol class='goals'>{lis}</ol>"
            f"<div class='lbl'>Limited Operation</div><div class='lim'>{lim}</div>"
            f"<div class='foot'>Never take the Event. Nothing qualifies: Pass. Discard after the turn.</div></div></div>")

BACK_CSS="""
.back .inner{background:#2f3a22;align-items:center;justify-content:center;border-color:#1f2716}
.back .ring{width:1.55in;height:1.55in;border:2.5pt solid #c9b98a;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#efe9cf}
.back .big{font-family:'Bitter',serif;font-weight:700;font-size:21pt;letter-spacing:1pt}
.back .small{font-size:6.8pt;letter-spacing:2pt;text-transform:uppercase;margin-top:2pt;color:#c9b98a}
.back .tag{margin-top:12pt;font-size:6.5pt;letter-spacing:1.5pt;color:#c9b98a;text-transform:uppercase}
"""
def card_back():
    return ("<div class='card back'><div class='inner'><div class='ring'><div class='small'>Force</div><div class='big'>136</div>"
            "<div class='small'>Directive</div></div><div class='tag'>Japanese Occupation · solo</div></div></div>")
def build_cards():
    body="<div class='sheet'>"+''.join(card_html(c) for c in CARDS)+"</div>"
    body+="<div class='sheet' style='break-before:page'>"+''.join(card_back() for c in CARDS)+"</div>"
    return page(CARD_CSS+BACK_CSS,body,'Force 136 Directive cards')

DOC_CSS=BASE_CSS+"""
h1{font-size:20pt;margin-bottom:6pt;border-bottom:3px solid #2f3a22;padding-bottom:4pt}
h2{font-size:13pt;margin:12pt 0 4pt;border-bottom:1px solid #b9b49a;padding-bottom:2pt;break-after:avoid}
h3{font-size:11pt;margin:9pt 0 3pt;break-after:avoid}
p{margin:0 0 6pt} ul,ol{margin:0 0 6pt;padding-left:16pt} li{margin:0 0 2pt}
table{border-collapse:collapse;width:100%;margin:4pt 0 8pt;font-size:8.8pt;break-inside:avoid}
th,td{border:1px solid #b9b49a;padding:3pt 5pt;text-align:left;vertical-align:top}
th{background:#e9e5d3}
pre{background:#f2efe2;border:1px solid #cfc8a6;padding:6pt;font-size:7.8pt;white-space:pre-wrap}
code{font-family:'DejaVu Sans Mono',monospace;font-size:8pt}
"""
def build_doc(md_name,title,small=False):
    md=(HERE/md_name).read_text(encoding='utf-8')
    body=markdown.markdown(md,extensions=['tables','fenced_code'])
    css=DOC_CSS+("body{font-size:8.2pt;line-height:1.35} li{margin-bottom:3pt}" if small else '')
    return page(css,body,title)

def main():
    rules=chrome_pdf(build_rules(),OUT/'Force_136_v1_Rules.pdf')
    ref=chrome_pdf(build_reference(),OUT/'Force_136_v1_Reference.pdf')
    cards=chrome_pdf(build_cards(),OUT/'Force_136_v1_Cards.pdf')
    w=PdfWriter()
    for p in (rules,ref,cards):
        for pg in PdfReader(str(p)).pages:w.add_page(pg)
    with open(OUT/'Force_136_v1_Print_and_Play.pdf','wb') as f:w.write(f)
    chrome_pdf(build_doc('Force_136_v1_Sim_Report.md','Force 136 v1.0 simulation report'),OUT/'Force_136_v1_Sim_Report.pdf')
    chrome_pdf(build_doc('Force_136_v1_Sample_Game.md','Force 136 v1.0 sample game',small=True),OUT/'Force_136_v1_Sample_Game.pdf')
    for h in OUT.glob('*.html'):h.unlink()
    for p in sorted(OUT.glob('*.pdf')):print(p.name,len(PdfReader(str(p)).pages),'pages')

if __name__=='__main__':main()
