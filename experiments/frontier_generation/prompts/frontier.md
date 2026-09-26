You are choosing the next research frontier.

Given the Original Question and the information available in this view,
decide whether the research is complete.

If it is not complete, output exactly one current research need:
the most useful unresolved question to investigate next.

A good need:
- serves the Original Question;
- is not already adequately resolved by the information available to you;
- can materially reduce uncertainty, distinguish candidates, resolve a conflict,
  establish a required condition, or obtain the final requested relation;
- is specific enough to guide the next research action;
- does not assume a provisional hypothesis is already true.

Do not output a search query, tool action, long-term plan, list of subquestions,
confidence score, or explanation.

If the available information is sufficient to answer the Original Question,
return stop.

Return only one JSON object with exactly these keys:
{"decision":"act","need":"one unresolved research question"}
or {"decision":"stop","need":""}.
