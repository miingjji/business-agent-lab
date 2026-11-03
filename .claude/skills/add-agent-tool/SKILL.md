---
name: add-agent-tool
description: Add a new tool (function calling) to the terminal assistant in this repo's week-05 folder — the function and its tool definition in tools.py, plus registration in TOOLS and FUNCTIONS in 03_assistant.py — then verify it. Use this whenever the user wants to add, create, or extend a tool, function, or capability of the assistant, e.g. "도구 추가해줘", "tool 만들어줘", "어시스턴트에 ○○ 기능 붙여줘", "add a tool that…", "let the assistant do X", or when they say they finished the week-05 exercise and want a tool of their own, even if they never say the word "tool".
---

# Add a tool to the week-05 assistant

The assistant in `week-05/` works because three things agree with each other. A tool that is missing any one of them fails quietly: the model never sees it, or sees it and the program cannot run it. So do all three, then check they line up.

1. **The function** in `week-05/tools.py` does the work.
2. **The tool definition** (an UPPER_CASE dict next to it) tells the model what the tool is. The model reads only this dict, never the function, so the `description` and each parameter's `description` are the model's whole manual. Say what the tool returns and what it does not do.
3. **The registration** in `week-05/03_assistant.py`: add the definition to `TOOLS`, the function to `FUNCTIONS`, and extend the `from tools import (...)` block.

The definition's `"name"` must equal the function name and the `FUNCTIONS` key. `dispatch()` looks the function up by that name, so a mismatch shows up as `error: unknown function`.

## Before writing code

Read `tools.py` and the `TOOLS`/`FUNCTIONS`/`SYSTEM_PROMPT` section of `03_assistant.py` first. Match what is there rather than what you remember: the existing tools show the house style (a section comment with dashes, the dict then the function, short descriptions).

If the request leaves out something that changes the design (which data source, whether it may write files, what a failure should look like), ask one short question. If a sensible default exists, take it and say so in one line.

## Writing the function

- Validate inputs and `raise ValueError("short message")` on bad ones. `dispatch()` catches every exception and returns `error: <message>` to the model, which the system prompt tells it to report honestly instead of inventing a result. A clear message is what lets the model recover.
- Return a string or something `json.dumps` can serialize. `dispatch()` converts non-strings to JSON.
- Return a readable string such as `f"no events on {date}"` for an empty result rather than `None` or an empty list; the model answers better from words than from nothing.
- For network calls use `requests` with a `timeout` and `raise_for_status()`, and send the same `User-Agent` style as the existing tools. Prefer services that need no API key.
- A tool that writes files must keep the path inside its folder (see how `save_note` sanitizes the name and never overwrites). Never build paths from raw model output.
- Keep the tool small: one job, flat parameters (`string`, `number`, `enum`). `required` lists every parameter without a default.

## Registering

Add the import, the `TOOLS` entry, and the `FUNCTIONS` entry. Then look at `SYSTEM_PROMPT`: if the model could confuse the new tool with an existing one, or must be told to prefer it (the way it says "Use convert_currency for any currency conversion"), add one short sentence. Do not touch the prompt otherwise.

## Verifying

The model call needs `OPENROUTER_API_KEY` and network, which may not be available, so verify in two layers and say which ones you ran.

**Always (no key needed)**, from the repo root with the venv active if one exists:

```sh
cd week-05 && python - <<'EOF'
import importlib.util, sys
sys.path.insert(0, ".")
spec = importlib.util.spec_from_file_location("assistant", "03_assistant.py")
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
names = [t["function"]["name"] for t in a.TOOLS]
assert sorted(names) == sorted(a.FUNCTIONS), (names, list(a.FUNCTIONS))
for t in a.TOOLS:
    assert t["function"]["name"] == a.FUNCTIONS[t["function"]["name"]].__name__
print("registered:", names)
EOF
```

Then call the new function directly once with a normal input and once with a bad input, and run it through `dispatch()` with a fake tool call (`{"id": "t1", "function": {"name": "<name>", "arguments": "{...}"}}`) to confirm the bad input becomes an `error: ...` string rather than a crash.

**If `.env` has a key**, run the assistant once with `printf '<question that needs the tool>\nexit\n' | python week-05/03_assistant.py` and read the trace for `tool call`, `tool result`, and the final answer. Check the answer against what the tool really returned. If there is no key, say that the live trace was not run and give the user the exact question to try.

## Reporting

Finish with a short summary in Korean: the tool's name, the three places you changed, what you verified, and what you could not (for example, the live trace). The README says the student explains the code themselves, so keep the explanation of what each part does to a few lines and offer to go deeper rather than writing an essay.
