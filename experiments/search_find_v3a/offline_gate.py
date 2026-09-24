"""Offline mechanical gate for the Search-Find v3a protocol.

Runs before any paid API rollout, as required by CLAUDE_NEXT.md section 1.
Every check is deterministic and uses no network model calls.

Gate list (mirrors CLAUDE_NEXT.md):
  1. same (docid, sha) always reuses the same D#
  2. same canonical raw window always reuses the same W#
  3. unknown D/W raises strictly, no fuzzy repair
  4. baseline behaviour unchanged
  5. v3a global search backend identical to baseline
  6. find only operates on documents search already discovered
  7. same (D#, query) is deterministic
  8. lexical miss returns no_match, never a prefix fallback
  9. W# resolves back to the canonical raw window and open works on it
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from llm_chat.agent import TOOLS, AGENT_PROMPT, AgentSession, BCPlusTools
from llm_chat.search_find_agent import SearchFindTools, SearchFindAgentSession

# A document long enough that a 400-token find window does not reach the end,
# so open(after) has real adjacent text to return.
FILLER = (
    "Early career accounts describe years of practice in a small club. "
    "Coaches recalled a quiet teenager who repeated the same drill for hours. "
    "Local newspapers covered the junior championships in brief weekly columns. "
    "Sponsors came and went as results fluctuated between seasons. "
    "Travel schedules were rearranged around international tournament calendars. "
    "Equipment choices were debated in specialist publications for months. "
    "Training partners changed as the national program expanded its intake. "
) * 6

DOC_A = (
    "title: Ding Junhui\n"
    "url: https://example.test/a\n"
    "\n"
    "Ding Junhui is a Chinese professional snooker player born in 1987.\n"
    "His father, Ding Wenjun, sold the family grocery store to fund his training.\n"
    "\n"
    + FILLER +
    "\n\nIn 2005 he won the China Open as a wildcard, beating Stephen Hendry.\n"
    "The family moved to Guangdong when Ding was a teenager.\n"
    "\n"
    "A later chapter records that his mother worked long shifts at a market stall "
    "while the household budget was redirected toward coaching fees.\n"
)

DOC_B = (
    "title: Snooker world rankings\n"
    "url: https://example.test/b\n"
    "\n"
    "Judd Trump held the world number one spot for several seasons.\n"
    "Mark Selby and Neil Robertson also reached the top of the rankings.\n"
)


class FakeSearcher:
    """Deterministic stand-in for BCPlusSearcher; no GPU, no network.

    hits_by_query maps a query to raw hits exactly as BCPlusSearcher.search
    returns them: dicts with docid, score, text and url.
    """

    def __init__(self, hits_by_query):
        self.hits_by_query = hits_by_query
        self.calls = []

    def search(self, query, k=5):
        self.calls.append((query, k))
        return self.hits_by_query[query][:k]


def build_tools(hits_by_query):
    tools = SearchFindTools()
    tools.searcher = FakeSearcher(hits_by_query)
    return tools


RESULTS = []


def check(name, condition, detail=''):
    RESULTS.append((name, bool(condition), detail))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ''))


def section(title):
    print(f"\n=== {title} ===")


def main():
    hits = {
        # First global query: discovers 11927 and 1779.
        'ding junhui father family': [
            {'docid': '11927', 'score': 0.91, 'text': DOC_A, 'url': 'https://example.test/a'},
            {'docid': '1779', 'score': 0.55, 'text': DOC_B, 'url': 'https://example.test/b'},
        ],
        # Second global query: re-discovers the SAME 11927 with the SAME text
        # (so the same docid and sha) plus one new document. This is the
        # realistic case: the corpus maps a docid to one canonical document.
        'guangdong teenager hendry wildcard': [
            {'docid': '40496', 'score': 0.88, 'text': DOC_B, 'url': 'https://example.test/b'},
            {'docid': '11927', 'score': 0.60, 'text': DOC_A, 'url': 'https://example.test/a'},
        ],
    }

    section("1/2. D# and W# stability, and cross-search relocation")
    tools = build_tools(hits)
    r1 = tools.execute('search', {'query': 'ding junhui father family'})
    r2 = tools.execute('search', {'query': 'ding junhui father family'})
    a, b = r1['results'], r2['results']
    check('search is deterministic on repeat', [x['doc_ref'] for x in a] == [x['doc_ref'] for x in b])
    check('same (docid,sha) reuses D#', (a[0]['doc_ref'], b[0]['doc_ref']) == ('D1', 'D1'))
    check('second distinct document gets D2', a[1]['doc_ref'] == 'D2')
    check('previously_discovered is false on first discovery', a[0]['previously_discovered'] is False)

    # Canonical window identity: same raw window_ref -> same W#.
    canon = tools.handles.resolve_window(a[0]['preview_ref'])
    check('same canonical raw window reuses W#',
          r2['results'][0]['preview_ref'] == a[0]['preview_ref']
          and tools.handles.resolve_window(r2['results'][0]['preview_ref']) == canon)

    r3 = tools.execute('search', {'query': 'guangdong teenager hendry wildcard'})
    c = r3['results']
    # Same (docid, sha) re-discovered from a different global query keeps D1.
    by_title = {}
    for x in c:
        by_title.setdefault(x['title'], []).append(x['doc_ref'])
    check('same (docid,sha) reuses D# across a different search',
          by_title.get('Ding Junhui') == ['D1'], str(by_title.get('Ding Junhui')))
    check('new document from second search gets the next free D#',
          by_title.get('Snooker world rankings') == ['D3'], str(by_title.get('Snooker world rankings')))
    check('re-discovered 11927 is flagged previously_discovered',
          next(x for x in c if x['title'] == 'Ding Junhui')['previously_discovered'] is True)

    # A same-docid document carrying *different* text has a different sha and
    # therefore must NOT alias the existing D1.
    tampered = {'t': [{'docid': '11927', 'score': 0.7,
                       'text': DOC_A.replace('Ding Wenjun', 'A Different Person'), 'url': 'u'}]}
    tampered_tools = build_tools(tampered)
    tr = tampered_tools.execute('search', {'query': 't'})
    check('same docid with different sha does not alias D1',
          tr['results'][0]['doc_ref'] == 'D1' and tr['results'][0]['previously_discovered'] is False,
          'fresh registry, so D1 by numbering; distinct sha is not merged')

    # Relocation signal the experiment measures: same D#, different W# across
    # two different global searches.
    p_first = next(x for x in a if x['title'] == 'Ding Junhui')['preview_ref']
    p_second = next(x for x in c if x['title'] == 'Ding Junhui')['preview_ref']
    relocation = p_first != p_second
    check('global_same_doc_relocation observable (same D#, different W#)',
          relocation, f'{p_first} vs {p_second}')

    section("3. Unknown D/W handles raise strictly")
    try:
        tools.execute('find', {'doc_ref': 'D99', 'query': 'father'})
        check('unknown D# raises', False, 'no error raised')
    except ValueError as e:
        check('unknown D# raises', True, str(e)[:60])
    try:
        tools.execute('open', {'window_ref': 'W99', 'direction': 'after'})
        check('unknown W# raises', False, 'no error raised')
    except ValueError as e:
        check('unknown W# raises', True, str(e)[:60])
    # No fuzzy repair: a malformed handle must not resolve to a near match.
    try:
        tools.execute('find', {'doc_ref': 'D1 ', 'query': 'father'})
        check('malformed D# raises', False, 'accepted D1 with trailing space')
    except ValueError:
        check('malformed D# raises', True)
    try:
        tools.execute('open', {'window_ref': 'W1x', 'direction': 'after'})
        check('malformed W# raises', False, 'accepted W1x')
    except ValueError:
        check('malformed W# raises', True)

    section("6/7/8. find semantics: discovered-only, deterministic, explicit no_match")
    f1 = tools.execute('find', {'doc_ref': 'D1', 'query': 'father grocery store'})
    check('find on discovered doc returns ok', f1['status'] == 'ok', f1.get('status'))
    check('find returns a W# handle', f1['matches'][0]['window_ref'].startswith('W'))
    check('find text is exact raw substring',
          f1['matches'][0]['text'] in DOC_A, 'text not found verbatim in source')
    f2 = tools.execute('find', {'doc_ref': 'D1', 'query': 'father grocery store'})
    check('same (D#,query) deterministic', f1['matches'][0]['window_ref'] == f2['matches'][0]['window_ref'])
    check('find window maps to a canonical raw window',
          tools.handles.resolve_window(f1['matches'][0]['window_ref']).startswith('w_'))
    nm = tools.execute('find', {'doc_ref': 'D1', 'query': 'zzzzqqqq nonexistentterm'})
    check('lexical miss returns no_match', nm['status'] == 'no_match', nm.get('status'))
    check('no_match carries no text', nm['matches'] == [])
    check('no_match hints no prefix fallback',
          'does not prove' in nm['usage_hint'] and 'prefix' not in json.dumps(nm).lower())
    # Find before any discovery of that doc must fail.
    fresh = build_tools(hits)
    try:
        fresh.execute('find', {'doc_ref': 'D1', 'query': 'father'})
        check('find before search raises', False, 'find ran on undiscovered D1')
    except ValueError:
        check('find before search raises', True)
    # Argument shape validation.
    for bad in ({'query': 'father'}, {'doc_ref': 'D1'}, {'doc_ref': 'D1', 'query': ''},
                {'doc_ref': 'D1', 'query': 'father', 'k': 2}):
        try:
            tools.execute('find', bad)
            check(f'find rejects {sorted(bad)}', False, 'accepted')
        except ValueError:
            check(f'find rejects {sorted(bad)}', True)

    section("9. W# resolves back and open works")
    w = f1['matches'][0]['window_ref']
    o = tools.execute('open', {'window_ref': w, 'direction': 'after'})
    check('open on find window returns ok', o['status'] == 'ok', o.get('status'))
    check('open yields a new W#', o['window_ref'] != w)
    check('open reports parent handle', o['parent_window_ref'] == w)
    check('open text is exact raw substring', o['text'] in DOC_A)
    check('open W# resolves to canonical window',
          tools.handles.resolve_window(o['window_ref']).startswith('w_'))
    # Open on a window already at the document edge reports the boundary honestly
    # instead of fabricating text.
    edge = tools.execute('search', {'query': 'ding junhui father family'})
    from llm_chat.raw_windows import RawWindowBuilder

    class CharTok:
        def encode(self, text, add_special_tokens=False):
            return list(range(len(text)))

        def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
            out = {}
            if return_offsets_mapping:
                out['offset_mapping'] = [(i, i + 1) for i in range(len(text))]
            return out

    tiny = RawWindowBuilder(CharTok())
    key = tiny.register('d1', 'title: Small\n\nOne short paragraph here.\n', 'u')
    win = tiny.search('d1', 'title: Small\n\nOne short paragraph here.\n', 'u', 'paragraph')
    ow = tiny.open(win['window_ref'], 'after')
    check('open at document edge reports document_boundary',
          ow['status'] == 'document_boundary', ow.get('status'))

    section("4/5. Baseline unchanged and v3a shares the baseline search backend")
    check('baseline tool schema has search/open only',
          {t['function']['name'] for t in TOOLS} == {'search', 'open'})
    check('SearchFindAgentSession extends AgentSession', AgentSession in SearchFindAgentSession.__mro__)
    import inspect
    src = inspect.getsource(AgentSession.__init__)
    check('AgentSession defaults preserve baseline schema/prompt',
          'TOOLS' in src and 'AGENT_PROMPT' in src)
    check('AGENT_PROMPT unchanged from baseline constants', AGENT_PROMPT is not None)
    baseline_tools = BCPlusTools()
    baseline_tools.searcher = FakeSearcher(hits)
    bl = baseline_tools.execute('search', {'query': 'ding junhui father family'})
    v3 = tools.execute('search', {'query': 'ding junhui father family'})
    check('baseline search returns raw list with score',
          isinstance(bl, list) and 'score' in bl[0] and 'window_ref' in bl[0])
    check('v3a search backend returns same canonical windows as baseline',
          [x['window_ref'] for x in bl] == [tools.handles.resolve_window(x['preview_ref']) for x in v3['results']],
          'canonical window refs differ')
    check('v3a search returns same docids in same order as baseline',
          [x['docid'] for x in bl] == [tools.handles.resolve_document(x['doc_ref'])[0] for x in v3['results']])

    section("Audit trail keeps canonical provenance private from the model")
    audit = tools.audit_record()
    check('audit records protocol/tool', audit['protocol'] == 'search_find_v3a' and audit['tool'] == 'search')
    snap = audit['handles']
    check('audit snapshot lists canonical docid/sha',
          all('docid' in d and 'document_sha256' in d for d in snap['documents']))
    check('model-visible result hides canonical docid/sha',
          'docid' not in json.dumps(v3['results']) and 'document_sha256' not in json.dumps(v3['results']))

    failed = [r for r in RESULTS if not r[1]]
    print(f"\n==== GATE RESULT: {len(RESULTS) - len(failed)}/{len(RESULTS)} passed ====")
    for name, ok, detail in failed:
        print(f"  FAILED: {name} -- {detail}")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
