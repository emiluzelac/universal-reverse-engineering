# Universal Reverse Engineering Skill

[![validate](https://github.com/emiluzelac/universal-reverse-engineering/actions/workflows/validate.yml/badge.svg)](https://github.com/emiluzelac/universal-reverse-engineering/actions/workflows/validate.yml)

An [Agent Skill](https://agentskills.io/specification) that teaches an AI coding agent to work out **how things work**: a program, a file format, a protocol, a gadget, a product, a process. It is evidence-first. The agent observes, builds a model, tests it, and explains, and it keeps *observed*, *inferred*, *verified* and *unknown* apart the whole way.

It is one folder, `reverse-engineering/`, in the open Agent Skills format, so the same copy works in Claude Code, Qwen Code, Codex and any other host that reads that format. It also degrades gracefully: pasted into a plain chat window with no tools, it still runs the method without inventing tool calls.

The skill's own [README](reverse-engineering/README.md) has the full install table, a first hands-on test, notes for bare chat endpoints, and the version history.

## Install

```bash
git clone https://github.com/emiluzelac/universal-reverse-engineering.git
cd universal-reverse-engineering
mkdir -p ~/.claude/skills ~/.agents/skills
cp -R reverse-engineering ~/.claude/skills/     # Claude Code
cp -R reverse-engineering ~/.agents/skills/     # Qwen Code and Codex
```

Restart the agent, then type `/reverse-engineering` (Claude Code, Qwen Code) or `$reverse-engineering` (Codex), or just ask how something works. Each host also loads the skill on its own when a request matches its description.

## What is in the skill

- **Two modes.** A quick explanation for conceptual questions and photos, and a full investigation with an investigation plan, a hypothesis ledger and a run log when there are artifacts to test. The agent picks the mode first.
- **The loop.** Observe, decompose, hypothesize, test, reconstruct, verify, explain. Predictions go in the run log before the run, not after.
- **Honesty without tools.** If the host offers no file or shell access, the agent works from the skill text alone and says which reference it would have read. It never fabricates a file read, a command result, or a path.
- **Playbooks** for software, protocols, hardware, and systems or processes, plus safety and reporting references and a report template.
- **Two small helpers**, standard-library Python, read-only: `file_probe.py` (size, hash, entropy, signature guess) and `snapshot.py` (manifest a folder before and after an experiment, then diff).
- **A practice target.** `examples/number_machine.py` is a harmless black box for the agent, or you, to reverse engineer.

## How it was tested

- The [Agent Skills validator](https://agentskills.io) passes, and `tests/smoke.sh` runs it together with syntax, helper and link checks. The same script runs in CI on every push.
- A fresh Claude Code agent with no knowledge of the practice target's rule recovered it exactly, pre-registering every prediction, in 34 logged runs plus a 257-input sweep, and left no side effects on disk.
- A local 27B model (Qwen3.8-27B behind SGLang) reached the same rule through a plain chat window, with the user pasting command output, and labelled its claims honestly.
- `tests/bare_chat_sample.py` measures how often a model behind a bare chat endpoint fabricates a tool call when it is handed `SKILL.md` as a system prompt. On that local model the installed text sits at the model's floor, about 2 in 30, and the one-line preface the skill's README recommends takes it to 0. The same measurement is how one wording change was caught and reverted: naming a runnable bundled file inside `SKILL.md` roughly doubled the rate.

Run the measurement against your own model:

```bash
python3 tests/bare_chat_sample.py --endpoint http://127.0.0.1:8888/v1/chat/completions \
  --model your-model --skill reverse-engineering/SKILL.md --runs 30
python3 tests/bare_chat_sample.py ... --preface     # with the README's mitigation line
```

## Contributing

Issues and pull requests are welcome. A few things keep the skill universal:

- Keep `SKILL.md` host-neutral. Use only the portable frontmatter fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) and never assume a host-specific variable exists in the shell.
- `tests/smoke.sh` must pass.
- If you change `SKILL.md`, run `tests/bare_chat_sample.py` against a small local model before and after, 30 runs each, and say what you measured in the pull request. Wording that reads naturally to a large model can make a small one invent tool calls.
- Bump `metadata.version` and add a line to the Versions list in `reverse-engineering/README.md`.

## Credits and licence

Written by Emil Uzelac. The first draft was made with ChatGPT; the audit, host-neutral packaging, test runs and later versions were done with Claude Code. Released under the [MIT licence](LICENSE).
