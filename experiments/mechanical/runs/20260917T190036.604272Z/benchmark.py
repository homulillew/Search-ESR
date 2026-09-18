"""Isolated before/after structural and latency checks; no API or reranking."""
import importlib.util,json,sys,time,sqlite3,shutil,hashlib,gc,tracemalloc,statistics
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder


def main():
    dest=ROOT/'experiments/mechanical/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    shutil.copy2(ROOT/'experiments/mechanical/baseline_raw_windows.txt',dest/'baseline.py')
    spec=importlib.util.spec_from_file_location('llm_chat._mechanical_baseline',dest/'baseline.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    cases=[('67431','Peter King role in The Constant Gardener'),('23800','2005 Champions League final Riise free kick'),('55516','Mark Selby 2023 results'),('54231','Shaun Deeb grandmother poker')]
    rows=[]
    # Alternate arm order across documents to reduce warm-up bias.
    for i,(did,q) in enumerate(cases):
        text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
        for name,cls in ([('old',module.RawWindowBuilder),('new',RawWindowBuilder)] if i%2==0 else [('new',RawWindowBuilder),('old',module.RawWindowBuilder)]):
            gc.collect();b=cls(tok);t=time.perf_counter();v=b.search(did,text,url,q);cold=time.perf_counter()-t
            warm=[];reads=[]
            for _ in range(5):
                t=time.perf_counter();again=b.search(did,text,url,q);warm.append(time.perf_counter()-t);assert again['text']==v['text']
                t=time.perf_counter();opened=b.open(v['window_ref'],'around');reads.append(time.perf_counter()-t)
                assert v['text'] in opened['text'];assert opened['text']==text[opened['offset']:opened['end_char']]
            assert v['text_tokens']+v['title_tokens']<=400
            # Estimate Python-owned payload, including cached objects. Excludes tokenizer/native allocations.
            visited=set()
            def size(obj):
                if id(obj) in visited:return 0
                visited.add(id(obj));n=sys.getsizeof(obj)
                if isinstance(obj,dict):n+=sum(size(k)+size(v) for k,v in obj.items())
                elif isinstance(obj,(list,tuple,set)):n+=sum(size(x) for x in obj)
                elif hasattr(obj,'__dict__'):n+=size(obj.__dict__)
                return n
            owned=size(b.documents)+size(b.windows)
            row={'docid':did,'chars':len(text),'query':q,'arm':name,'cold_search_seconds':cold,'warm_search_median_seconds':statistics.median(warm),'around_median_seconds':statistics.median(reads),'document_registry_python_bytes':owned,'memory_note':'Approximate documents/windows graph only; excludes tokenizer, native RSS and count-cache closure.','count_cache':str(b.count.cache_info()) if hasattr(b.count,'cache_info') else None,'search':v,'around':opened}
            rows.append(row);print(did,name,round(cold,3),round(statistics.median(warm),4),round(statistics.median(reads),4),flush=True)
            del b;gc.collect()
    (dest/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    manifest={'scope':'Four fixed real documents, five repeated search/around operations each. Single process, alternating order; not a statistically controlled load test. Tokenizer load excluded. No API or new document retrieval.','source_hashes':{}}
    for rel in ['llm_chat/raw_windows.py','llm_chat/window_units.py','llm_chat/window_locator.py','experiments/mechanical/benchmark.py']:
        src=ROOT/rel;shutil.copy2(src,dest/src.name);manifest['source_hashes'][rel]=hashlib.sha256(src.read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2));print(dest,flush=True)
    db.close()
if __name__=='__main__':main()
