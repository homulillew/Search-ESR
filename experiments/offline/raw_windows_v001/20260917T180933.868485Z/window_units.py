"""Query-local windows over raw sentence/line units; no model or gold input."""
from dataclasses import asdict
import hashlib
import re

from .window_locator import Chunk, Selector


class WindowSelector(Selector):
    def units(self, docid, text):
        # Conservative heuristic: Markdown headings are section boundaries.
        # Tables and lists remain line units; prose is split at sentence endings.
        result = []
        section = 0
        for line in re.finditer(r'[^\n]*\n|[^\n]+$', text):
            value = line.group()
            if re.match(r'^\s*#{1,6}\s+', value):
                section += 1
            structured = bool(re.match(r'^\s*(?:\||[-*+]\s|\d+[.)]\s|#{1,6}\s)', value))
            cuts = [] if structured else [m.end() for m in re.finditer(
                r'(?<=[.!?])\s+(?=[A-Z0-9“"\u3400-\u9fff])|(?<=[。！？])', value)]
            start = 0
            for end in sorted(set(cuts + [len(value)])):
                if end <= start:
                    continue
                a, b = line.start()+start, line.start()+end
                part = text[a:b]
                if part.strip():
                    # Oversize units alone are split, explicitly marked.
                    pieces = self.chunks(docid, part) if self.count(part) > self.budget else None
                    spans = [(a+c.start_char, a+c.end_char, 'oversize_split') for c in pieces] if pieces else [(a,b,'unit')]
                    for left, right, kind in spans:
                        raw = text[left:right]
                        ident = hashlib.sha256(f'window-v1:{docid}:{left}:{right}:{raw}'.encode()).hexdigest()[:24]
                        result.append((Chunk(ident,left,right,raw,self.count(raw),kind),section))
                start = end
        return result

    def observe(self, query, text, units):
        anchor, reason = self.select(query, [u[0] for u in units])
        if anchor is None:
            value = self.prefix(text)
            return {'start_char':0,'end_char':len(value),'text':value,'tokens':self.count(value),
                    'anchor':None,'selection':reason,'stop':{'both':'prefix_fallback'}}
        index = next(i for i,u in enumerate(units) if u[0].chunk_id == anchor.chunk_id)
        lo = hi = index
        section = units[index][1]
        stops = {}
        # Alternate previous/next; keep trying the other side if one cannot fit.
        while len(stops) < 2:
            for direction in ('before','after'):
                if direction in stops:
                    continue
                candidate = lo-1 if direction == 'before' else hi+1
                if not 0 <= candidate < len(units):
                    stops[direction] = 'document_boundary'
                    continue
                if units[candidate][1] != section:
                    stops[direction] = 'section_boundary'
                    continue
                left, right = min(lo,candidate), max(hi,candidate)
                raw = text[units[left][0].start_char:units[right][0].end_char]
                if self.count(raw) > self.budget:
                    stops[direction] = 'token_budget'
                    continue
                lo, hi = left, right
        a, b = units[lo][0].start_char, units[hi][0].end_char
        raw = text[a:b]
        return {'start_char':a,'end_char':b,'text':raw,'tokens':self.count(raw),
                'anchor':asdict(anchor),'selection':reason,'stop':stops,
                'expanded_units_before':index-lo,'expanded_units_after':hi-index}
