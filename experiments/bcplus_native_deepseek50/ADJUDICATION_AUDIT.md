# Investigator adjudication audit

The investigator reviewed only the 45 cards in `MANUAL_ADJUDICATION_QUEUE.json`, each containing the question, gold answer, and model final answer. QIDs, trajectories, and experimental history were not used until decisions were locked. No Qwen3-32B or other LLM judge was called.

The deterministic comparison identified 5 correct answers. Of 45 nonempty mismatches, the investigator marked 41 correct, 4 incorrect, and 0 ambiguous. Primary score: **46/50**; ambiguous would have counted as incorrect. The queue preserves every decision. This is a single-investigator project score and is not an official BC+ judge score.

The four incorrect cards were 1, 18, 30, and 32 in queue order: two insufficient-evidence responses and two wrong entities/titles. After the decisions were locked, these mapped to qids 870, 54, 875, and 763, respectively.

Examples of accepted equivalence include a leading article or hyphen in *Micro Man*; “£500 per year” for the first principal of the Egyptian school where gold says “500 Egyptian pounds per year”; the corrected spelling “Narendra Modi Stadium” where gold has “Narender”; Zimri Eder with “Zimri Elder” explicitly given as a variant; and Union Carbide Corporation with its historical name Union Carbide and Carbon Corporation stated in the answer. These were judged from the final answers and question context, without consulting trajectories.
