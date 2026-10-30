"""Build and import cmi5 course packages (cmi5.xml + zip) for Novak courses."""
import io
import json
import os
import re
import zipfile
from pathlib import Path

from lxml import etree

from .util import MOVE_ON_VALUES, NS, new_uuid

_db = None
_m = None
_deps = None
XSD_PATH = Path(__file__).resolve().parent / 'xsd' / 'CourseStructure.xsd'
_SCHEMA = None


def init(db, models, deps):
    global _db, _m, _deps
    _db, _m, _deps = db, models, deps


def M(name):
    return _m[name]


def schema():
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = etree.XMLSchema(etree.parse(str(XSD_PATH)))
    return _SCHEMA


def validate_xml(xml_bytes):
    document = etree.fromstring(xml_bytes)
    schema().assertValid(document)
    return document


def _plain(html, limit=5000):
    text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', html or '')
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:limit]


def _qn(tag):
    return f'{{{NS}}}{tag}'


def _lang(parent, tag, text):
    el = etree.SubElement(parent, _qn(tag))
    span = etree.SubElement(el, _qn('langstring'))
    span.set('lang', 'en-US')
    span.text = (text or 'Novak LMS lesson').strip() or 'Novak LMS lesson'
    return el


def _au_script():
    path = Path(__file__).resolve().parents[1] / 'static' / 'cmi5-au.js'
    return path.read_text(encoding='utf-8')


def _html_page(title, body_html, question=None):
    question_html = ''
    if question:
        options = []
        correct_index = 0
        for index, option in enumerate(question['options']):
            if option == question['correct']:
                correct_index = index
            options.append(
                f'<label class="opt"><input type="radio" name="answer" value="{index}"> {_esc(option)}</label>'
            )
        question_html = (
            f'<form id="cmi5-check" data-correct="{correct_index}">'
            f'<p><strong>Check.</strong> {_esc(question["text"])}</p>'
            + ''.join(options)
            + '<button type="button" id="cmi5-score">Submit answer</button></form>'
        )
    else:
        question_html = '<button type="button" id="cmi5-complete">Mark complete</button>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_esc(title)} — Novak LMS™</title>
<style>
  body {{ font-family: Georgia, serif; margin: 0; color: #1c1915; background: #f7f4ee; }}
  main {{ max-width: 42rem; margin: 0 auto; padding: 1.5rem 1.25rem 6rem; }}
  h1 {{ font-size: 1.6rem; line-height: 1.25; }}
  .status {{ font-family: system-ui, sans-serif; font-size: .95rem; }}
  button {{ font: inherit; margin-top: 1rem; padding: .55rem 1rem; }}
  .opt {{ display: block; margin: .35rem 0; }}
</style>
</head>
<body>
<main>
  <p class="status" id="cmi5-status">Opening this assignable unit…</p>
  <h1>{_esc(title)}</h1>
  {body_html}
  {question_html}
</main>
<script>
{_au_script()}
</script>
</body>
</html>
'''


def _esc(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def _first_question(quiz):
    if quiz is None or not quiz.questions:
        return None
    try:
        items = json.loads(quiz.questions)
    except Exception:
        return None
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        options = item.get('options') or []
        correct = item.get('correct')
        text = item.get('text') or item.get('prompt')
        if text and correct and isinstance(options, list) and correct in options and len(options) >= 2:
            return {'text': _plain(text, 500), 'options': [_plain(str(o), 240) for o in options], 'correct': _plain(str(correct), 240)}
    return None


def build_course_xml_and_files(course_code):
    """Return (xml_bytes, {path: bytes}) for one Novak course. Validates against the XSD."""
    Course = _deps['Course']
    Module = _deps['Module']
    Lesson = _deps['Lesson']
    Quiz = _deps['Quiz']
    from interactive_labs import labs_for_module

    code = (course_code or '').upper()
    course = Course.query.filter_by(code=code).first()
    if course is None:
        raise ValueError('Unknown course')
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    root = etree.Element(_qn('courseStructure'), nsmap={None: NS})
    course_el = etree.SubElement(root, _qn('course'))
    course_el.set('id', f'https://novakornothing.com/cmi5/course/{code}')
    _lang(course_el, 'title', course.title)
    description = _plain(course.description, 1200) or f'{course.title} in Novak LMS™.'
    _lang(course_el, 'description', description)

    files = {}
    blocks = 0
    for module in modules:
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        try:
            labs = labs_for_module(module)
        except Exception:
            labs = []
        if not lessons and not labs:
            continue
        blocks += 1
        block = etree.SubElement(root, _qn('block'))
        block.set('id', f'https://novakornothing.com/cmi5/course/{code}/block/{module.id}')
        _lang(block, 'title', module.title or f'Chapter {module.order}')
        _lang(block, 'description', _plain(module.content, 800) or f'Chapter {module.order} of {course.title}.')
        quiz = Quiz.query.filter_by(module_id=module.id).first()
        question = _first_question(quiz)
        for lesson in lessons:
            au_id = f'https://novakornothing.com/cmi5/course/{code}/au/lesson/{lesson.id}'
            path = f'au/lesson-{lesson.id}.html'
            _append_au(block, au_id, lesson.title, _plain(lesson.content, 400) or lesson.title,
                       path, 'CompletedAndPassed' if question else 'Completed', '0.8' if question else None,
                       'http://adlnet.gov/expapi/activities/lesson')
            article = f'<p>{_esc(_plain(lesson.content, 6000) or lesson.title)}</p>'
            files[path] = _html_page(lesson.title, article, question).encode('utf-8')
        seen_labs = set()
        for lab in labs:
            lab_id = lab.get('id')
            if not lab_id or lab_id in seen_labs:
                continue
            seen_labs.add(lab_id)
            title = lab.get('title') or lab_id
            au_id = f'https://novakornothing.com/cmi5/course/{code}/au/lab/{module.id}/{lab_id}'
            path = f'au/lab-{module.id}-{_slug(lab_id)}.html'
            blurb = lab.get('blurb') or lab.get('align') or title
            _append_au(block, au_id, title, _plain(blurb, 400) or title, path, 'Completed', None,
                       'http://adlnet.gov/expapi/activities/simulation')
            files[path] = _html_page(title, f'<p>{_esc(_plain(blurb, 2000) or title)}</p>', None).encode('utf-8')
    if blocks == 0:
        raise ValueError('This course has no chapters to export')
    xml = etree.tostring(root, xml_declaration=True, encoding='UTF-8')
    validate_xml(xml)
    files['cmi5.xml'] = xml
    return xml, files


def _slug(value):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', str(value)).strip('-') or 'lab'


def _append_au(parent, au_id, title, description, url, move_on, mastery, activity_type):
    au = etree.SubElement(parent, _qn('au'))
    au.set('id', au_id)
    au.set('moveOn', move_on if move_on in MOVE_ON_VALUES else 'NotApplicable')
    au.set('launchMethod', 'AnyWindow')
    if mastery is not None:
        au.set('masteryScore', mastery)
    if activity_type:
        au.set('activityType', activity_type)
    _lang(au, 'title', title)
    _lang(au, 'description', description or title)
    url_el = etree.SubElement(au, _qn('url'))
    url_el.text = url


def build_zip(course_code):
    xml, files = build_course_xml_and_files(course_code)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    code = course_code.lower()
    return buf.getvalue(), f'novak-lms-{code}-cmi5.zip'


def _text(el):
    if el is None:
        return ''
    parts = []
    for node in el.findall(_qn('langstring')):
        parts.append((node.get('lang') or '', (node.text or '').strip()))
    for _lang_code, text in parts:
        if _lang_code.lower().startswith('en') and text:
            return text
    return parts[0][1] if parts else ''


def _local(el):
    return etree.QName(el).localname if isinstance(el.tag, str) else ''


def import_package(filename, raw_bytes):
    """Import a cmi5.xml file or a zip whose root contains cmi5.xml. Returns the course row."""
    name = (filename or '').lower()
    files = {}
    if name.endswith('.xml') or raw_bytes.lstrip().startswith(b'<'):
        xml = raw_bytes
    else:
        try:
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
                names = [item for item in zf.namelist() if not item.endswith('/')]
                if 'cmi5.xml' not in names:
                    raise ValueError('The zip must contain cmi5.xml at its root.')
                for item in names:
                    if item.startswith('/') or '..' in item.split('/'):
                        raise ValueError('The package contains an unsafe path.')
                    files[item] = zf.read(item)
        except zipfile.BadZipFile as exc:
            raise ValueError('This file is not a valid zip package.') from exc
        xml = files['cmi5.xml']
    try:
        document = validate_xml(xml)
    except etree.DocumentInvalid as exc:
        raise ValueError('cmi5.xml does not match the cmi5 course structure schema.') from exc
    except etree.XMLSyntaxError as exc:
        raise ValueError('cmi5.xml is not well-formed XML.') from exc

    course_el = None
    blocks_and_aus = []
    for child in document:
        if _local(child) == 'course':
            course_el = child
        elif _local(child) in ('block', 'au'):
            blocks_and_aus.append(child)
    if course_el is None or not course_el.get('id'):
        raise ValueError('The course structure is missing a course id.')
    publisher_id = course_el.get('id').strip()
    title = _text(course_el.find(_qn('title'))) or 'Imported course'
    description = _text(course_el.find(_qn('description'))) or title

    is_zip = bool(files)
    _reject_duplicate_ids(document)
    parsed_blocks, parsed_aus = _walk_structure(blocks_and_aus, None, is_zip, files, [0])
    if not parsed_aus:
        raise ValueError('The course structure has no assignable units.')

    existing = M('Cmi5Course').query.filter_by(publisher_id=publisher_id, source='import').all()
    for old in existing:
        _delete_course(old)
    course = M('Cmi5Course')(
        publisher_id=publisher_id,
        lms_activity_id=_activity_iri('course'),
        title=title[:400],
        description=description,
        source='import',
    )
    _db.session.add(course)
    _db.session.flush()
    id_map = {}
    for block in parsed_blocks:
        row = M('Cmi5Block')(
            course_id=course.id,
            parent_id=None,
            publisher_id=block['publisher_id'],
            lms_activity_id=_activity_iri('block'),
            title=block['title'][:400],
            description=block['description'],
            sort_order=block['order'],
        )
        _db.session.add(row)
        _db.session.flush()
        id_map[block['key']] = row
    for block in parsed_blocks:
        parent_key = block['parent_key']
        if parent_key is not None:
            id_map[block['key']].parent_id = id_map[parent_key].id
    for au in parsed_aus:
        block_row = id_map.get(au['block_key']) if au['block_key'] is not None else None
        row = M('Cmi5AU')(
            course_id=course.id,
            block_id=block_row.id if block_row else None,
            publisher_id=au['publisher_id'],
            lms_activity_id=_activity_iri('au'),
            title=au['title'][:400],
            description=au['description'],
            url=au['url'],
            launch_method=au['launch_method'],
            move_on=au['move_on'],
            mastery_score=au['mastery_score'],
            launch_parameters=au['launch_parameters'],
            entitlement_key=au['entitlement_key'],
            activity_type=au['activity_type'],
            sort_order=au['order'],
        )
        if row.lms_activity_id == row.publisher_id:
            row.lms_activity_id = _activity_iri('au')
        _db.session.add(row)
    for path, content in files.items():
        _db.session.add(M('Cmi5File')(
            course_id=course.id, path=path, content_type=_content_type(path), content=content,
        ))
    _db.session.commit()
    return course


def _activity_iri(kind):
    return f'https://novakornothing.com/xapi/cmi5/{kind}/{new_uuid()}'


def _content_type(path):
    ext = os.path.splitext(path)[1].lower()
    return {
        '.html': 'text/html; charset=utf-8',
        '.xml': 'application/xml',
        '.css': 'text/css',
        '.js': 'text/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.gif': 'image/gif',
    }.get(ext, 'application/octet-stream')


def _delete_course(course):
    regs = M('Cmi5Registration').query.filter_by(course_id=course.id).all()
    for reg in regs:
        M('Cmi5Session').query.filter_by(registration_id=reg.id).delete()
    M('Cmi5Registration').query.filter_by(course_id=course.id).delete()
    M('Cmi5AU').query.filter_by(course_id=course.id).delete()
    M('Cmi5Block').query.filter_by(course_id=course.id).update({M('Cmi5Block').parent_id: None})
    M('Cmi5Block').query.filter_by(course_id=course.id).delete()
    M('Cmi5File').query.filter_by(course_id=course.id).delete()
    _db.session.delete(course)
    _db.session.flush()


def _reject_duplicate_ids(document):
    seen = set()
    for el in document.iter():
        ident = (el.get('id') or '').strip()
        if not ident:
            continue
        if ident in seen:
            raise ValueError('The course structure repeats an id.')
        seen.add(ident)


def _walk_structure(elements, parent_key, is_zip, files, counter):
    blocks = []
    aus = []
    for el in elements:
        counter[0] += 1
        order = counter[0]
        kind = _local(el)
        if kind == 'block':
            key = el.get('id')
            if not key:
                raise ValueError('A block is missing an id.')
            blocks.append({
                'key': key.strip(),
                'parent_key': parent_key,
                'publisher_id': key.strip(),
                'title': _text(el.find(_qn('title'))) or 'Block',
                'description': _text(el.find(_qn('description'))) or 'Block',
                'order': order,
            })
            nested = [child for child in el if _local(child) in ('block', 'au')]
            child_blocks, child_aus = _walk_structure(nested, key.strip(), is_zip, files, counter)
            blocks.extend(child_blocks)
            aus.extend(child_aus)
        elif kind == 'au':
            aus.append(_parse_au(el, parent_key, order, is_zip, files))
    return blocks, aus


def _parse_au(el, block_key, order, is_zip, files):
    publisher_id = (el.get('id') or '').strip()
    if not publisher_id:
        raise ValueError('An assignable unit is missing an id.')
    url = (el.findtext(_qn('url')) or '').strip()
    if not url or any(ch.isspace() for ch in url):
        raise ValueError(f'{publisher_id} has an invalid url.')
    absolute = url.startswith('http://') or url.startswith('https://') or '://' in url.split('/')[0]
    if is_zip and not absolute:
        rel = url.split('?', 1)[0].split('#', 1)[0]
        if rel not in files:
            raise ValueError(f'{url} is not in the zip package.')
    if not is_zip and not absolute:
        raise ValueError('A standalone cmi5.xml must use fully qualified assignable-unit URLs.')
    move_on = el.get('moveOn') or 'NotApplicable'
    if move_on not in MOVE_ON_VALUES:
        raise ValueError(f'Unsupported moveOn value: {move_on}')
    launch_method = el.get('launchMethod') or 'AnyWindow'
    if launch_method not in ('AnyWindow', 'OwnWindow'):
        raise ValueError(f'Unsupported launchMethod: {launch_method}')
    mastery = el.get('masteryScore')
    if mastery is not None:
        try:
            number = float(mastery)
        except ValueError as exc:
            raise ValueError('masteryScore must be a decimal between 0 and 1.') from exc
        if number < 0 or number > 1:
            raise ValueError('masteryScore must be between 0 and 1.')
        mastery = mastery.strip()
    params = el.findtext(_qn('launchParameters'))
    entitlement = el.findtext(_qn('entitlementKey'))
    return {
        'block_key': block_key,
        'publisher_id': publisher_id,
        'title': _text(el.find(_qn('title'))) or 'Assignable unit',
        'description': _text(el.find(_qn('description'))) or 'Assignable unit',
        'url': url,
        'launch_method': launch_method,
        'move_on': move_on,
        'mastery_score': mastery,
        'launch_parameters': (params or '').strip() or None,
        'entitlement_key': (entitlement or '').strip() or None,
        'activity_type': (el.get('activityType') or '').strip() or None,
        'order': order,
    }


def ensure_live_course(course_code, host_url):
    """A launchable structure whose assignable units are the live lesson player."""
    Course = _deps['Course']
    Module = _deps['Module']
    Lesson = _deps['Lesson']
    ClassSection = _deps['ClassSection']
    code = course_code.upper()
    course = Course.query.filter_by(code=code).first()
    if course is None:
        raise ValueError('Unknown course')
    publisher = f'https://novakornothing.com/cmi5/course/{code}/live'
    row = M('Cmi5Course').query.filter_by(publisher_id=publisher).first()
    if row:
        return row
    section = ClassSection.query.filter_by(course_id=course.id).order_by(ClassSection.id).first()
    if section is None:
        raise ValueError('This course has no class to launch from.')
    row = M('Cmi5Course')(
        publisher_id=publisher,
        lms_activity_id=_activity_iri('course'),
        title=course.title,
        description=_plain(course.description, 500) or course.title,
        source='novak',
        novak_code=code,
    )
    _db.session.add(row)
    _db.session.flush()
    order = 0
    for module in Module.query.filter_by(course_id=course.id).order_by(Module.order).all():
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        if not lessons:
            continue
        block = M('Cmi5Block')(
            course_id=row.id, publisher_id=f'{publisher}/block/{module.id}',
            lms_activity_id=_activity_iri('block'), title=module.title or f'Chapter {module.order}',
            description=_plain(module.content, 400) or module.title, sort_order=module.order,
        )
        _db.session.add(block)
        _db.session.flush()
        for lesson in lessons:
            order += 1
            url = f'/student/module/{section.id}/{module.id}/lesson/{lesson.id}'
            _db.session.add(M('Cmi5AU')(
                course_id=row.id, block_id=block.id,
                publisher_id=f'{publisher}/au/lesson/{lesson.id}',
                lms_activity_id=_activity_iri('au'),
                title=lesson.title, description=lesson.title, url=url,
                launch_method='AnyWindow', move_on='CompletedAndPassed', mastery_score='0.8',
                activity_type='http://adlnet.gov/expapi/activities/lesson', sort_order=order,
            ))
    _db.session.commit()
    return row
