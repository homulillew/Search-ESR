"""Lossless question references. Units are text locations, never semantic constraints."""
import hashlib
import re

VERSION = 'question_units_v1'
ABBREVIATIONS = {'mr', 'mrs', 'ms', 'dr', 'prof', 'st', 'jr', 'sr', 'vs',
                 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept',
                 'oct', 'nov', 'dec', 'inc', 'ltd', 'approx', 'no', 'fig'}


def build_question(question):
    if not isinstance(question, str) or not question.strip():
        raise ValueError('Question must be nonempty text')
    cuts = {len(question)}
    # Hard line boundaries and conservative sentence ends. Ambiguous spans stay larger.
    cuts.update(m.end() for m in re.finditer(r'\r\n|[\r\n]', question))
    # BC+ sometimes flattens explicit lists onto one line; avoid splitting numeric ranges.
    cuts.update(m.end() for m in re.finditer(r'(?<=[.:!?])[ \t]+(?=[*\-\u2022][ \t]+[A-Z])', question))
    for match in re.finditer(r'[.!?]["\u201d\u2019\')\]]*[ \t]+(?=[A-Z0-9"\u201c])', question):
        dot = match.start()
        if question[dot] == '.':
            before = question[:dot + 1]
            word = re.search(r'([A-Za-z]+)\.$', before)
            if word and (word.group(1).lower() in ABBREVIATIONS or len(word.group(1)) == 1):
                continue
            if re.search(r'(?:[A-Za-z]\.){2,}$', before):
                continue
        cuts.add(match.end())
    units = []
    start = 0
    for end in sorted(cuts):
        text = question[start:end]
        if not text.strip():
            continue
        units.append(dict(ref=f'q{len(units) + 1}', start=start, end=end, text=text))
        start = end
    if start < len(question):
        units[-1]['end'] = len(question)
        units[-1]['text'] = question[units[-1]['start']:]
    result = dict(text=question, sha256=hashlib.sha256(question.encode('utf-8')).hexdigest(),
                  unit_version=VERSION, units=units)
    check_question(result)
    return result


def check_question(question):
    text = question['text']
    if not text.strip() or question['unit_version'] != VERSION:
        raise ValueError('Invalid question or unit version')
    if hashlib.sha256(text.encode('utf-8')).hexdigest() != question['sha256']:
        raise ValueError('Question version mismatch')
    cursor = 0
    for i, unit in enumerate(question['units'], 1):
        if (unit['ref'] != f'q{i}' or unit['start'] != cursor
                or not cursor < unit['end'] <= len(text)
                or unit['text'] != text[cursor:unit['end']]):
            raise ValueError('Question reference mapping mismatch')
        cursor = unit['end']
    if cursor != len(text):
        raise ValueError('Question references do not cover the original text')


def model_input(question):
    check_question(question)
    return dict(question=question['text'], question_units=[dict(ref=u['ref'], text=u['text'])
                for u in question['units']], requested_directions=1)
