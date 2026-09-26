You are updating a conservative Research State from one observed source.

Persistent State has two semantic layers:

1. Verified Claims:
   facts directly supported by the Observation.

2. Working Hypothesis:
   a provisional candidate or interpretation that may guide exploration
   but is NOT treated as solved by Goal Review.

Propose at most 2 new Verified Claims.

A Verified Claim must be directly entailed by the Observation.
Do not promote:
- partial clue agreement into "this is the answer",
- an article date into an event date,
- general source context into a stronger relation,
- two separate facts into an unsupported joined relation.

Candidate handling:

If the Observation establishes only some identifying clues for a
candidate, add only those atomic factual Claims and, if useful,
set the candidate as Working Hypothesis.

Do NOT add:
"The described person/team/game is X"
unless the Observation and existing Verified Claims are sufficient to
establish that task-level identification.

If the Observation contradicts the current Working Hypothesis on a
material requirement:
- add the directly supported contradictory fact when useful,
- clear the Working Hypothesis.

If the Observation directly supplies the requested final relation,
add that exact factual Claim.

Do not generate:
- Goal Residual,
- next Gap,
- Search query,
- D#/W#/offsets.

Return only:
{
  "claims_to_add": [
    "..."
  ],
  "hypothesis_update": {
    "action": "keep" | "set" | "clear",
    "statement": ""
  }
}


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
