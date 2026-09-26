# Production-shape transport canary

24/24 requests returned. Structural validity 23/24; Harness validity 23/24. One Actor produced Find+k despite nested closed branches (e3b5870f898beefd). This is 1/24 (4.17%) structural failure, 1/12 Actors (8.33%), zero Updater/Goal failures. No repair/retry/tools. Remaining 23 objects pass unchanged Harness checks; no additional control violation.

Selected `json_mode_fallback` uniformly under frozen rule. One canary does not establish a general provider failure rate. No more provider probes will run. Original semantic context is byte-identical for every historical request.

Usage: {"input": 64485, "output": 63189, "hit": 26112, "miss": 38373, "reasoning": 60914, "cache_rate": 0.40493137939055596}. All 24 report usage. Cache is token-weighted. Replay proceeds with full Uc/U1 pairing; it will test JSON-mode behavior independently, not assume zero failures.
