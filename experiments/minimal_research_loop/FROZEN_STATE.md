# Freeze ledger

Each stage has a separate `freeze.json` created and committed before that stage calls a model. V1 has an observation/Reader freeze followed by a Finding-label/Verifier freeze. Reader responses are never resampled for verifier comparison. An unsuccessful stage preserves failures and records which downstream work did not run. This file records policy; exact hashes and orders are in each stage freeze.
