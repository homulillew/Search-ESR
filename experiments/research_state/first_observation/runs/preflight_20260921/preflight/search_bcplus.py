"""Local BC+ adapter using official Qwen3-Embedding-8B vectors."""
from pathlib import Path
import os
import pickle
import sqlite3
import numpy as np
import faiss
import torch
from transformers import AutoModel, AutoTokenizer

BASE = Path(__file__).resolve().parents[1]
MODEL = '/data/model/Qwen3-Embedding-8B'
PREFIX = 'Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:'

class BCPlusSearcher:
    def __init__(self):
        self.index = faiss.IndexFlatIP(4096)
        self.docids = []
        for path in sorted((BASE / 'indexes/qwen3-embedding-8b').glob('*.pkl')):
            with path.open('rb') as f:
                vectors, ids = pickle.load(f)
            self.index.add(np.asarray(vectors, dtype=np.float32))
            self.docids.extend(map(str, ids))
        if self.index.ntotal != 100195:
            raise ValueError('Incomplete BC+ index')
        self.db = sqlite3.connect(f"{(BASE / 'indexes/bcplus-qwen3-8b/documents.sqlite').as_uri()}?mode=ro", uri=True)
        self.device = os.environ.get('BCPLUS_DEVICE', 'cuda:0' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, padding_side='left')
        self.model = AutoModel.from_pretrained(MODEL, local_files_only=True,
            dtype=torch.float16 if self.device.startswith('cuda') else torch.float32,
            attn_implementation='sdpa').to(self.device).eval()

    def search(self, query, k=5):
        if not isinstance(query, str) or not query.strip():
            raise ValueError('query must be nonempty text')
        if type(k) is not int or not 1 <= k <= 10:
            raise ValueError('k must be between 1 and 10')
        batch = self.tokenizer(PREFIX + query, return_tensors='pt', truncation=False)
        if batch['input_ids'].shape[1] > 8192:
            raise ValueError('query exceeds 8192 tokens')
        batch = batch.to(self.device)
        with torch.inference_mode():
            hidden = self.model(**batch).last_hidden_state[:, -1]
            vector = torch.nn.functional.normalize(hidden, p=2, dim=1).float().cpu().numpy()
        scores, positions = self.index.search(vector, k)
        results = []
        for score, pos in zip(scores[0], positions[0]):
            docid = self.docids[pos]
            row = self.db.execute('SELECT text, url FROM documents WHERE docid=?', (docid,)).fetchone()
            if row is None:
                raise RuntimeError(f'Missing indexed document {docid}')
            results.append(dict(docid=docid, score=float(score), text=row[0], url=row[1]))
        return results

    def close(self):
        self.db.close()
