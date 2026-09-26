# Offline validation (Phase A)

- `python -m pytest -q tests/test_goal_residual_contract_v2.py`: 31 passed. Includes all required action/goal/updater contracts, dependency rejection, shared auth, and exact equivalence of all 120 old/new request objects after removal of the contract appendix.
- Earlier focused contract/auth regression invocation: 58 passed before the final two tests were added.
- Unqualified root `pytest -q` encountered 19 collection errors in archived historical test copies (duplicate module names and missing sibling imports). No historical archive was altered. The maintained full suite is run explicitly with `python -m pytest -q tests`; its completed result is recorded in the freeze preflight.
- No real API, Search, Find or Open call was made in Phase A. Mock authentication tests use an in-memory httpx transport.
