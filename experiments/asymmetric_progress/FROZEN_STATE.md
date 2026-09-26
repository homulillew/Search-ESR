# Frozen state

Base remote HEAD: `094b87382668fa21e68290eed3050d5f8e5f979a`. New branch: `experiment/asymmetric-progress-closure-audit`.

Provider: existing `experiments/model_backend_deepseek/provider.json`, model `deepseek-flash`, JSON object transport, provider defaults, retry=0, 240s per HTTP operation, 4 workers. No tools. All exact inputs and semantic labels are hashed in stage freeze.json. Real run HEAD is recorded in each request event.

Bank and pairing are frozen before any new model call. Mechanical dummy canary precedes formal primary/challenge freeze. Formal plan: 144 primary + 54 challenge submissions. All outcomes retained. Primary:19 unresolved×2=38 and5 resolved×2=10 per arm.

Progress/Audit receive only original Q and exact Claim statements. No runtime Hypothesis, Workspace, source text, labels, old Light output or permanent checklist. `historical_hashes.json` protects all tracked historical experiment files; final integrity report verifies unchanged bytes.

Gate thresholds, exception-free denominators and stage stop policy are fixed in PROTOCOL.md. Replicate assignment is fixed in bank/PAIRING.json. Near-closure/resolved/conflict availability shortfalls are disclosed in DESIGN_AUDIT.md and bank/SELECTION.json.
