"""Immutable raw observations and position-only continuation over pinned documents."""
from dataclasses import dataclass
import hashlib
import re
from bisect import bisect_left, bisect_right
from functools import lru_cache
from .window_locator import Selector
from .window_units import WindowSelector

@dataclass(frozen=True)
class Window:
    docid: str
    digest: str
    start: int
    end: int

class RawWindowBuilder:
    search_budget=400
    open_budget=1200
    max_around_budget=2400

    def __init__(self, tokenizer):
        self.tokenizer=tokenizer
        self.selector=Selector(tokenizer)
        self.documents={}
        self.windows={}
        self.count=lru_cache(maxsize=256)(self._count)

    def _count(self,text):
        return self.selector.count(text)

    def register(self,docid,text,url):
        digest=hashlib.sha256(text.encode()).hexdigest()
        key=(docid,digest)
        if key not in self.documents:
            match=re.search(r'^title:[ \t]*([^\s\n][^\n]*)$',text,re.M) or re.search(r'^#[ \t]+([^\s\n][^\n]*)$',text,re.M)
            title=match.group(1).strip() if match else ''
            # Only source-derived title; cap metadata allocation, preserve exact source range.
            title=Selector(self.tokenizer,budget=48,overlap=0).prefix(title)
            title_span=[match.start(1),match.start(1)+len(title)] if match else None
            self.documents[key]={'text':text,'url':url,'title':title,'title_span':title_span,
                'units':WindowSelector(self.tokenizer).units(docid,text),
                'chunks':self.selector.chunks(docid,text)}
            doc=self.documents[key]
            doc['unit_starts']=sorted({c.start_char for c,_ in doc['units']})
            doc['unit_ends']=sorted({c.end_char for c,_ in doc['units']})
            doc['tables']=[]
            lines=list(re.finditer(r'[^\n]*\n|[^\n]+$',text))
            for i,line in enumerate(lines[1:],1):
                if re.fullmatch(r'[ \t]*\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-{3,}:?[ \t]*)+\|?[ \t]*\n?',line.group()):
                    header=lines[i-1]
                    if '|' not in header.group():continue
                    j=i+1
                    while j<len(lines) and '|' in lines[j].group():j+=1
                    doc['tables'].append((header.start(),line.end(),lines[j-1].end()))
        return key

    def _emit(self,key,start,end,parent=None,reason=None):
        doc=self.documents[key];text=doc['text'];raw=text[start:end]
        ref='w_'+hashlib.sha256(f'raw-v1:{key[0]}:{key[1]}:{start}:{end}'.encode()).hexdigest()[:24]
        self.windows.setdefault(ref,Window(key[0],key[1],start,end))
        return {'docid':key[0],'url':doc['url'],'title':doc['title'],
          'title_span':doc['title_span'],'document_sha256':key[1],
          'window_ref':ref,'text':raw,'offset':start,'end_char':end,
          'text_tokens':self.count(raw),'title_tokens':self.count(doc['title']),
          'has_more_before':start>0,'has_more_after':end<len(text),
          'parent_window_ref':parent,'status':reason or 'ok'}

    def _expand(self,key,start,end,budget,before=True,after=True):
        doc=self.documents[key];text=doc['text'];units=doc['units']
        # No reranking. Add adjacent structural units; preserve the existing span.
        starts=doc['unit_starts'];ends=doc['unit_ends']
        left=reversed(starts[:bisect_left(starts,start)])
        left=list(left)
        right=ends[bisect_right(ends,end):]
        li=ri=0;blocked_left=not before;blocked_right=not after
        while not(blocked_left and blocked_right):
            if not blocked_left:
                if li==len(left) or self.count(text[left[li]:end])>budget:blocked_left=True
                else:start=left[li];li+=1
            if not blocked_right:
                if ri==len(right) or self.count(text[start:right[ri]])>budget:blocked_right=True
                else:end=right[ri];ri+=1
        return start,end

    def _repair_anchor(self,key,start,end,budget):
        """Only structural range repair; retain the chosen anchor and ranking."""
        doc=self.documents[key];text=doc['text']
        starts=doc['unit_starts'];ends=doc['unit_ends']
        i=bisect_right(starts,start)-1;j=bisect_left(ends,end)
        a=starts[i] if i>=0 else start
        z=ends[j] if j<len(ends) else end
        if self.count(text[a:z])<=budget:start,end=a,z
        for header,body,table_end in doc['tables']:
            if body<=start<table_end and end<=table_end:
                if self.count(text[header:end])<=budget:start=header
                break
        return start,end

    def search(self,docid,text,url,query):
        key=self.register(docid,text,url);doc=self.documents[key]
        cap=self.search_budget-self.count(doc['title'])
        chunk,_=self.selector.select(query,doc['chunks'])
        if chunk is None:
            raw=Selector(self.tokenizer,budget=cap,overlap=0).prefix(text)
            return self._emit(key,0,len(raw),reason='prefix_fallback')
        # Locate inside the winning retrieval chunk, then expand in full document.
        local=WindowSelector(self.tokenizer,budget=cap,overlap=0)
        units=local.units(docid,chunk.text)
        anchor,_=local.select(query,[c for c,_ in units])
        if anchor is None:
            start=chunk.start_char;end=start+len(local.prefix(chunk.text))
        else:start=chunk.start_char+anchor.start_char;end=chunk.start_char+anchor.end_char
        start,end=self._repair_anchor(key,start,end,cap)
        start,end=self._expand(key,start,end,cap)
        return self._emit(key,start,end)

    def find(self,key,query):
        """Locate a query-relevant raw window inside an already registered document.

        Unlike search(), a lexical miss is explicit: it never falls back to the
        document prefix. This keeps local-location failure distinct from
        document discovery.
        """
        if key not in self.documents:
            raise ValueError('Unknown document key')
        if not isinstance(query,str) or not query.strip():
            raise ValueError('find query must be nonempty text')
        doc=self.documents[key]
        cap=self.search_budget-self.count(doc['title'])
        chunk,meta=self.selector.select(query,doc['chunks'])
        if chunk is None:
            return None,meta
        local=WindowSelector(self.tokenizer,budget=cap,overlap=0)
        units=local.units(key[0],chunk.text)
        anchor,_=local.select(query,[c for c,_ in units])
        if anchor is None:
            start=chunk.start_char;end=start+len(local.prefix(chunk.text))
        else:
            start=chunk.start_char+anchor.start_char;end=chunk.start_char+anchor.end_char
        start,end=self._repair_anchor(key,start,end,cap)
        start,end=self._expand(key,start,end,cap)
        return self._emit(key,start,end),meta

    def open(self,ref,direction):
        if ref not in self.windows:raise ValueError('Unknown window_ref; use a reference returned by search or open')
        if direction not in ('before','after','around'):raise ValueError('direction must be before, after, or around')
        old=self.windows[ref];key=(old.docid,old.digest);doc=self.documents[key];text=doc['text']
        cap=self.open_budget-self.count(doc['title'])
        if direction=='around':
            if old.start==0 and old.end==len(text):
                return self._emit(key,old.start,old.end,ref,'document_complete')
            cap=min(self.max_around_budget-self.count(doc['title']),max(cap,self.count(text[old.start:old.end])+600))
            start,end=self._expand(key,old.start,old.end,cap)
        elif direction=='after':
            if old.end==len(text):return self._emit(key,old.start,old.end,ref,'document_boundary')
            start=end=old.end;start,end=self._expand(key,start,end,cap,before=False)
            if start==end:end=start+len(Selector(self.tokenizer,budget=cap,overlap=0).prefix(text[start:]))
        else:
            if old.start==0:return self._emit(key,old.start,old.end,ref,'document_boundary')
            start=end=old.start;start,end=self._expand(key,start,end,cap,after=False)
            if start==end:
                offsets=self.tokenizer(text[:end],add_special_tokens=False,return_offsets_mapping=True)['offset_mapping']
                start=offsets[max(0,len(offsets)-cap)][0] if offsets else 0
                while start<end and self.count(text[start:end])>cap:start+=1
        reason='no_expansion_within_budget' if (start,end)==(old.start,old.end) else 'ok'
        return self._emit(key,start,end,ref,reason)
