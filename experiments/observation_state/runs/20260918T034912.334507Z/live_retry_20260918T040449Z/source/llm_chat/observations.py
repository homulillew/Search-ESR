"""Durable per-session raw observations. No relevance or progress judgments."""
import hashlib
import json
import sqlite3
from pathlib import Path


def merge_ranges(ranges):
    result = []
    for a, z in sorted(ranges):
        if z <= a:
            continue
        if result and a <= result[-1][1]:
            result[-1][1] = max(result[-1][1], z)
        else:
            result.append([a, z])
    return result


def subtract_ranges(start, end, covered):
    result, cursor = [], start
    for a, z in merge_ranges(covered):
        if z <= cursor:
            continue
        if a >= end:
            break
        if a > cursor:
            result.append([cursor, min(a, end)])
        cursor = max(cursor, z)
        if cursor >= end:
            break
    if cursor < end:
        result.append([cursor, end])
    return result


class ObservationStore:
    """One writer/session. Full pinned sources enable Open after process restart."""
    def __init__(self, path=':memory:'):
        if str(path) != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS documents (
            docid TEXT, digest TEXT, text TEXT NOT NULL, url TEXT NOT NULL,
            PRIMARY KEY(docid,digest));
          CREATE TABLE IF NOT EXISTS windows (
            ref TEXT PRIMARY KEY, docid TEXT, digest TEXT, start INTEGER, end INTEGER);
          CREATE TABLE IF NOT EXISTS events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, active INTEGER NOT NULL DEFAULT 1,
            tool TEXT, arguments TEXT, result TEXT, metrics TEXT);
          CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT);
        ''')
        self.coverage, self.seen = {}, set()
        self._rebuild()

    def _rebuild(self):
        self.coverage, self.seen = {}, set()
        for (raw,) in self.db.execute('SELECT metrics FROM events WHERE active=1 ORDER BY seq'):
            for v in json.loads(raw):
                key=(v['docid'],v['document_sha256'])
                self.coverage[key]=merge_ranges(self.coverage.get(key,[])+v['source_ranges'])
                self.seen.add(v['window_ref'])

    @property
    def sequence(self):
        return self.db.execute('SELECT coalesce(max(seq),0) FROM events WHERE active=1').fetchone()[0]

    def record(self, tool, arguments, result, builder):
        views = result if isinstance(result,list) else [result]
        coverage={key:[list(x) for x in value] for key,value in self.coverage.items()}
        seen=set(self.seen); metrics=[]; pins={}; windows=[]
        for v in views:
            if 'window_ref' not in v:
                continue
            did,digest=v['docid'],v['document_sha256'];key=(did,digest)
            doc=builder.documents[key];text=doc['text'];start,end=v['offset'],v['end_char']
            if not (0<=start<=end<=len(text)) or text[start:end]!=v['text']:
                raise ValueError('Observation does not match pinned source range')
            expected='w_'+hashlib.sha256(f'raw-v1:{did}:{digest}:{start}:{end}'.encode()).hexdigest()[:24]
            if expected!=v['window_ref'] or hashlib.sha256(text.encode()).hexdigest()!=digest:
                raise ValueError('Observation source/reference integrity mismatch')
            if v.get('parent_window_ref') and v['parent_window_ref'] not in seen:
                raise ValueError('Parent window was not returned in this active session')
            ranges=coverage.get(key,[]);body_new=subtract_ranges(start,end,ranges)
            ranges=merge_ranges(ranges+[[start,end]])
            title_span=v.get('title_span');title_new=[];source_ranges=[[start,end]]
            if title_span:
                a,z=title_span
                if not (0<=a<=z<=len(text)) or text[a:z]!=v['title']:
                    raise ValueError('Title does not match pinned source range')
                title_new=subtract_ranges(a,z,ranges)
                ranges=merge_ranges(ranges+[[a,z]]);source_ranges.append([a,z])
            m=dict(docid=did,document_sha256=digest,window_ref=v['window_ref'],
                   repeated_window=v['window_ref'] in seen,source_ranges=source_ranges,
                   body_new_spans=body_new,title_new_spans=title_new,
                   new_chars=sum(z-a for a,z in body_new+title_new),
                   body_overlap_chars=end-start-sum(z-a for a,z in body_new))
            metrics.append(m);coverage[key]=ranges;seen.add(v['window_ref'])
            pins[key]=(did,digest,text,doc['url']);windows.append((v['window_ref'],did,digest,start,end))
        # Validation precedes all writes; one bad view cannot partly advance state.
        with self.db:
            self.db.executemany('INSERT OR IGNORE INTO documents VALUES (?,?,?,?)',pins.values())
            self.db.executemany('INSERT OR IGNORE INTO windows VALUES (?,?,?,?,?)',windows)
            cursor=self.db.execute('INSERT INTO events(tool,arguments,result,metrics) VALUES (?,?,?,?)',
                (tool,json.dumps(arguments,ensure_ascii=False),json.dumps(result,ensure_ascii=False),json.dumps(metrics,ensure_ascii=False)))
        self.coverage,self.seen=coverage,seen
        return {'sequence':cursor.lastrowid,'observations':metrics}

    def restore_window(self, builder, ref):
        if ref not in self.seen:
            raise ValueError('Window was not returned in this active session')
        row=self.db.execute('SELECT w.docid,w.digest,w.start,w.end,d.text,d.url FROM windows w JOIN documents d ON w.docid=d.docid AND w.digest=d.digest WHERE w.ref=?',(ref,)).fetchone()
        if row is None:
            raise ValueError('Missing persisted source')
        did,digest,start,end,text,url=row
        if hashlib.sha256(text.encode()).hexdigest()!=digest:
            raise ValueError('Persisted source hash mismatch')
        key=builder.register(did,text,url)
        restored=builder._emit(key,start,end)
        if restored['window_ref']!=ref:
            raise ValueError('Restored window reference mismatch')
        return restored

    def deactivate_after(self, sequence):
        # Retain failed/cleared attempts for audit, exclude them from active coverage.
        with self.db:
            self.db.execute('UPDATE events SET active=0 WHERE seq>?',(sequence,))
        self._rebuild()

    def save_checkpoint(self, payload):
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',
                ('session',json.dumps(dict(payload,sequence=self.sequence),ensure_ascii=False)))

    def checkpoint(self):
        row=self.db.execute('SELECT value FROM metadata WHERE key=?',('session',)).fetchone()
        return json.loads(row[0]) if row else None

    def events(self, active_only=False):
        sql='SELECT seq,active,tool,arguments,result,metrics FROM events'+(' WHERE active=1' if active_only else '')+' ORDER BY seq'
        return [dict(sequence=s,active=bool(a),tool=t,arguments=json.loads(q),result=json.loads(r),observations=json.loads(m)) for s,a,t,q,r,m in self.db.execute(sql)]

    def summary(self):
        events=self.events(active_only=True);views=[v for e in events for v in e['observations']]
        return dict(events=len(events),returned_windows=len(views),distinct_windows=len(self.seen),
                    repeated_windows=sum(v['repeated_window'] for v in views),
                    source_versions=len(self.coverage),new_source_chars=sum(v['new_chars'] for v in views),
                    covered_source_chars=sum(z-a for ranges in self.coverage.values() for a,z in ranges),
                    note='Returned source ranges, not model comprehension or semantic research progress.')

    def close(self):
        self.db.close()
