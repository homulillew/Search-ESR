# State-conditioned retrieval protocol

SC0 freezes a 24-cell, 10-qid bank before any query writing or retrieval. S0–S3 keep Question and target Gap identical and add only source-supported facts visible before target evidence. Private provenance, direct sufficient-document truth, bridge truth, and censored first-seen records stay outside model inputs. Historical experiment directories are read-only.

S1 will compare the same DeepSeek query writer and unchanged Qwen3-Embedding-8B/FAISS retriever across State arms at equal top50 budget. Noise and raw-history controls must be frozen before retrieval. S2 and S3 remain conditional on S1's mechanism result. No Retriever, Find, Reader, Verify, production State schema, or Claim Admission change is allowed here.
