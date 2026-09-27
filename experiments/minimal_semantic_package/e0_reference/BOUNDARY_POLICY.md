# Source-anchored boundary reference

## Authority and construction

The current task governs this new experiment. Preserve all old certificates,
labels, calls and results byte-for-byte. Select all48 historical certificates,
covering24 cells,16 natural snapshots and9 qids. There are17 distinct Parents
and34 distinct Parent+Locator pairs. One package is shared across all evidence
subsets of the same pair; no evidence-dependent package selection is allowed.

The author is a single task-familiar Codex reviewer who has seen the previous
study. This is not an independent or cognitively blind annotation. The boundary
builder's actual inputs are restricted to Q, Parent and Locator; it cannot read
Claims, previous verdicts or model outputs. Its source-only input and all
choices are separately committed and hashed before support-label construction.

## Exact source units

78 ordered units cover every non-whitespace Parent character. Texts, offsets
and source hashes are stored in UNITS.json. Offsets count Unicode code points,
start inclusive/end exclusive. The original Parent text remains immutable;
whitespace between spans is recoverable from offsets. No new entity, paraphrase
or reordered span is introduced. A locator may begin/end inside a unit; its
unit IDs are all intersecting units, and those units must be retained in either
target or interpretive context. Each verifier sees exact unit text and IDs.

Minimality means the smallest sufficient semantic package at this frozen
segmentation, not character-level minimality. A source unit may include a
connective attached to its material predicate. Units are ephemeral evaluation
material, never finer persistent Requirement nodes.

## Target versus context versus sibling

Target units contribute truth conditions. Interpretive units only resolve
reference, ellipsis or narrative framing. Siblings are excluded from the
verifier payload, including Original Q and the full Parent. None of the three
categories supplies evidence by itself. The verifier's evidence is solely the
listed current Verified Claims. Missing governing relations remain missing.

Examples of the actual reference choices:

- Euler: references + well-known figure + birth/European/initials qualifiers
  are target; the engineer and scientist references are siblings.
- Clinical: first-described-case/individual roles and the selected clinical
  predicate are target. Report country and country history are siblings.
  In the walking/shoulder locator, the prior pain description is interpretive
  context; it resolves pain without adding its half-year qualifier to this
  narrower cause/effect target.
- Ding: person/spouse role, 2019 frame and childlessness are target. The gift,
  building and complex are siblings. No literal Ding entity is invented in a
  Parent that says only “This person”; evidence must bind a concrete branch.
- DLC technology: DLC/base-game binding and technology change are target.
  Religion and qualified European-nation mechanics are independent conditions.
- Book publication/interval: article and book publication operands and the
  six-year comparison are target; the similar-topic condition is separate.
  For the topic locator, the two publication operands and topic comparison
  are target; the six-year comparison is separate.
- Champion: coder/nationality, membership and championship remain target.
  For the full-sentence locator the questioner's discovery phrase is context,
  not an evidence obligation about the questioner's private mental history.
- Alma mater/building: target is building–university affiliation in its as-of
  frame, never attendance of a person. The opening schedule is a sibling.
- Letter: source-letter attribution, author and author-country relationship
  remain in target. Merely naming Romania does not prove it is the author's
  country.

Packages may retain pronouns already present in the Parent. A pronoun names a
role to be grounded in the Claims; it does not prove identity. Outside-Parent
entity names cannot be injected as synthetic units. If an extractor cannot
express a complete scope using the given units, E2 allows
UNITIZATION_INSUFFICIENT. There is no free-text repair.

## Candidate-conditional support

As required by the task's clinical and Ding positive controls, target support
can be established for an observed candidate branch without first proving that
it is the final answer satisfying all other Q/R constraints. This is a scoped
support judgment, not permission to close the whole Parent or erase the
branch's bindings. A target that itself contains a membership, source-reference
or temporal-comparison relation still requires that relation in evidence.

This convention is material: inherited anaphoric roles are not instructions to
revalidate every clue in Original Q. The original task/question remain the
semantic authority. E4, if reached, must preserve bindings and still-open
relations in an ephemeral view; it never rewrites R.

## Limits declared before calls

This is a familiar, correlated mechanism bank. The34 packages are not34 new
independent questions. Only2 packages use nonempty interpretive-context sets;
context/target separation is therefore sparsely tested. Some source-only
pronouns remain abstract, as the task prohibits adding new source units.

Publication-year versus exact-day comparison, isolated “that paper” evidence,
general mechanics versus its enumerated subconditions, and the letter
author-country shorthand require explicit ambiguity disclosure in the support
reference. Keep all primary labels frozen; no output-conditioned relabeling.
