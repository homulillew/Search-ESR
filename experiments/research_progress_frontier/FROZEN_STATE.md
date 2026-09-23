# Source boundary before Stage A

`origin/experiment/research-state-projection` was fetched at `6d190e6` and this branch was created from it. Historical experiment trees remain read only. Stage A uses frozen, actually exposed search previews/windows from eight qids and no model-generated labels. `closure_probe/case_specs.py` is the pre-call reviewer annotation source; `closure_probe/build_cases.py` mechanically copies exact visible text from historical event packets. `closure_probe/freeze.json` records the commit, hashes, requests and stop rule immediately before the first new DeepSeek call.

The older histories use raw `docid` and `w_...` refs; the Orthogonal Search packets use D#/W#. These formats are retained as observed. The 29-case set includes repeated checkpoint siblings for stale-gap diagnosis; the effective number of independent evidence facts is smaller than 29, and all summaries must show qid and claim clustering.
