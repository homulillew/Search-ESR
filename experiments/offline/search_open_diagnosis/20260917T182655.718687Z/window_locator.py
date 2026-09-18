"""Offline, extractive per-document BM25 snippet selection. No gold or LLM input."""
from bisect import bisect_left, bisect_right
from collections import Counter
from dataclasses import dataclass, asdict
import hashlib
import math
import re


def terms(text):
    # Keep years/scores/names as literal terms; no web search operators or stemming.
    return re.findall(r'[a-z0-9]+|[\u3400-\u9fff]', text.casefold())


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    start_char: int
    end_char: int
    text: str
    tokens: int
    boundary: str


class Selector:
    def __init__(self, tokenizer, budget=400, overlap=50):
        if budget < 16 or not 0 <= overlap < budget // 2:
            raise ValueError('budget >= 16 and 0 <= overlap < budget/2 required')
        self.tokenizer = tokenizer
        self.budget, self.overlap = budget, overlap

    def count(self, text):
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def prefix(self, text):
        offsets = self.tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)['offset_mapping']
        end = offsets[self.budget][0] if len(offsets) > self.budget else len(text)
        while end and self.count(text[:end]) > self.budget:
            end -= 1
        return text[:end]

    def chunks(self, docid, text):
        offsets = self.tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)['offset_mapping']
        if not offsets:
            return []
        starts = [o[0] for o in offsets]
        paragraphs = [m.end() for m in re.finditer(r'\n[ \t]*\n', text)]
        lines = [m.end() for m in re.finditer(r'\n', text)]
        digest = hashlib.sha256(text.encode()).hexdigest()
        result, start = [], 0
        while start < len(text):
            i = bisect_left(starts, start)
            j = min(i + self.budget, len(offsets))
            limit = offsets[j][0] if j < len(offsets) else len(text)
            boundary = 'document_end'
            end = limit
            if limit < len(text):
                p = bisect_right(paragraphs, limit)-1
                l = bisect_right(lines, limit)-1
                # Prefer paragraph boundaries in the latter half, then complete lines.
                midpoint = offsets[min(i+self.budget//2, len(offsets)-1)][0]
                if p >= 0 and paragraphs[p] >= midpoint:
                    end, boundary = paragraphs[p], 'paragraph'
                elif l >= 0 and lines[l] > start:
                    end, boundary = lines[l], 'line'
                else:
                    boundary = 'hard_token_split'
            # Encoding a standalone slice can differ from whole-document tokenization.
            while end > start and self.count(text[start:end]) > self.budget:
                end -= 1
                boundary = 'hard_token_split'
            if end <= start:
                raise ValueError('Tokenizer failed to make progress')
            value = text[start:end]
            ident = hashlib.sha256(f'v1:{docid}:{digest}:{self.budget}:{self.overlap}:{start}:{end}'.encode()).hexdigest()[:24]
            result.append(Chunk(ident, start, end, value, self.count(value), boundary))
            if end == len(text):
                break
            # Overlap only at an existing line boundary; never start halfway through a row.
            end_i = bisect_left(starts, end)
            lower = starts[max(i+1, end_i-self.overlap)] if end_i > i+1 else end
            candidates = [x for x in lines[bisect_left(lines, lower):bisect_left(lines, end)] if x > start]
            start = candidates[0] if candidates else end
        return result

    def select(self, query, chunks):
        if not chunks:
            return None, {'fallback': 'empty_document', 'matched_terms': [], 'score': 0.0}
        frequencies = [Counter(terms(c.text)) for c in chunks]
        lengths = [sum(c.values()) for c in frequencies]
        avg = sum(lengths)/len(lengths) or 1
        df = Counter(t for f in frequencies for t in f)
        qterms = set(terms(query))
        scored = []
        for index, (freq, length) in enumerate(zip(frequencies, lengths)):
            score = 0.0
            matches = sorted(qterms & freq.keys())
            for term in matches:
                idf = math.log(1 + (len(chunks)-df[term]+0.5)/(df[term]+0.5))
                tf = freq[term]
                score += idf * tf * 2.5/(tf + 1.5*(0.25+0.75*length/avg))
            scored.append((score, -index, matches))
        score, negative_index, matches = max(scored)
        if score <= 0:
            return None, {'fallback': 'no_lexical_match_use_prefix', 'matched_terms': [], 'score': 0.0}
        return chunks[-negative_index], {'fallback': None, 'matched_terms': matches, 'score': score}
