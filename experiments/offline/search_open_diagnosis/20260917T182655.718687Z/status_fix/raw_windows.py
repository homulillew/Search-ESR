"""Immutable raw observations and position-only continuation over pinned documents."""
from dataclasses import dataclass
import hashlib
import re
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

    def count(self,text):
        return self.selector.count(text)

    def register(self,docid,text,url):
        digest=hashlib.sha256(text.encode()).hexdigest()
        key=(docid,digest)
        if key not in self.documents:
            match=re.search(r'^title:\s*(.+)$',text,re.M) or re.search(r'^#\s+(.+)$',text,re.M)
            title=match.group(1).strip() if match else ''
            # Only source-derived title; cap metadata allocation, preserve exact source range.
            title=Selector(self.tokenizer,budget=48,overlap=0).prefix(title)
            title_span=[match.start(1),match.start(1)+len(title)] if match else None
            self.documents[key]={'text':text,'url':url,'title':title,'title_span':title_span,
                'units':WindowSelector(self.tokenizer).units(docid,text),
                'chunks':self.selector.chunks(docid,text)}
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
        left=sorted({c.start_char for c,_ in units if c.start_char<start},reverse=True)
        right=sorted({c.end_char for c,_ in units if c.end_char>end})
        li=ri=0;blocked_left=not before;blocked_right=not after
        while not(blocked_left and blocked_right):
            if not blocked_left:
                if li==len(left) or self.count(text[left[li]:end])>budget:blocked_left=True
                else:start=left[li];li+=1
            if not blocked_right:
                if ri==len(right) or self.count(text[start:right[ri]])>budget:blocked_right=True
                else:end=right[ri];ri+=1
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
        start,end=self._expand(key,start,end,cap)
        return self._emit(key,start,end)

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
