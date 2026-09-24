# Stage freeze ledger

E1 case bank, reviewer labels, rubric, request hashes, provider, prompt, arm and case order, baseline HEAD, and failure policy are frozen in `evidence_packet/freeze.json` before the first E1 model call. The source bank retains historical paths and text hashes. E2, E3, and F3b may only receive independent freezes after their preceding stage passes. A failed stage ends downstream calling and is documented as not run.
