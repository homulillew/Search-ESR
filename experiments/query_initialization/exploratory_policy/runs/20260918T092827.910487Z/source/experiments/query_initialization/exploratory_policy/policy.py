"""A two-action prompt ablation, separate from the default Agent runtime."""
import copy
import json
from llm_chat.agent import AGENT_PROMPT, TOOLS

GUIDANCE = (
    "Begin with a distinctive, independently searchable entry into the question; you do not need to cover every condition in the first search.\n"
    "You may omit conditions, but preserve the subjects, relationships, negation, and time scope of those you use, and treat unverified identities as hypotheses.\n"
    "After observing the results, choose the next search or open from what the returned text actually establishes and what remains unresolved."
)
PROBE = (
    "This is a bounded research probe with at most two tool actions. Begin with one search. "
    "Issue at most one tool call in each response. Every search returns exactly six documents; use k=6 if specifying k. "
    "After the first observation, you may search again, open a returned window, or answer if the observed evidence is sufficient. "
    "You do not need to finish the whole question within this probe."
)


def system_prompt(config, arm):
    if arm not in ("current", "exploratory"):
        raise ValueError("Unknown arm")
    base = config.system_prompt + "\n\n" + AGENT_PROMPT + "\n\n" + PROBE
    return base + ("\n\n" + GUIDANCE if arm == "exploratory" else "")


def schemas():
    tools = copy.deepcopy(TOOLS)
    tools[0]["function"]["description"] += " This probe returns exactly six documents."
    tools[0]["function"]["parameters"]["properties"]["k"] = {
        "type": "integer", "enum": [6], "description": "Fixed at 6 for this probe; omission also uses 6."
    }
    return tools


def request(config, messages, step):
    return dict(model=config.model, messages=copy.deepcopy(messages), tools=schemas(),
        tool_choice={"type": "function", "function": {"name": "search"}} if step == 1 else "auto",
        parallel_tool_calls=False, stream=False, max_tokens=1536, **config.request_options())


def action(message, finish_reason, step):
    """No semantic repair, call selection or silent query transformation."""
    calls = message.get("tool_calls") or []
    if not calls:
        if step != 2 or finish_reason != "stop" or not (message.get("content") or message.get("refusal")):
            raise ValueError("Expected first Search or a complete second-step response")
        return None
    # This endpoint reports `stop` for complete forced function calls. Retain
    # the raw marker and require the same single-call JSON/schema contract.
    # A length-limited or filtered response remains non-executable.
    if finish_reason not in ("tool_calls", "stop") or len(calls) != 1:
        raise ValueError("Exactly one complete tool call is allowed per action")
    call = calls[0]
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])
    if not isinstance(args, dict):
        raise ValueError("Arguments must be an object")
    if name == "search":
        if not set(args) <= {"query", "k"} or not isinstance(args.get("query"), str) or not args["query"].strip():
            raise ValueError("Invalid search arguments")
        if type(args.get("k", 6)) is not int or args.get("k", 6) != 6:
            raise ValueError("Search k must be six")
        actual = dict(query=args["query"], k=6)
    elif name == "open" and step == 2:
        if set(args) != {"window_ref", "direction"} or not isinstance(args["window_ref"], str) or args["direction"] not in ("before", "after", "around"):
            raise ValueError("Invalid open arguments")
        actual = dict(args)
    else:
        raise ValueError("First action must search; second may search or open")
    return dict(name=name, tool_call_id=call["id"], requested_arguments=args, arguments=actual)
