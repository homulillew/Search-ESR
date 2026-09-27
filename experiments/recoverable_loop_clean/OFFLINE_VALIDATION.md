# Offline validation

## Recorded result

2026-09-28: **76 passed, 0 failed, 0 skipped** (73 new checks + 3 existing
Orthogonal/scoped/alias tool regressions). pytest test time0.34s; full validation
runner wall time1.17s. Python3.12.2, pytest8.3.5, jsonschema4.26.0.

Artifacts: `offline_validation/run001/summary.json`, `junit.xml`, `pytest.txt`,
and12 append-only replay traces under `traces/`. Source and trace SHA256 manifests
are included. The recorded Git HEAD is the audit commit because implementation
files were uncommitted at validation; exact tested Python file hashes identify
the implementation. The subsequent implementation commit contains those bytes.

```bash
# Existing dependencies were sufficient; installation was not performed.
# If needed in another environment:
# python -m pip install -r experiments/recoverable_loop_clean/requirements-offline.txt
python -m pytest -q tests/recoverable_loop_clean tests/test_search_find_v3b.py
# Save a NEW artifact directory (refuses overwrite):
python experiments/recoverable_loop_clean/validate_offline.py /tmp/clean-loop-new-validation
```

| Layer | New tests | Scope |
|---|---:|---|
| A: real tools | 25 | all tools/directions, strict arguments/handles, exact dispatch, misses, Orthogonal repeat semantics, raw span/hash identity |
| B–F: state and loop | 30 | immutable Q/R, authority, selective/full-window claim chain, bounds, failure retention, H, NoGain, Closure and final permit |
| Historical regression | 17 | ten fixture Closure round trips, premise boundaries, q546 source opportunity, q1094 NoGain, source hashes/context |
| Proposed budget | 1 | enumerate acquisition/CONTINUE/READY branches to verify192-request ceiling |

`SearchFindTools` / `OrthogonalSearchFindTools`, their actual handle registries,
RawWindowBuilder and local window selection execute in these tests. Corpus
retrieval and tokenization are deterministic offline substitutes. New tests deny
socket connections and `Config.load`; no credential file is read. No model client
is constructed. Existing three tool tests also inject offline substitutes.

**Paid API calls0. Live BC+ rollout0. Tokens0. Cache hit rate N/A** (no requests,
not0%). No model-quality, latency or retrieval-performance estimates were made.

## Historical fixture provenance

`build_fixtures.py` selects reviewed source-relative Claims and exact observed
windows from Stage4 ancestry; `fixtures/MANIFEST.json` pins every source and output.
Stage4 D2 source spans are reused for eight fixtures. q546/q1094 use a mechanical
whole-question R1, explicitly marked as a fixture scaffold. No later Writer,
Admission, action API or runner code is imported.

| Fixture | Retained local support | Expected scripted Closure gap / mechanism |
|---|---|---|
| Euler / q538 | birth/date/place biography | book→Euler reference absent |
| Book/article / q971 | book publication and author background | later article not established |
| Memo/letter / q922 | covering memo and enclosed letter transmission | actual letter date absent |
| Patient country / q637 | clinical case, nationality, actual clinic context | do not extend to both reports’ publication location/date |
| Teammates / q1259 | member identity and team membership | other two members’ same-country binding absent |
| DLC / q843 | release/technology/government facts | European-nation qualifier unestablished |
| q637 local/global | eleven source-relative clinical facts | preserve these while checking shared identity/report conditions |
| Ding2019 / q228 | Kwon seed C; explicitly injected tentative Ding H | no selected C establishes Ding’s 2019 family condition |
| q546 | opening result and real D17/W31 prefix source | keep pending source salient; execute Find |
| q1094 | local match/free-kick facts | repeated Search NoGain signal survives query paraphrase |

These are **selected historical projections**, not complete replays of every
original message. Ding H is an explicit offline injection; it is not presented as
the natural H at that seed. We intentionally do not use the later snapshot that
already contains a Ding 2019 childlessness Claim while calling that fact unknown.

The patient window explicitly says “clinic in Pakistan”. A regression that treated
all Pakistan location evidence as absent would be invalid. The fixture preserves
this positive local context and rejects only the stronger, unsupported inference
about both reports and their publication dates/locations.

For mock tools, each archived observed window becomes a small local document;
new D/W hashes/aliases are mechanically remapped and original provenance remains
in the fixture. Original full documents and unobserved text are not fetched.
Therefore localizer behavior on these small documents is not an estimate of live
BC+ behavior. q546’s additional source is read before checkpoint seq33 only.

## What the passes establish

- Real advertised tool arguments dispatch unchanged; malformed actions are retained
  as failures without repair. All three Open directions work on nontrivial spans.
- Actor/H outputs cannot directly commit C or grant completion. Role views exclude
  prohibited authorities. OneGap and Closure feedback do not rewrite Q/R/C.
- A Claim commit needs an observed ref and a recorded supported verdict on its
  exact candidate/evidence payload; no model-authored provenance is accepted.
- Reader caps/dedup and H bounds work. A bare new handle does not count as Gain.
- Three control paths are executable with scripted responses: two NoGain → new
  route; evidence → H rejection; real Closure invocation → CONTINUE → next Actor.
- Finalizer requires a current one-use READY; failures are retained and not retried.
- Replay reconstructs state/evidence and rejects tampered hashes. Historical local
  facts remain present across a Closure veto.

## What remains unmeasured

Scripts supply the semantic decisions. They **do not** establish premise safety,
Claim relevance/truth precision, H semantic novelty, correct source routing,
False-READY rate, autonomous recovery, or answer accuracy for DeepSeek. A
structurally valid hardened OneGap can pass the action validator; a mistaken
Grounding or Closure verdict can still cause false C/READY. These are the explicit
high-risk targets of the proposed real Micro-Recovery diagnostic.
