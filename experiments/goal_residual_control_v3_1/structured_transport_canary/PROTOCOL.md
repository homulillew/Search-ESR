# One production transport canary

Reuse the 24 v3 historical requests selected before prior capability testing (12 Actor,8 Updater,4 Goal). No research tools. Use Responses object-root schema, nested anyOf tool branches; no array bounds in transport. Required keys, types, enum and closed shapes checked separately from exact v2 Harness. Select responses_structured only if all 24 are structurally valid; otherwise json_mode_fallback uniformly. No extra probe or retry. Default thinking/sampling unchanged. Even fallback continues Admission.

Official reference checked 2026-09-26: https://api-docs.deepseek.com/api/create-response/ documents text.format json_schema and default enabled thinking. Actual production canary, not documentation, determines selection.
