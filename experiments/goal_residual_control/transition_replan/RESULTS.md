# Not run — execution integrity gate

G2 yielded 75/120 valid Actor objects (62.5%), below the task’s 80% execution integrity threshold. Root cause: the harness omitted an explicit flat action-object response contract. No performance/effect threshold caused this stop. No calls, rollouts or evidence acquisition from this stage exist. Prepared runner/selection code is unexecuted and must receive a new freeze before use. See ../research_decision/INTERFACE_FAILURE.md and ../EXECUTION_GATE.json.
