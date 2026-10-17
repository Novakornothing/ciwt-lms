"""Course documents as a simple block model, rendered to HTML (in-app), DOCX and PDF.

Blocks: ('h1'|'h2'|'h3'|'p'|'note', text), ('ul'|'ol', [text, ...]), ('table', head, rows), ('pagebreak',).
One builder per document keeps the in-app view, the DOCX and the PDF identical in content.
"""
import io
import os

from curriculum_v2 import course_package as CP

DOCS = [
    # key, title, audience ('all' = students may see it; 'instructor' = instructors/admins only)
    ('syllabus', 'Syllabus', 'all'),
    ('pacing', 'Pacing guide (16, 8 and 10 weeks)', 'all'),
    ('rubrics', 'Rubrics', 'all'),
    ('glossary', 'Glossary', 'all'),
    ('lesson-plans', 'Instructor lesson plans', 'instructor'),
    ('lab-manual', 'Lab manual (standard format)', 'instructor'),
    ('blueprints', 'Midterm and final blueprints', 'instructor'),
    ('answer-key', 'Answer keys with rationales', 'instructor'),
]
DOC_TITLES = {k: t for k, t, _a in DOCS}
STUDENT_DOCS = {k for k, _t, a in DOCS if a == 'all'}


def _v(field):
    return field['value'] or field['placeholder']


def syllabus_doc(code, section=None, gb=None):
    s = CP.syllabus(code, section, gb)
    b = [('h1', f"{s['title']} — Syllabus")]
    b.append(('table', ['Item', 'Details'], [[f['label'], _v(f)] for f in s['fields']]))
    b += [('h2', 'Course description'), ('p', s['description']), ('h2', 'Prerequisites'), ('p', s['prerequisites'])]
    cr = s['credits']
    b += [('h2', 'Credit and contact hours'),
          ('table', ['Component', 'Credits', 'Hours over the term'],
           [['Lecture / discussion', str(cr['lecture_credits']), f"{cr['lecture_hours']} contact hours"],
            ['Lab', str(cr['lab_credits']), f"{cr['lab_hours']} contact hours"],
            ['Out-of-class work', '—', f"about {cr['out_of_class_hours']} hours"],
            ['Total', str(cr['credits']), f"{cr['contact_hours']} contact hours over {cr['weeks']} weeks + final week"]]),
          ('p', cr['basis']), ('note', cr['source']), ('p', cr['note'])]
    b += [('h2', 'Course learning outcomes'), ('p', 'By the end of the course, students will be able to:'),
          ('ol', [f"{c['code']}: {c['text']}" for c in s['clos']])]
    b += [('h2', 'Chapters and lesson objectives')]
    for ch in s['chapters']:
        b.append(('h3', ch['title']))
        b.append(('ul', [f"{o['code']} ({o['bloom']}): {o['text']}" for o in ch['objectives']] or ['See chapter overview in the LMS']))
    g = s['grading']
    b += [('h2', 'Grading'),
          ('table', ['Category', 'Weight', 'What it includes'], [[r['label'], f"{r['weight']}%", r['what']] for r in g['categories']]),
          ('p', f"Pass mark: {g['pass_mark']}%. For repeated attempts, {g['attempt_policy']}. {g['late']}"),
          ('table', ['Letter', 'Minimum %'], [[lab, str(lo)] for lo, lab in g['scale']]),
          ('ul', g['notes'])]
    b += [('h2', 'Skills exams')]
    for ex in s['skills_exams']:
        b.append(('p', f"{ex['title']} — {ex['minutes']} minutes, pass {ex['passing']}%. Stations: "
                       + '; '.join(f"{st['lab']} ({st['area']})" for st in ex['stations'])))
    b.append(('p', 'Each station is scored with the skills rubric (see Rubrics).'))
    b += [('h2', 'Schedule'), ('p', f"{s['pacing_weeks']}-week schedule. {s['pacing_note']}"),
          ('table', ['Week', 'Topics', 'Lab', 'Assessment'], [[str(r['week']), r['topics'], r['lab'], r['assessment']] for r in s['pacing']])]
    b += [('h2', 'Course policies')]
    for p in s['policies']:
        b += [('h3', p['label']), ('p', _v(p))]
    b += [('h2', 'Accessibility'), ('p', s['accessibility']['statement']), ('ul', s['accessibility']['features'])]
    b += [('note', s['disclaimer'])]
    return {'title': f"{s['title']} — Syllabus", 'blocks': b}


def pacing_doc(code, section=None, gb=None):
    title = CP.COURSES[code]['title']
    b = [('h1', f'{title} — Pacing guide')]
    for weeks, label in ((16, '16-week semester'), (8, '8-week accelerated'), (10, '10-week quarter')):
        rows = CP.pacing(code, weeks)
        b += [('h2', label), ('p', CP.PACING_NOTES.get(weeks, '')),
              ('table', ['Week', 'Topics', 'Lab', 'Assessment'], [[str(r['week']), r['topics'], r['lab'], r['assessment']] for r in rows])]
    cr = CP.credit_mapping(code)
    b += [('h2', 'Contact-hour mapping'), ('p', cr['basis']), ('note', cr['source'])]
    return {'title': f'{title} — Pacing guide', 'blocks': b}


def lesson_plans_doc(code, section=None, gb=None):
    import lessons
    pack = {'ITSUP': lessons.APLUS, 'NETOPS': lessons.NETPLUS, 'CLIENT': lessons.CLIENT}[code]
    title = CP.COURSES[code]['title']
    b = [('h1', f'{title} — Instructor lesson plans'),
         ('p', 'Each plan uses a 150-minute lecture + lab block. For 75-minute meetings, split at the break; for 50-minute '
               'meetings, run warm-up + direct instruction + check one day and guided practice + lab + exit ticket the next.'),
         ('table', ['Minutes', 'Phase', 'How'], [[str(m), p, h] for m, p, h in CP.SESSION_TEMPLATE])]
    for ch in pack:
        p = CP.lesson_plan(code, ch['order'])
        if not p:
            continue
        b += [('pagebreak',), ('h2', p['title']),
              ('p', f"About {p['minutes']} minutes of LMS content; plan {p['sessions']} block(s)."),
              ('h3', 'Objectives'), ('ul', [f"{o['code']}: {o['text']}" for o in p['objectives']]),
              ('h3', 'Lesson sequence (direct instruction)'), ('ol', p['lessons']),
              ('h3', 'Warm-up'), ('p', p['warmup']),
              ('h3', 'Guided practice'), ('p', p['guided']),
              ('h3', 'Lab'), ('ul', [f"{l['title']} ({l['id']})" for l in p['labs']] +
                              ([f"…and {p['more_labs']} more in the LMS"] if p['more_labs'] else []) +
                              [f"Classroom lab {l['id']}: {l['title']}" for l in p['classroom_labs']]),
              ('h3', 'Check for understanding'), ('p', p['check']),
              ('h3', 'Exit ticket'), ('p', p['exit_ticket']),
              ('h3', 'Discussion prompts'), ('ul', p['discussion']),
              ('h3', 'Common misconceptions'), ('ul', p['misconceptions']),
              ('h3', 'Differentiation'), ('ul', [f"Support: {p['support']}", f"Extension: {p['extension']}"]),
              ('h3', 'Materials'), ('p', p['materials'])]
    return {'title': f'{title} — Instructor lesson plans', 'blocks': b}


def _lab_blocks(f, classroom=False):
    b = [('h2', f['title']), ('p', f"Objective: {f['objective']}")]
    if f.get('scenario'):
        b.append(('p', f"Scenario: {f['scenario']}"))
    b += [('h3', 'Prerequisites'), ('ul', f['prerequisites']),
          ('h3', 'Equipment'), ('ul', [f['equipment']] + ([f"Real equipment: {f['real_equipment']}"] if f.get('real_equipment') else []) +
                                     [f"Low-cost / virtual alternative: {f['low_cost']}"]),
          ('h3', 'Steps'), ('ol', f['steps'])]
    if f.get('commands'):
        b.append(('p', 'Commands used: ' + '; '.join(f['commands'])))
    b += [('h3', 'Expected results'), ('p', f['expected']),
          ('h3', 'Troubleshooting'), ('ul', f['troubleshooting']),
          ('h3', 'Reflection questions'), ('ol', f['reflection']),
          ('p', f"Scored with: {CP.RUBRICS[f['rubric']]['title']}. Estimated time: {f['minutes']} minutes.")]
    return b


def lab_manual_doc(code, section=None, gb=None):
    import interactive_labs
    title = CP.COURSES[code]['title']
    b = [('h1', f'{title} — Lab manual')]
    by_id = {l['id']: l for l in interactive_labs.LABS}
    seen = []
    import lessons
    pack = {'ITSUP': lessons.APLUS, 'NETOPS': lessons.NETPLUS, 'CLIENT': lessons.CLIENT}[code]
    for ch in pack:
        key = ('ITSUP', ch['order'] + 7) if code == 'CLIENT' else (code, ch['order'])
        ids = [i for i in interactive_labs.CHAPTER_LABS.get(key, []) if i not in seen and i in by_id]
        cls = [cl for cl in CP.CLASSROOM_LABS.values() if (code, ch['order']) in cl['chapters'] or key in cl['chapters']]
        if not ids and not cls:
            continue
        b += [('pagebreak',), ('h1', ch['title'])]
        for i in ids:
            seen.append(i)
            b += _lab_blocks(CP.standard_lab(by_id[i]))
        for cl in cls:
            b += _lab_blocks(cl, classroom=True)
    return {'title': f'{title} — Lab manual', 'blocks': b}


def rubrics_doc(code=None, section=None, gb=None):
    b = [('h1', 'Rubrics')]
    for key, r in CP.RUBRICS.items():
        b += [('h2', r['title'], key), ('p', r['use'])]
        b.append(('table', ['Criterion'] + r['scale'], [[name] + levels for name, levels in r['criteria']]))
        if r.get('critical_errors'):
            b += [('p', 'Critical errors (station scores 0 regardless of other criteria):'), ('ul', r['critical_errors'])]
        b.append(('p', f"Maximum: {r['points']} points."))
    return {'title': 'Rubrics', 'blocks': b}


def blueprints_doc(code, section=None, gb=None):
    title = CP.COURSES[code]['title']
    b = [('h1', f'{title} — Exam blueprints')]
    for exam in ('midterm', 'final'):
        bp = CP.blueprint(code, exam)
        label = 'Midterm' if exam == 'midterm' else 'Final'
        b += [('h2', f"{label} ({bp['n_items']} items; chapters {', '.join(str(c - 7 if code == 'CLIENT' else c) for c in bp['chapters'])})"),
              ('p', bp['note']),
              ('table', ['Objective', 'Bloom', 'Items', 'Available item IDs'],
               [[f"{r['objective']}: {r['text']}", r['bloom'], 'skills exam' if r['practical'] and not r['available'] else str(r['recommended']),
                 ', '.join(r['items'])] for r in bp['rows']]),
              ('p', 'Cognitive level mix: ' + ', '.join(f'{k} {v}' for k, v in sorted(bp['bloom'].items())))]
    if code != 'CLIENT':
        b += [('h2', 'How the LMS forms are spread across chapters'),
              ('table', ['Form', 'Items'] + [f'Ch {c}' for c in sorted({c for f in CP.form_coverage(code) for c in f['by_chapter']})],
               [[f['title'], str(f['n'])] + [str(f['by_chapter'].get(c, 0)) for c in sorted({c for g in CP.form_coverage(code) for c in g['by_chapter']})]
                for f in CP.form_coverage(code)])]
    b += [('h2', 'Skills exams')]
    for ex in CP.skills_stations(code):
        b += [('h3', f"{ex['title']} ({ex['minutes']} min, pass {ex['passing']}%)"),
              ('table', ['Station', 'Area', 'Evidence the student must show'],
               [[st['lab'], st['area'], '; '.join(st['evidence'])] for st in ex['stations']])]
    return {'title': f'{title} — Exam blueprints', 'blocks': b}


def answer_key_doc(code, section=None, gb=None):
    title = CP.COURSES[code]['title']
    b = [('h1', f'{title} — Answer keys (instructor only)'),
         ('note', 'Do not share with students. Option order matches the LMS delivery order.')]
    for key in CP.answer_keys(code):
        b += [('pagebreak',), ('h2', f"{key['title']} ({key['kind']})"),
              ('table', ['#', 'Item', 'Key', 'Objective', 'Rationale'],
               [[str(r['n']), r['stem'] + '\n' + '\n'.join(r['options']), r['key'], r['objective'], r['rationale']] for r in key['rows']])]
    return {'title': f'{title} — Answer keys', 'blocks': b}


def glossary_doc(code=None, section=None, gb=None):
    return {'title': 'Glossary', 'blocks': [('h1', 'Glossary'), ('table', ['Term', 'Definition'], [[t, d] for t, d in CP.GLOSSARY])]}


BUILDERS = {'syllabus': syllabus_doc, 'pacing': pacing_doc, 'lesson-plans': lesson_plans_doc, 'lab-manual': lab_manual_doc,
            'rubrics': rubrics_doc, 'blueprints': blueprints_doc, 'answer-key': answer_key_doc, 'glossary': glossary_doc}


def build(kind, code, section=None, gb=None):
    return BUILDERS[kind](code, section, gb)


def has_placeholders(doc):
    """True when any text in the document still contains a [bracketed] placeholder."""
    def walk(x):
        if isinstance(x, str):
            return '[' in x
        if isinstance(x, (list, tuple)):
            return any(walk(i) for i in x)
        return False
    return walk(doc['blocks'])


# ------------------------------------------------------------------------------------------- DOCX
def to_docx(doc):
    from docx import Document
    from docx.shared import Pt
    d = Document()
    st = d.styles['Normal']
    st.font.name = 'Calibri'
    st.font.size = Pt(10.5)
    d.core_properties.title = doc['title']
    d.core_properties.author = 'CIWT LMS'
    for blk in doc['blocks']:
        kind = blk[0]
        if kind in ('h1', 'h2', 'h3'):
            d.add_heading(blk[1], level=int(kind[1]))
        elif kind == 'p':
            d.add_paragraph(blk[1])
        elif kind == 'note':
            para = d.add_paragraph()
            run = para.add_run(blk[1])
            run.italic = True
        elif kind in ('ul', 'ol'):
            for item in blk[1]:
                d.add_paragraph(item, style='List Bullet' if kind == 'ul' else 'List Number')
        elif kind == 'table':
            head, rows = blk[1], blk[2]
            t = d.add_table(rows=1, cols=len(head))
            t.style = 'Table Grid'
            for i, h in enumerate(head):
                cell = t.rows[0].cells[i]
                cell.text = ''
                cell.paragraphs[0].add_run(h).bold = True
            _repeat_header(t.rows[0])
            for r in rows:
                cells = t.add_row().cells
                for i, v in enumerate(r):
                    cells[i].text = str(v)
            d.add_paragraph()
        elif kind == 'pagebreak':
            d.add_page_break()
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def _repeat_header(row):
    """Mark a table row as a header row (repeats on each page; read as headers by screen readers)."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement('w:tblHeader')
    el.set(qn('w:val'), 'true')
    tr_pr.append(el)


# ------------------------------------------------------------------------------------------- PDF
_FONT = None
_ASCII = {'→': '->', '←': '<-', '−': '-', '≤': '<=', '≥': '>=', '✓': 'v', '…': '...'}


def _font():
    global _FONT
    if _FONT is None:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        cands = [('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
                 ('/Library/Fonts/Arial Unicode.ttf', '/Library/Fonts/Arial Unicode.ttf'),
                 ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf')]
        _FONT = ('Helvetica', 'Helvetica-Bold', False)
        for reg, bold in cands:
            if os.path.exists(reg) and os.path.exists(bold):
                try:
                    pdfmetrics.registerFont(TTFont('DocSans', reg))
                    pdfmetrics.registerFont(TTFont('DocSans-Bold', bold))
                    _FONT = ('DocSans', 'DocSans-Bold', True)
                except Exception:  # pragma: no cover - font file unreadable
                    continue
                break
    return _FONT


def _esc(text, unicode_ok):
    from xml.sax.saxutils import escape
    t = str(text)
    if not unicode_ok:
        for a, b in _ASCII.items():
            t = t.replace(a, b)
    return escape(t).replace('\n', '<br/>')


def to_pdf(doc):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                    TableStyle)
    reg, bold, uni = _font()
    ss = getSampleStyleSheet()
    body = ParagraphStyle('b', parent=ss['BodyText'], fontName=reg, fontSize=9.5, leading=12.5)
    cell = ParagraphStyle('c', parent=body, fontSize=8.5, leading=10.5)
    cellb = ParagraphStyle('cb', parent=cell, fontName=bold)
    note = ParagraphStyle('n', parent=body, textColor=colors.HexColor('#444444'), fontSize=8.5)
    hs = {'h1': ParagraphStyle('h1', parent=ss['Heading1'], fontName=bold, fontSize=16, spaceAfter=8),
          'h2': ParagraphStyle('h2', parent=ss['Heading2'], fontName=bold, fontSize=13, spaceBefore=10),
          'h3': ParagraphStyle('h3', parent=ss['Heading3'], fontName=bold, fontSize=10.5, spaceBefore=6)}
    width = letter[0] - 1.5 * inch
    story = []
    for blk in doc['blocks']:
        kind = blk[0]
        if kind in hs:
            story.append(Paragraph(_esc(blk[1], uni), hs[kind]))
        elif kind == 'p':
            story.append(Paragraph(_esc(blk[1], uni), body))
        elif kind == 'note':
            story.append(Paragraph('<i>' + _esc(blk[1], uni) + '</i>', note))
        elif kind in ('ul', 'ol'):
            story.append(ListFlowable([ListItem(Paragraph(_esc(i, uni), body), leftIndent=12) for i in blk[1]],
                                      bulletType='bullet' if kind == 'ul' else '1', start=None if kind == 'ul' else 1,
                                      bulletFontName=reg, bulletFontSize=8, leftIndent=14))
        elif kind == 'table':
            head, rows = blk[1], blk[2]
            data = [[Paragraph(_esc(h, uni), cellb) for h in head]] + [[Paragraph(_esc(v, uni), cell) for v in r] for r in rows]
            n = len(head)
            if n == 5:   # answer key: narrow number/key/objective columns
                widths = [0.42, 3.05, 0.5, 0.83, 2.2]
            elif n == 2:
                widths = [2.0, 5.0]
            else:
                widths = [7.0 / n] * n
            scale = width / (sum(widths) * inch)
            t = Table(data, colWidths=[w * inch * scale for w in widths], repeatRows=1)
            t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
                                   ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef5')),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            story += [t, Spacer(1, 6)]
        elif kind == 'pagebreak':
            if story:
                story.append(PageBreak())
    buf = io.BytesIO()

    def _footer(canvas, d):
        canvas.saveState()
        canvas.setFont(reg, 7.5)
        canvas.drawString(0.75 * inch, 0.5 * inch, _esc(doc['title'], uni)[:110])
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f'Page {d.page}')
        canvas.restoreState()
    SimpleDocTemplate(buf, pagesize=letter, title=doc['title'], author='CIWT LMS',
                      leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.7 * inch,
                      bottomMargin=0.75 * inch).build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
