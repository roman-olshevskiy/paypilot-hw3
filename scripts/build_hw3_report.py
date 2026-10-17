"""Build a paginated review copy and explicit claim-level evidence, offline."""
import hashlib
import html
import json
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
import subprocess
from pypdf import PdfReader

ROOT = Path('D:/neoversity/paypilot-hw3')
SOURCE = Path('D:/neoversity/Lectures/Homework-03-final-report.md')
text = SOURCE.read_text(encoding='utf-8-sig')
(ROOT/'ragas-diagnostic-report.md').write_text(text, encoding='utf-8')

# Manual atomic-fact annotation. Tool-supported != retrieved-context-supported.
clean_claims = [
 ('Customer account is Tier 3', False, 'get_account.customer.tier'),
 ('Total allowance is EUR 5,000', False, 'quote_fx.allowance_total_eur'),
 ('EUR 2,500 has been used', False, 'quote_fx.allowance_used_before_eur'),
 ('EUR 2,500 remains', False, 'arithmetic from the two quote fields'),
 ('No spread while within remaining allowance', True, 'fx-guide.md#s1: If the whole conversion fits ... no spread is charged'),
 ('This sample quote was fully covered by allowance', False, 'quote_fx.allowance_applied'),
 ('Sample is EUR 100 to USD', False, 'quote_fx arguments and result'),
 ('Mid rate is 1.086957', False, 'quote_fx.mid_rate'),
 ('Gross is 108.695652 USD', False, 'quote_fx.gross_amount'),
 ('Sample spread amount is 0.00', False, 'quote_fx.spread_amount'),
 ('Final sample amount is 108.695652 USD', False, 'quote_fx.final_amount'),
 ('Full tier spread applies after allowance exhaustion', True, 'fx-guide.md#s1: Once the allowance is exhausted, the full tier spread applies'),
]
broken_claims = [
 ('Customer account is Tier 3', False, 'get_account.customer.tier'),
 ('Tier 3 FX spread is 0.5%', True, 'tariffs.md#b3: Tier 3 | 0.5% | EUR 5'),
]
raw = json.loads((ROOT/'evidence/labs/20261017T101519/captures.json').read_text())
annotation = {'method': 'Manual atomic factual claims; unique substantive claims, repeated facts counted once. Exclude offers, tool-capability descriptions and statements about missing evidence. Denominator includes customer/quote facts; numerator is support strictly in retrieved fragments, not all tool outputs.', 'runs': []}
for cid, claims in [('cause-clean', clean_claims), ('cause-broken', broken_claims)]:
    record = next(r for r in raw if r['id'] == cid)
    facts = [{'claim': c, 'supported_by_retrieval': ok, 'actual_source': s} for c,ok,s in claims]
    annotation['runs'].append({'id': cid, 'request_id': record['response']['request_id'],
        'answer': record['response']['answer'], 'claims': facts,
        'faithfulness': {'n': sum(f['supported_by_retrieval'] for f in facts), 'm': len(facts)},
        'note': 'Not supported by retrieval does not mean false: named tool facts are supported by get_account/quote_fx.'})
(ROOT/'evidence/faithfulness-annotations.json').write_text(json.dumps(annotation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
billing = {'date': '2026-10-17', 'source': 'User report in this conversation', 'amount_usd_approx': 0.21,
           'scope': 'All spending today as of the user message; not independently reconciled or allocated per API request.',
           'new_live_calls_for_report_preparation': 0}
(ROOT/'evidence/billing-observation.json').write_text(json.dumps(billing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
styles = {
 'body': ParagraphStyle('body',fontName='Arial',fontSize=9.4,leading=12,spaceAfter=5,textColor=colors.HexColor('#253244')),
 'title': ParagraphStyle('title',fontName='Arial-Bold',fontSize=16,leading=19,spaceAfter=8,textColor=colors.HexColor('#123755')),
 'heading': ParagraphStyle('heading',fontName='Arial-Bold',fontSize=10.3,leading=13,spaceBefore=6,spaceAfter=5,textColor=colors.HexColor('#123755')),
 'cell': ParagraphStyle('cell',fontName='Arial',fontSize=8.6,leading=10.5,spaceAfter=0),
 'th': ParagraphStyle('th',fontName='Arial-Bold',fontSize=8.6,leading=10.5,textColor=colors.white),
}

def inline(s):
    s = s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    s = html.escape(s)
    s = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', s)
    s = re.sub(r'`([^`]+)`', r'<font color="#123755">\1</font>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    return s

width = A4[0]-70
story=[]
lines=text.splitlines()
i=0
while i<len(lines):
    s=lines[i].strip()
    if not s:
        i+=1;continue
    if s=='<!-- pagebreak -->':
        story.append(PageBreak());i+=1;continue
    if s.startswith('# '):
        story.append(Paragraph(inline(s[2:]),styles['title']));i+=1;continue
    if s.startswith('## '):
        story.append(Paragraph(inline(s[3:]),styles['heading']));i+=1;continue
    if s.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',c) for c in row): rows.append(row)
            i+=1
        n=len(rows[0])
        if n==3: proportions=[.20,.33,.47]
        elif n==4: proportions=[.30,.24,.24,.22]
        else: proportions=[.10,.25,.25,.18,.22]
        if n==5 and rows[0][0]=='Точка': proportions=[.13,.24,.25,.16,.22]
        table=Table([[Paragraph(inline(c),styles['th'] if j==0 else styles['cell']) for c in row] for j,row in enumerate(rows)],colWidths=[width*p for p in proportions],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#123755')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf3f7'),colors.white]),
            ('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d4dee7'))]))
        story += [table,Spacer(1,6)];continue
    story.append(Paragraph(inline(s),styles['body']));i+=1

out=ROOT/'output/pdf/ragas-diagnostic-report.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
def footer(c,doc):
    c.setFont('Arial',8);c.setFillColor(colors.HexColor('#657587'))
    c.drawString(35,24,'PayPilot | HW3 | 2026-10-17 | 97dc8e0936fa')
    c.drawRightString(A4[0]-35,24,str(doc.page))
SimpleDocTemplate(str(out),pagesize=A4,leftMargin=35,rightMargin=35,topMargin=28,bottomMargin=36).build(story,onFirstPage=footer,onLaterPages=footer)
doc=PdfReader(out)
images=Path('D:/neoversity/Lectures/tmp/pdfs/hw3')
images.mkdir(parents=True,exist_ok=True)
subprocess.run(['C:/Users/olshe/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe', '-r','110','-png',str(out),str(images/'page')],check=True)
validation={'pages':len(doc.pages),'page_characters':[len(p.extract_text()) for p in doc.pages],
            'report_sha256':hashlib.sha256((ROOT/'ragas-diagnostic-report.md').read_bytes()).hexdigest(),
            'pdf_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'word_count':len(text.split()),'rendered_pages':str(images)}
(ROOT/'evidence/report-layout-check.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
print(json.dumps(validation,indent=2))
if len(doc.pages)!=2: raise RuntimeError(f'Expected 2 pages, got {len(doc.pages)}')
