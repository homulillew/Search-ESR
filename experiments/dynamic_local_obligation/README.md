# Dynamic Local Obligation

E1: Q+C→O (O0), with Q+C+H (O1) ablation; 27 unchanged historical states×2 arms×2 replicates=108 calls. Only an E1 PASS permits a separately frozen E2 dynamic/oracle cascade using the exact old Gap prompt. No acquisition or persistent-state changes.

Run offline prepare, tests, freeze, then commit before executing. Commands:

```bash
python -m experiments.dynamic_local_obligation.prepare prepare
python -m unittest experiments.dynamic_local_obligation.test_contracts -v
python -m experiments.dynamic_local_obligation.prepare freeze
python -m experiments.dynamic_local_obligation.run audit
python -m experiments.dynamic_local_obligation.run execute
python -m experiments.dynamic_local_obligation.run export_review
```

Never rerun execute on existing artifacts. All semantic first-pass labels must be committed before unmask/aggregate. See PROTOCOL.md for review and gates; analysis/FINAL_CONCLUSION.md records final outcome when complete.
