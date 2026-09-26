

EXACT RESPONSE SERIALIZATION CONTRACT (examples illustrate formatting only)
The complete response must be one JSON object matching the schema below.
Use exactly the lowercase action discriminator "tool". Never use "type", "name", or an "arguments" wrapper for an action.
Search requires exactly tool, query, k. k must be an integer from 1 to 10 (use 5 when choosing the default).
Find requires exactly tool, doc_ref, query. Open requires exactly tool, window_ref, direction; direction is before, after, or around.
No additional keys are allowed. Do not emit Markdown fences or text outside JSON.
STOP means decision=stop, gap="", actions=[]. ACT means a nonempty gap and one or two actions.
All D#/W# arguments must already exist in the supplied workspace before either action executes. A Search→Find batch referencing a new document from that Search is invalid. Two independent searches or inspections of two already available documents are legal.
The Tool schema in the input describes available tools and their parameter semantics. Your response uses the flat objects in THIS contract, not an OpenAI function-call wrapper.

Full JSON Schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "oneOf": [
    {
      "type": "object",
      "properties": {
        "decision": {
          "const": "stop"
        },
        "gap": {
          "const": ""
        },
        "actions": {
          "type": "array",
          "maxItems": 0
        }
      },
      "required": [
        "decision",
        "gap",
        "actions"
      ],
      "additionalProperties": false
    },
    {
      "type": "object",
      "properties": {
        "decision": {
          "const": "act"
        },
        "gap": {
          "type": "string",
          "minLength": 1,
          "pattern": "\\S"
        },
        "actions": {
          "type": "array",
          "minItems": 1,
          "maxItems": 2,
          "items": {
            "oneOf": [
              {
                "type": "object",
                "properties": {
                  "tool": {
                    "const": "search"
                  },
                  "query": {
                    "type": "string",
                    "description": "A standalone global search query, usually in English"
                  },
                  "k": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of documents, default 5"
                  }
                },
                "required": [
                  "tool",
                  "query",
                  "k"
                ],
                "additionalProperties": false
              },
              {
                "type": "object",
                "properties": {
                  "tool": {
                    "const": "find"
                  },
                  "doc_ref": {
                    "type": "string",
                    "pattern": "^D[1-9][0-9]*$",
                    "description": "Stable document handle returned by search, for example D3"
                  },
                  "query": {
                    "type": "string",
                    "description": "Local query for the fact or passage to locate"
                  }
                },
                "required": [
                  "tool",
                  "doc_ref",
                  "query"
                ],
                "additionalProperties": false
              },
              {
                "type": "object",
                "properties": {
                  "tool": {
                    "const": "open"
                  },
                  "window_ref": {
                    "type": "string",
                    "pattern": "^W[1-9][0-9]*$",
                    "description": "Stable observed-window handle returned by search, find, or open"
                  },
                  "direction": {
                    "type": "string",
                    "enum": [
                      "before",
                      "after",
                      "around"
                    ]
                  }
                },
                "required": [
                  "tool",
                  "window_ref",
                  "direction"
                ],
                "additionalProperties": false
              }
            ]
          }
        }
      },
      "required": [
        "decision",
        "gap",
        "actions"
      ],
      "additionalProperties": false
    }
  ]
}

Complete formatting examples (D3 and W1 are hypothetical existing handles, not targets for this task):
{
  "decision": "act",
  "gap": "Which observatory is described by the remaining historical clues?",
  "actions": [
    {
      "tool": "search",
      "query": "observatory mountain founded historical measurements",
      "k": 5
    }
  ]
}

{
  "decision": "act",
  "gap": "When was the instrument installed at the candidate observatory?",
  "actions": [
    {
      "tool": "find",
      "doc_ref": "D3",
      "query": "instrument installation year"
    }
  ]
}

{
  "decision": "act",
  "gap": "What does the surrounding passage say about the instrument installation?",
  "actions": [
    {
      "tool": "open",
      "window_ref": "W1",
      "direction": "around"
    }
  ]
}

{
  "decision": "act",
  "gap": "Which records can establish the observatory instrument history?",
  "actions": [
    {
      "tool": "search",
      "query": "observatory instrument installation history",
      "k": 5
    },
    {
      "tool": "search",
      "query": "observatory annual report equipment commissioning",
      "k": 5
    }
  ]
}

{
  "decision": "stop",
  "gap": "",
  "actions": []
}
