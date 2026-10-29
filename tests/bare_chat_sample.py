#!/usr/bin/env python3
"""Measure fabricated tool calls when a model gets SKILL.md as a bare system prompt.

Hosts that support Agent Skills give the model real tools. A plain chat endpoint
does not, and a model that has just read a skill mentioning scripts may invent a
tool call anyway. This script sends the same full-mode request N times to an
OpenAI-compatible /v1/chat/completions endpoint, with the body of SKILL.md as the
system prompt, and counts replies that contain tool-call markup.

Standard library only. Example:

    python3 tests/bare_chat_sample.py \
        --endpoint http://127.0.0.1:8888/v1/chat/completions \
        --model llm --skill reverse-engineering/SKILL.md --runs 30

Add --preface to prepend the one-line "You have no tools" notice that the skill's
README recommends for bare chat windows, and compare the two counts.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PREFACE = ("You have no tools in this conversation. The user runs every command "
           "and pastes the results; work only from what is pasted.")

DEFAULT_PROMPT = """I have a small command-line program, number_machine, that takes one integer and prints JSON. I cannot share its source. I ran it six times:

input 5 -> {"channel": "B", "input": 5, "status": "ok", "value": 16}
input 8 -> {"channel": "A", "input": 8, "status": "ok", "value": 66}
input -2 -> {"channel": "A", "input": -2, "status": "ok", "value": 6}
input 0 -> {"input": 0, "status": "idle", "value": 0}
input 21 -> {"input": 21, "status": "out_of_range"}
input 3 -> {"channel": "B", "input": 3, "status": "ok", "value": 10}

Use full mode. Investigate it as a black box: give me the investigation plan, at least two competing hypotheses about the rule, the hypothesis ledger and run log in the skill's layout, and the single most discriminating next test (which inputs to run and what each hypothesis predicts). Label everything observed / inferred / verified / unknown. Do not pretend to run anything yourself."""

# Markup a model emits when it believes it is calling a tool. Matches the
# Qwen/Hermes <tool_call> form, the <function=...> form, and OpenAI-style fields.
FABRICATION = re.compile(r"tool_call|<function=|<\|tool", re.IGNORECASE)


def skill_body(path: pathlib.Path) -> str:
    """SKILL.md without its YAML frontmatter, as a host would inject it."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break
    return "\n".join(lines).lstrip("\n")


def one_run(i, args, system, user):
    payload = {
        "model": args.model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"
    req = urllib.request.Request(args.endpoint, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=args.timeout) as resp:
        reply = json.load(resp)
    choice = reply["choices"][0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    m = FABRICATION.search(content)
    fabricated = bool(msg.get("tool_calls")) or m is not None
    snippet = content[max(0, m.start() - 60): m.start() + 40] if m else content[:100]
    return {
        "run": i,
        "fabricated": fabricated,
        "finish_reason": choice.get("finish_reason"),
        "completion_tokens": (reply.get("usage") or {}).get("completion_tokens"),
        "seconds": round(time.time() - t0, 1),
        "snippet": " ".join(snippet.split()),
        "payload": payload,
        "reply": reply,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--endpoint", required=True, help="full URL of /v1/chat/completions")
    ap.add_argument("--model", required=True)
    ap.add_argument("--skill", required=True, type=pathlib.Path, help="path to SKILL.md")
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--parallel", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--max-tokens", type=int, default=400,
                    help="enough to see whether the reply opens with a fabricated call")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--preface", action="store_true", help=f"prepend: {PREFACE!r}")
    ap.add_argument("--prompt", type=pathlib.Path, help="file with a user prompt to use instead of the built-in one")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"), help="or set OPENAI_API_KEY")
    ap.add_argument("--out", type=pathlib.Path, help="directory to save every request and reply as JSON")
    args = ap.parse_args()

    system = skill_body(args.skill)
    if args.preface:
        system = PREFACE + "\n\n" + system
    user = args.prompt.read_text(encoding="utf-8") if args.prompt else DEFAULT_PROMPT
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)

    print(f"endpoint={args.endpoint} model={args.model} skill={args.skill} runs={args.runs} "
          f"temp={args.temperature} max_tokens={args.max_tokens} preface={args.preface}")
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(one_run, i, args, system, user): i for i in range(1, args.runs + 1)}
        for fut in futures:
            i = futures[fut]
            try:
                results.append(fut.result())
            except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as e:
                errors.append((i, repr(e)))
    results.sort(key=lambda r: r["run"])
    for r in results:
        flag = "FAB" if r["fabricated"] else "ok "
        print(f"{r['run']:3d} {flag} {r['finish_reason']:<6} {str(r['completion_tokens']):>5} tok {r['seconds']:>5}s | {r['snippet']}")
        if args.out:
            (args.out / f"run-{r['run']:03d}.json").write_text(
                json.dumps({k: r[k] for k in ("run", "fabricated", "finish_reason", "completion_tokens", "payload", "reply")}, indent=1))
    for i, e in errors:
        print(f"{i:3d} ERR {e}")
    n_fab = sum(r["fabricated"] for r in results)
    print(f"\nfabricated tool calls: {n_fab}/{len(results)}" + (f" ({len(errors)} request errors)" if errors else ""))
    return 1 if errors and not results else 0


if __name__ == "__main__":
    sys.exit(main())
