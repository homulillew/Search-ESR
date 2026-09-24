Read exactly one new observation in light of the current Active Gap and already committed relevant Claims. The Gap tells you what matters. Existing Claims tell you what is already stably known.

Extract 0–3 NEW factual findings only when the new observation directly supports the fact, the fact materially advances the current Gap, and the same fact is not already adequately represented by an existing Claim. Do not infer missing values from the Gap. Do not repeat existing Claims. Do not output research plans, search instructions, questions, or "still unverified" meta-statements. If the observation provides no new Gap-relevant fact, return an empty list.

Return only JSON: {"findings":[{"statement":"...","evidence_refs":["W1"]}]}.
