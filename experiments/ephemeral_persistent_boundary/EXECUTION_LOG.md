# Execution log

S1 froze at Git HEAD `129c8ad` before 71 actual Search cells. S2 froze at
Git HEAD `aad362d` before 120 Binder and 72 Verifier calls. Both used the
recorded provider/backend, `deepseek-flash` for S2, `max_retries=0`, and
retained every request, response, and error. S1 has no gate over S2. S2 failed
the paired-improvement gate, so S3 and S4 have no freeze or model calls.
