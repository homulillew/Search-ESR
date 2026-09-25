# Global retrieval robustness protocol

Base: frozen U1 40-case cohort. Historical files are read-only. K0 rank depth and F1 oracle-document Find are independent diagnostics. K0 decides whether Q1 complementary queries run. F1 is run regardless of K0. After F1, F2 compares Top1 and parallel Top2 Find. A1 runs only when a document policy passes its gate. No result-driven query edits, retries, or case replacement.

The diagnostic oracle document is used only in F1. Runtime policies must use retrieved documents. New model calls are allowed only for Q1, with DeepSeek `deepseek-flash`, `max_retries=0`, one call per cell. All freezes precede the corresponding calls.

Document policy: Single Query@10 if A/B >=19/20, C/D >=18/20, overall >=37/40. Otherwise compare frozen Query1 top10 with Query1 top5 + Query2 top5 at equal candidate budget. Select dual only if A/B >=19, C/D >=18, overall >=37, net paired rescue >=2 and regressions <=1. F2 chooses Top2 only if useful hit gains >=10 percentage points and useful-W per Find-call falls <=5 percentage points. A1 uses two decisions and requires A/B >=85%, C/D >=75%, overall >=80% useful hit for its proposed gate.
