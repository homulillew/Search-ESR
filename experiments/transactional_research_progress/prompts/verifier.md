Judge only whether the supplied evidence supports, refutes, or leaves open the supplied claim. Do not use outside knowledge. Do not infer missing links. Do not treat separately true clues as proof of their conjunction.

Return exactly one strict JSON object: `{ "status": "supported|refuted|open", "evidence_refs": ["W#"], "missing_evidence": "...", "reason": "..." }`. Cite only supplied exact observed refs. If conflicting supplied evidence prevents closure, return `open`. Keep the reason to one or two sentences.
