# K0 rank depth

Run the 40 frozen Query1 strings once against the unchanged Qwen3-Embedding-8B + FAISS index at top50. Validate each new top5 against U1 GPU results. Compute sufficient-document recall at 5, 10, 20, 50 and MRR@50. Examine each of the five old misses, q435 wording sensitivity, q186 partial-match documents, and q1094 D24763. No new LLM calls.
