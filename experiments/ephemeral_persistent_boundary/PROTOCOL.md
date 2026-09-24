# Ephemeral policy / persistent state boundary

This branch tests two independent questions. S1 executes the already frozen V2
queries and their mechanically de-speculated pairs against the unchanged local
BC+ Search stack. S2 tests whether action arguments contaminate persistent
bindings, using historical observations and a query-blind verifier. S1 has no
gate over S2. Only a passing S2 permits S3 NoGain context expiry; only passing
S2 and S3 permit S4 short causal rollout. All failed cells remain in results,
all model calls use `deepseek-flash` with zero retries, and historical studies
remain append-only.

**I_EPHEMERAL_ISOLATION:** action arguments, rationale and guessed candidates
are absent from the isolated Binder and every Verifier request. They remain in
the append-only action trace. **I_EXTRACTIVE_BINDING:** treatment X mechanically
rejects a proposed persistent value unless it is a contiguous case-insensitive
span of the exact new observed W text, before semantic verification.

No Search/Find/Open hard mask, backend change, localizer change, or new
provenance compiler is introduced. Natural `condition/known/unknown` TestCards
from the previous branch remain the state representation.
