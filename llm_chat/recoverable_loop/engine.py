"""Narrow role orchestration. No hidden state patches, retries or action repair."""
from copy import deepcopy
from dataclasses import asdict, replace
import json
import hashlib
import re
from pathlib import Path
from .contracts import check, parse_json, validate_decision
from .state import (Claim, Hypothesis, append_event, actor_view, fact_view, trace_view,
                    digest, canonical, family, next_id)
from .roles import request, SemanticPort
from .tools import ToolBridge
from .integrity import IntegrityError, observed_evidence, validate_integrity


def normalized_statement(text): return ' '.join(text.casefold().split())


class HypothesisFailure(ValueError):
    """Only a rejected H proposal or an exception from its semantic port."""
    def __init__(self, error_type, message):
        super().__init__(message)
        self.error_type = error_type


class RecoverableLoop:
    def __init__(self, state, bridge: ToolBridge, semantics: SemanticPort, log_path=None):
        self._state, self.bridge, self.semantics = state, bridge, semantics
        self._ready = None; self._attempt = max((e.payload().get('attempt_id', 0) for e in state.T), default=0); self._log = None
        for c in state.C: bridge.evidence.select(c.evidence_refs)
        for h in state.H: bridge.evidence.select(h.basis_refs)
        self._initial_state = state
        self._initial_evidence = observed_evidence(bridge)
        self._assert_integrity()
        if log_path is not None:
            self._log = Path(log_path).open('x', encoding='utf-8')
            observed = [w['window_ref'] for w in bridge.tools.handles.snapshot()['windows']]
            self._log.write(canonical({'kind': 'initial_state', 'state': asdict(state),
                                      'evidence': bridge.evidence.select(observed)}) + '\n')
            self._log.flush()

    @property
    def state(self): return self._state

    def close(self):
        if self._log is not None: self._log.close(); self._log = None

    def _assert_integrity(self):
        validate_integrity(self._initial_state, self._initial_evidence, self._state, self.bridge)

    def _emit(self, kind, **payload):
        self._state = append_event(self._state, kind, payload)
        if self._log is not None:
            self._log.write(canonical(asdict(self._state.T[-1])) + '\n'); self._log.flush()

    def _call(self, role, payload):
        req = request(role, payload)
        self._emit('role_request', attempt_id=self._attempt, role=role, request_hash=req.request_hash,
                   prompt=req.prompt, input=json.loads(req.input_json), schema=json.loads(req.schema_json))
        try:
            raw = self.semantics.complete(req)
        except Exception as exc:
            self._emit('role_failure', attempt_id=self._attempt, role=role, error_type=type(exc).__name__, message=str(exc))
            if role == 'hypotheses' and not isinstance(exc, IntegrityError):
                raise HypothesisFailure('provider_failure', f'{type(exc).__name__}: {exc}') from exc
            raise
        # Archive before parsing/validation. No corrected response replaces raw.
        self._emit('role_response', attempt_id=self._attempt, role=role, output=raw)
        try:
            value = parse_json(raw) if isinstance(raw, str) else deepcopy(raw)
            # Specific diagnostic without coercing or mapping any references.
            if role == 'hypotheses' and isinstance(value, dict):
                updates = value.get('updates')
                if isinstance(updates, list):
                    for update in updates:
                        basis = update.get('basis_refs') if isinstance(update, dict) else None
                        if isinstance(basis, list) and any(isinstance(r, str) and not re.fullmatch(r'W[1-9][0-9]*', r) for r in basis):
                            raise HypothesisFailure('invalid_basis_ref_namespace', 'basis_refs accepts observed W# only')
            check(value, json.loads(req.schema_json))
        except HypothesisFailure:
            raise
        except (ValueError, TypeError) as exc:
            if role == 'hypotheses': raise HypothesisFailure('invalid_schema', str(exc)) from exc
            raise
        return value

    def _evidence_for_claims(self):
        return self.bridge.evidence.select([ref for c in self._state.C for ref in c.evidence_refs])

    def _fact_snapshot(self):
        return {**fact_view(self._state), 'Evidence': self._evidence_for_claims()}

    def _claim_chain(self, one_gap, windows):
        if not windows: return
        refs = {w.window_ref for w in windows}
        response = self._call('reader', {'OneGap': one_gap, 'C': [asdict(c) for c in self._state.C],
                                          'Observation': [asdict(w) for w in windows]})
        for candidate in response['findings']:
            if not candidate['statement'].strip() or not set(candidate['evidence_refs']) <= refs:
                raise ValueError('candidate must cite actual current observations')
        for candidate in response['findings']:
            if normalized_statement(candidate['statement']) in {normalized_statement(c.statement) for c in self._state.C}:
                self._emit('candidate_duplicate', candidate=candidate); continue
            evidence = self.bridge.evidence.select(candidate['evidence_refs'])
            # No Gap, Q, R, H, Trace or prior C can serve as grounding evidence.
            payload = {'candidate': candidate, 'Evidence': evidence}
            verdict = self._call('grounding', payload)
            self._emit('grounding_decision', payload_hash=digest(payload), candidate=candidate, verdict=verdict)
            if verdict['verdict'] != 'supported': continue
            c = Claim(next_id(self._state.C, 'claim_id', 'C'), candidate['statement'], tuple(candidate['evidence_refs']))
            self._state = replace(self._state, C=self._state.C+(c,)); self._ready = None
            self._emit('claim_committed', claim=asdict(c), evidence_hash=digest(evidence), grounding_payload_hash=digest(payload))

    def _propose_hypotheses(self, batch, new_claims):
        before = self._state.H
        inspected = set(batch['inspected_sources'])
        for event in self._state.T:
            if event.kind == 'step_outcome': inspected.update(event.payload().get('inspected_sources', []))
        eligible = sorted(set(batch['new_document_refs']) - inspected)
        proposal = self._call('hypotheses', {
            'Q': self._state.Q, 'R': [asdict(r) for r in self._state.R], 'H': [asdict(h) for h in before],
            'Observation': [asdict(w) for w in batch['windows']], 'new_Claims': [asdict(c) for c in new_claims],
            'eligible_source_refs': eligible,
            'Trace_outcome': {'recent': trace_view(self._state), 'tool_status': batch['result'].get('status'),
                              'new_document_refs': batch['new_document_refs'], 'inspected_sources': batch['inspected_sources']}})
        hs = list(before); touched = set()
        for update in proposal['updates']:
            op = update['operation']
            basis = tuple(update.get('basis_refs', []))
            if any(r not in self.bridge.evidence._windows for r in basis):
                raise HypothesisFailure('unknown_basis_ref', 'basis must reference observed W#')
            if op == 'ADD':
                if not update['statement'].strip(): raise HypothesisFailure('empty_hypothesis', 'empty H')
                if normalized_statement(update['statement']) in {normalized_statement(h.statement) for h in hs}: continue
                hs.append(Hypothesis(next_id(hs, 'hypothesis_id', 'H'), update['statement'], 'active', basis))
            else:
                hid = update['hypothesis_id']
                if hid in touched: raise HypothesisFailure('duplicate_operation', 'multiple updates for one H')
                touched.add(hid)
                index = next((i for i,h in enumerate(hs) if h.hypothesis_id == hid), None)
                if index is None: raise HypothesisFailure('unknown_hypothesis', 'unknown H update')
                if op == 'REJECT' and not basis: raise HypothesisFailure('missing_rejection_basis', 'rejection requires observed evidence')
                if op != 'KEEP':
                    hs[index] = replace(hs[index], status='rejected' if op == 'REJECT' else 'deprioritized', basis_refs=basis)
        opportunities = []
        for ref in proposal['useful_source_refs']:
            if ref not in eligible:
                raise HypothesisFailure('invalid_source_nomination', 'opportunity must be a newly discovered uninspected source')
            w = next(w for w in batch['windows'] if w.doc_ref == ref)
            opportunities.append({'doc_ref': ref, 'window_ref': w.window_ref, 'title': w.title,
                                  'preview': w.text, 'uninspected': True})
        # Atomic bounded H update: a malformed proposal cannot partially alter H.
        if sum(h.status == 'active' for h in hs) > 6:
            raise HypothesisFailure('active_hypothesis_limit', 'too many active H')
        return tuple(hs), proposal, opportunities

    def _should_update_hypotheses(self, decision, batch, new_claims, new_windows):
        return bool(any(h.status == 'active' for h in self._state.H)
                    or decision['hypothesis_ids_under_test'] or new_claims
                    or new_windows or batch['new_document_refs'])

    def _hypotheses(self, batch, new_claims):
        """Optional atomic transaction; only explicitly typed H failures are isolated."""
        self._assert_integrity()
        before = self._state.H
        start = len(self._state.T)
        try:
            hs, proposal, opportunities = self._propose_hypotheses(batch, new_claims)
        except HypothesisFailure as exc:
            # Corruption discovered during a provider failure must still be fatal.
            self._assert_integrity()
            responses = [e.payload()['output'] for e in self._state.T[start:]
                         if e.kind == 'role_response' and e.payload()['role'] == 'hypotheses']
            raw = responses[-1] if responses else None
            raw_hash = (hashlib.sha256((raw if isinstance(raw, str) else canonical(raw)).encode()).hexdigest()
                        if responses else None)
            failure = {'module': 'hypotheses', 'type': 'provider_failure' if exc.error_type == 'provider_failure' else 'contract_failure',
                       'error_type': exc.error_type, 'message': str(exc), 'raw_output_hash': raw_hash,
                       'H_unchanged': self._state.H == before}
            self._emit('hypothesis_update_failed', attempt_id=self._attempt, **failure)
            return [], [failure]
        # Integrity and commit/logging errors sit OUTSIDE the auxiliary catch.
        self._assert_integrity()
        self._state = replace(self._state, H=hs)
        self._emit('hypotheses_updated', before=[asdict(h) for h in before], after=[asdict(h) for h in hs], proposed=proposal)
        self._assert_integrity()
        return opportunities, []

    def _closure(self):
        payload = self._fact_snapshot()
        result = self._call('closure', payload)
        if result['status'] == 'CONTINUE':
            valid_r = {r.requirement_id for r in self._state.R}
            if any(m['requirement_id'] not in valid_r or not m['summary'].strip() for m in result['missing']):
                raise ValueError('invalid Closure feedback')
            self._ready = None
            self._emit('closure_feedback', **result)
        else:
            if not set(result['claim_ids']) <= {c.claim_id for c in self._state.C}: raise ValueError('unknown Closure C')
            self._ready = {'snapshot_hash': digest(payload), 'result': deepcopy(result)}
            self._emit('closure_ready', snapshot_hash=self._ready['snapshot_hash'], result=result)
        return result

    def finalize(self):
        if self._ready is None or self._ready['snapshot_hash'] != digest(self._fact_snapshot()):
            raise PermissionError('Final answer requires READY on this exact factual snapshot')
        permit = self._ready; self._ready = None  # one attempt, including failed finalization
        try:
            result = self._call('final', {'Q': self._state.Q, 'C': [asdict(c) for c in self._state.C],
                                          'Evidence': self._evidence_for_claims(), 'Closure': permit['result']})
            if not result['answer'].strip() or not set(result['claim_ids']) <= set(permit['result']['claim_ids']):
                raise ValueError('final answer must cite READY claims')
        except Exception as exc:
            self._emit('final_failure', error_type=type(exc).__name__, message=str(exc))
            raise
        self._emit('final_answer', **result)
        return result

    def step(self):
        # Fail closed before a corrupt Trace can be extended or another role called.
        self._assert_integrity()
        self._attempt += 1; self._ready = None
        old_c, old_h = self._state.C, self._state.H
        decision = None; batch = None; opportunities = []; outcome = None; error = None
        auxiliary_failures = []; hypothesis_outcome = 'not_applicable'
        acquisition_outcome = 'not_attempted'; claim_outcome = 'not_attempted'
        old_windows = set(self.bridge.evidence._windows)
        try:
            raw = self._call('actor', actor_view(self._state, self.bridge.source_handles()))
            decision = validate_decision(raw, self._state, self.bridge.tools.handles)
            if decision['decision'] == 'request_closure':
                outcome = {'decision': 'request_closure', 'closure': self._closure()}
            else:
                self._emit('tool_attempt', attempt_id=self._attempt, action=decision['action'])
                acquisition_outcome = 'attempted'
                batch = self.bridge.execute(decision['action'])
                self._emit('tool_observation', attempt_id=self._attempt, action=decision['action'],
                           result=batch['result'], windows=[asdict(w) for w in batch['windows']], audit=batch['audit'])
                acquisition_outcome = batch['result'].get('status')
                claim_outcome = 'attempted'
                self._claim_chain(decision['one_gap'], batch['windows'])
                claim_outcome = 'completed'
                new_claims = self._state.C[len(old_c):]
                new_windows = set(self.bridge.evidence._windows) - old_windows
                self._assert_integrity()
                if self._should_update_hypotheses(decision, batch, new_claims, new_windows):
                    opportunities, auxiliary_failures = self._hypotheses(batch, new_claims)
                    hypothesis_outcome = 'failed' if auxiliary_failures else 'completed'
                else:
                    hypothesis_outcome = 'skipped'
                    self._emit('hypothesis_update_skipped', attempt_id=self._attempt,
                               reason='no_active_or_tested_H_and_no_new_C_W_D', H_unchanged=True)
                outcome = {'decision': 'acquire', 'tool_status': batch['result'].get('status')}
        except IntegrityError:
            raise  # Never relabel integrity corruption as an auxiliary role error.
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc)}
            self._emit('step_failure', attempt_id=self._attempt, error=error)
            outcome = {'decision': decision.get('decision') if decision else None, 'failure': error}
        prior_h = {h.hypothesis_id:h for h in old_h}
        added_h = [h.hypothesis_id for h in self._state.H if h.hypothesis_id not in prior_h]
        downgraded = [h.hypothesis_id for h in self._state.H if h.hypothesis_id in prior_h and
                      prior_h[h.hypothesis_id].status == 'active' and h.status in ('rejected', 'deprioritized')]
        new_c = self._state.C[len(old_c):]
        reasons = []
        if new_c: reasons.append('new_useful_verified_claim')
        if added_h: reasons.append('new_nonduplicate_hypothesis')
        if downgraded: reasons.append('active_hypothesis_downgraded')
        if opportunities: reasons.append('new_uninspected_useful_source')
        record = {'attempt_id': self._attempt, 'decision': deepcopy(decision),
                  'family': family(decision) if decision else None,
                  'feedback': 'Gain' if reasons else 'NoGain', 'gain_reasons': reasons,
                  'claim_delta': [c.claim_id for c in new_c], 'hypothesis_delta': added_h+downgraded,
                  'observed_handles': [w.window_ref for w in batch['windows']] if batch else [],
                  'inspected_sources': batch['inspected_sources'] if batch else [],
                  'new_source_opportunities': opportunities, 'failure': error}
        record.update(acquisition_outcome=acquisition_outcome, claim_outcome=claim_outcome,
                      hypothesis_outcome=hypothesis_outcome, auxiliary_failures=auxiliary_failures)
        self._emit('step_outcome', **record)
        self._assert_integrity()
        return {**outcome, 'feedback': record['feedback'], 'claim_delta': record['claim_delta'],
                'acquisition_outcome': acquisition_outcome, 'claim_outcome': claim_outcome,
                'hypothesis_outcome': hypothesis_outcome, 'auxiliary_failures': auxiliary_failures}
