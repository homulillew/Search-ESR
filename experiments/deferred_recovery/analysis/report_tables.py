"""Generate descriptive tables from preserved labels and usage, with no live calls."""
import json
from collections import Counter
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]


def rd(path):
    return json.loads(path.read_text())


def md(path, text):
    path.write_text(text.strip() + '\n')


def main():
    metrics = rd(TOP / 'analysis/METRICS.json')
    cases = rd(TOP / 'analysis/PER_CASE_METRICS.json')
    actions = rd(TOP / 'analysis/PER_ACTION_METRICS.json')
    by_cell = {r['cell']: r for r in cases}
    first = rd(TOP / 'r1/post_writer_cells.json')
    wl = rd(TOP / 'r1/WRITER_LABELS.json')
    first_claims = {r['cell'] for r in wl if r['strict_recovery_contribution']}
    lines = ['# R1: one real decision per cell', '',
             'Fourteen Actor calls, 14 tools, 45 new observations and 45 unchanged U1 Writer calls. '
             'All returned structurally and mechanically valid outputs. No retries or repairs.', '',
             '|Cell|Tool|Historical target rank (Search only)|Sufficient Need evidence|New necessary Claim|',
             '|---|---|---|---|---|']
    for a in actions:
        if a['round']:
            continue
        lines.append(f"|{a['cell']}|{a['tool']}|{a['target_rank'] or '—'}|{'yes' if a['sufficient'] else 'no'}|{'yes' if a['cell'] in first_claims else 'no'}|")
    lines += ['', 'D3/D4 only: G evidence and Claim recovery **5/5**; H evidence **3/5**, '
              'strict Claim recovery **2/5**. Fresh DR01: G recovered, H Find returned no match. '
              'D2: G preserved the 1993 conflict, H only corroborated the already stored 1992. '
              'D1: both recovered the July 24 article/date relation.', '',
              'The target rank is offline analysis, never Actor input. DR03 H preserves useful '
              '5/21-minute counterevidence rather than recovering the old 4-minute report. '
              'DR04 H is a date-scope admission miss, despite sufficient dated raw evidence. '
              'DR05 H writes a supported lower bound and an unsupported upper-bound Hypothesis.', '',
              'All 14 nonterminal cells continued from their exact real post-Writer state. '
              'R1 was not resampled and no outcome selected which cells entered R2. '
              'See continuation_freeze.json in ../r2 and the raw event journals.']
    md(TOP / 'r1/RESULTS.md', '\n'.join(lines))

    def latency(value):
        return str(value) if value is not None else 'not recovered by 2'

    lines = ['# R2: completed two-decision diagnostic', '',
             'The second decision adds 14 Actor calls, 7 Stop outputs, 7 tools, 27 observations and '
             '27 Writer calls. Total: 28 Actors, 72 Writers, 21 tools. Cells whose raw status remains '
             '`active` reached the frozen horizon; they are not running jobs.', '',
             '|Cell|Decision 1 → 2|First evidence|First necessary Claim|Strict Claim recovery|Original omitted fact recovered|',
             '|---|---|---|---|---|---|']
    for r in cases:
        seq = ' → '.join(a['tool'] for a in actions if a['cell'] == r['cell'])
        lines.append(f"|{r['cell']}|{seq}|{latency(r['decisions_to_evidence'])}|{latency(r['decisions_to_claim'])}|{r['strict_recovered']}|{r['old_omitted_fact_recovered']}|")
    lines += ['', '|Cohort|Cases / qids|G strict recovery|H strict recovery|H count-only sensitivity|',
              '|---|---|---|---|---|']
    for label in ['fresh', 'known_D3_D4', 'D3_D4_diagnostic', 'safety_D2', 'immediate_D1', 'all_diagnostic']:
        g, h = (metrics['cohorts'][label][arm] for arm in ['G', 'H'])
        ids = {r['case_id'] for r in cases if (label == 'fresh' and r['cohort'] == 'fresh') or
               (label == 'known_D3_D4' and r['category'] in ['D3', 'D4'] and r['cohort'] != 'fresh') or
               (label == 'D3_D4_diagnostic' and r['category'] in ['D3', 'D4']) or
               (label == 'safety_D2' and r['category'] == 'D2') or
               (label == 'immediate_D1' and r['category'] == 'D1') or label == 'all_diagnostic'}
        qids = {r['qid'] for r in cases if r['case_id'] in ids}
        lines.append(f"|{label}|{g['planned']} / {len(qids)}|{g['need_claim_recovery']}/{g['planned']}|{h['need_claim_recovery']}/{h['planned']}|{h['lenient_count_recovery']}/{h['planned']}|")
    lines += ['', 'The D3/D4 mixed row is descriptive, not a fresh primary estimate. '
              'DR03 H counts source-grounded refutation; it does not recover the old 4-minute atom '
              'or reconcile the duration conflict. DR04 H fails the frozen date-qualified criterion '
              'but passes a count-only sensitivity. Sensitivities never replace the primary labels.', '',
              'No H-only success. D3/D4 pairs: 3 both-success, 2 G-only, 0 both-fail. '
              'Count-only sensitivity: 4 both-success, 1 G-only. The evidence-level retrieval failure '
              'is DR05 H; the remaining strict failure is DR04 H admission scope. '
              'D2 and D1 stay outside the deferred denominator.', '',
              'R1 local no-recovery with paired G success: DR01, DR05, DR06. Only DR05 remains '
              'an end-to-end local-path regression, after two insufficient Find windows on the correct '
              'document. A new source was not necessary: G recovered the fact from that same old document.', '',
              'Need-bearing Find yield is 3/6 for D3/D4 (4/8 including controls). One of these is '
              'DR03 second-step corroboration of an already admitted duration, with an empty Writer. '
              'Excluding that repeated semantic information, first sufficient local-evidence yield is '
              '2/6 (3/8 with controls). Open was never selected, so its yield is unmeasured.', '',
              'There were no evidence-level premature Stops. DR04 H is one strict Claim-level premature '
              'Stop because the persistent count lacks the cutoff date; the Actor had enough raw evidence. '
              'The DR05 Actor explicitly rejected the unproven total-season inference and continued.']
    md(TOP / 'r2/RESULTS.md', '\n'.join(lines))

    lines = ['# Cost, cache and decision latency', '',
             'All costs include both decisions and every returned preview sent to U1. '
             'No price conversion is estimated. Tokens are provider usage, including reported reasoning '
             'within output tokens. Cache rate = total hit tokens / total input tokens, not an average of '
             'per-request rates.', '']
    for cohort in ['D3_D4_diagnostic', 'all_diagnostic']:
        g, h = (metrics['cohorts'][cohort][a] for a in ['G', 'H'])
        lines += [f'## {cohort}', '', '|Metric|G|H|', '|---|---:|---:|']
        for title, field in [('Actor calls', 'actor_calls'), ('Tool calls', 'tool_calls'),
                             ('Search', 'search_calls'), ('Find', 'find_calls'), ('Open', 'open_calls'),
                             ('Writer calls', 'updater_calls'), ('Input tokens', 'input'), ('Output tokens', 'output'),
                             ('Total tokens', 'total_tokens'), ('Cache hit tokens', 'hit'), ('Cache miss tokens', 'miss'),
                             ('Reasoning tokens (part of output)', 'reasoning')]:
            lines.append(f"|{title}|{g['cost'].get(field, 0):,}|{h['cost'].get(field, 0):,}|")
        lines.append(f"|Weighted cache hit rate|{g['cache_rate']:.2%}|{h['cache_rate']:.2%}|")
        lines.append(f"|Summed model request seconds|{g['cost']['model_seconds']:.3f}|{h['cost']['model_seconds']:.3f}|")
        lines.append(f"|Tool execution seconds (excludes loading)|{g['cost']['tool_seconds']:.3f}|{h['cost']['tool_seconds']:.3f}|")
        lines += ['', f"H used {1-h['cost']['total_tokens']/g['cost']['total_tokens']:.2%} fewer tokens. "
                  'Recovery quality is not equal; this does not pass the equal-recovery cost rule.', '']
    totals = Counter()
    for a in ['G', 'H']:
        totals.update(metrics['cohorts']['all_diagnostic'][a]['cost'])
    lines += ['## Total recorded usage', '',
              f"100 model calls: {totals['input']:,} input + {totals['output']:,} output = "
              f"{totals['total_tokens']:,} tokens. Cache hit {totals['hit']:,}, miss {totals['miss']:,}; "
              f"weighted hit rate **{totals['hit']/totals['input']:.2%}**. All 100 calls reported usage.", '',
              '## Paired costs', '', '|Case|G tokens|H tokens|G tools|H tools|Cheaper tokens|Cheaper tools|',
              '|---|---:|---:|---:|---:|---|---|']
    for pair in metrics['paired']:
        cid = pair['case_id']; g, h = (by_cell[cid + ':' + a]['cost'] for a in ['G', 'H'])
        lines.append(f"|{cid}|{g['input']+g['output']:,}|{h['input']+h['output']:,}|{g['tool_calls']}|{h['tool_calls']}|{pair['token_cost_comparison']}|{pair['tool_cost_comparison']}|")
    lines += ['', '## Interpretation', '',
              '- Search normally exposes five previews and therefore five Writer calls. Find normally '
              'exposes one, sometimes none. Much of the token difference follows this fan-out; it is '
              'not evidence that local policy is generally more efficient at equal recovery quality.',
              '- G first sufficient evidence and first necessary Claim are at decision 1 for all five '
              'D3/D4 cases. H has evidence at decisions 2/1/1/1/not-recovered for DR01–05; strict Claims '
              'at 2/1/1/not-recovered/not-recovered. Failures are censored at horizon 2, not silently omitted.',
              '- H adds no action-count advantage: eight tools versus seven in D3/D4. DR01 and D2 DR06 '
              'need an extra recovery decision after an insufficient first Find. No faster local recovery '
              'was observed on this bank.',
              '- Summed request durations are not end-to-end wall time. Four requests can run concurrently; '
              'cache state, completion length and scheduling are not controlled latency interventions. '
              'Tool timing excludes loading, registry restoration and model initialization.',
              '- Per-qid correlation and known-case selection preclude independent-sample significance claims.']
    md(TOP / 'analysis/COSTS.md', '\n'.join(lines))
    print('Wrote R1, R2 and cost tables from preserved results.')


if __name__ == '__main__':
    main()
