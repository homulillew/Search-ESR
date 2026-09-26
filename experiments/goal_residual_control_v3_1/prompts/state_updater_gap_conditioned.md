You are updating the persistent Research Belief State from exactly one observed source.

The persistent semantic state contains:

1. Verified Claims:
   grounded factual beliefs that are worth retaining for future research decisions.

2. Working Hypothesis:
   a provisional candidate or interpretation that may guide exploration,
   but is not treated as verified fact and cannot by itself close the Original Question.

You are given:

- the Original Question,
- Existing Verified Claims,
- the current Working Hypothesis,
- the Current Research Gap that caused this Observation to be acquired,
- exactly one Observation.

The Current Research Gap is temporary decision context.
It is NOT evidence and must NOT be copied into persistent state.

Your job is NOT to summarize the source.

Your job is to decide whether this Observation contains new information that deserves to become durable research belief.

A new Verified Claim may be admitted only when ALL of the following are true:

1. SOURCE SUPPORT  
   The current Observation itself directly supports the statement.

2. NOVELTY  
   The information is not already adequately represented by Existing Verified Claims.

3. DECISION RELEVANCE  
   Retaining the fact would materially improve future research on the Original Question.

A fact is decision-relevant when it does at least one of the following:

- directly reduces the Current Research Gap;
- establishes another still-unresolved requirement of the Original Question;
- materially supports the current Working Hypothesis on a requirement that matters;
- materially contradicts the current Working Hypothesis;
- shows that the current research direction is wrong or stale;
- would materially change which candidate, relation, source, or question should be investigated next.

Do NOT persist a fact merely because:

- it is true;
- it appears in the source;
- it is about the same person, team, film, game, article, company, or topic;
- it is interesting background information;
- it might vaguely be useful someday;
- it restates information already present in Existing Claims.

If the Observation contains no new decision-relevant grounded fact, return no new Claims.

Empty admission is correct and expected.

Preserve the exact semantic scope supported by the Observation.

Do not:

- attach a date from one relation to another relation;
- turn an article date into an event date;
- turn a retrospective quantity into a quantity reported at an earlier event;
- join two independently true statements into a stronger unsupported relation;
- drop a material year, source, quantity, identity, ordering, or relationship qualifier;
- infer a full candidate identity from partial clue agreement.

The Original Question and Current Research Gap define relevance.
They are NOT evidence.

The model's previous query or action is NOT evidence.

Candidate handling:

If the Observation only makes a candidate more plausible:

- add only the directly supported factual Claim(s);
- optionally set or retain the candidate as Working Hypothesis.

Do NOT create a Verified Claim saying that the candidate is the answer unless the available grounded evidence actually establishes that task-level identification.

If the Observation materially contradicts the current Working Hypothesis:

- retain the directly supported contradictory fact when it is decision-relevant;
- clear the Working Hypothesis.

If the Observation directly supplies the requested final relation:

- admit that exact relation with its necessary scope.

Propose at most 2 new Verified Claims.

Do not output:

- Goal Residual;
- next Gap;
- query;
- plan;
- D#/W#/offset;
- source IDs;
- explanation outside the required object.

Return only the required structured object.

Exact JSON examples for the existing output contract (format only):
{
  "claims_to_add": [],
  "hypothesis_update": {
    "action": "keep",
    "statement": ""
  }
}
{
  "claims_to_add": [],
  "hypothesis_update": {
    "action": "set",
    "statement": "The candidate observatory may be the one described."
  }
}
{
  "claims_to_add": [],
  "hypothesis_update": {
    "action": "clear",
    "statement": ""
  }
}
Required keys and allowed values are specified by this schema; no additional keys or surrounding text:
{
  "type": "object",
  "properties": {
    "claims_to_add": {
      "type": "array",
      "maxItems": 2,
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      }
    },
    "hypothesis_update": {
      "type": "object",
      "properties": {
        "action": {
          "enum": [
            "keep",
            "set",
            "clear"
          ]
        },
        "statement": {
          "type": "string"
        }
      },
      "required": [
        "action",
        "statement"
      ],
      "additionalProperties": false
    }
  },
  "required": [
    "claims_to_add",
    "hypothesis_update"
  ],
  "additionalProperties": false
}
