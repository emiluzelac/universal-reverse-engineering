# Universal Reverse Engineering Skill

A portable, evidence-first investigation toolkit for understanding **how things work**: software, local files and formats, protocols, electronics, mechanisms, products, and processes. Written in the open [Agent Skills](https://agentskills.io/specification) format, which Claude Code, Qwen Code, Codex and other agent hosts read natively. Useful to a curious beginner while still enforcing rigorous engineering habits.

## What is inside?

- `SKILL.md`: the agent's main workflow (observe, decompose, hypothesize, test, reconstruct, verify, explain), with a quick mode for conceptual questions and a full mode that keeps a hypothesis ledger and a run log.
- `references/`: focused playbooks for software, protocols, hardware, systems, evidence, safety, and local tools.
- `scripts/file_probe.py`: static local file fingerprint (size, hash, signature guess, sample entropy).
- `scripts/snapshot.py`: read-only directory manifests and differential analysis.
- `templates/report.md`: reusable investigation report / experiment ledger.
- `examples/number_machine.py`: an offline black-box investigation exercise.

No network access or third-party Python packages are required by these scripts. They never execute target software.

## Install

The skill is one directory named `reverse-engineering`. Copy the **whole directory** into the skills folder of each agent you use. Back up any existing copy first; do not merge files from two versions.

| Agent | User-level location | Also reads | Invoke with |
|---|---|---|---|
| Claude Code | `~/.claude/skills/reverse-engineering/` | `.claude/skills/` in a project | `/reverse-engineering` |
| Qwen Code | `~/.agents/skills/reverse-engineering/` or `~/.qwen/skills/` | `.agents/skills/` or `.qwen/skills/` in a project | `/reverse-engineering` |
| Codex | `~/.agents/skills/reverse-engineering/` | `.agents/skills/` in a project | `$reverse-engineering` |

`~/.agents/skills/` is shared by Qwen Code and Codex. Claude Code does not read it, so keep a second copy (or a symlink) under `~/.claude/skills/`.

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
cp -R reverse-engineering ~/.claude/skills/
cp -R reverse-engineering ~/.agents/skills/
```

Restart the agent, then type the invocation from the table, or simply ask: "Reverse engineer how this small program works. Treat it as a black box, test competing hypotheses, and show your evidence." Each host also loads the skill on its own when a request matches the description.

## First hands-on test

Ask your agent:

> Use the reverse-engineering skill to investigate the `number_machine.py` example bundled in its `examples/` folder as a black box. Don't read its source until you've made and tested predictions. Run it with at least six inputs, log competing hypotheses, and tell me the rule in plain English.

The script accepts an integer and returns a JSON object. It is a deliberately harmless local practice target.

## If your model runs behind a bare chat endpoint

A **model** does not load `SKILL.md` just because the file is on disk. The *agent host* must support Agent Skills, tool calls, and reading the skill folder. A plain chat window in front of Ollama, LM Studio, SGLang, vLLM or a hosted API does none of that.

Options:

1. Run a skills-aware host (Claude Code, Qwen Code, Codex, or similar) connected to your model through its OpenAI-compatible endpoint. Verify compatibility with your exact runner and model.
2. In a basic chat UI without Skills support, paste the contents of `SKILL.md` into the system prompt and supply relevant `references/` text as needed. In that case tool use, automatic discovery, and the bundled scripts are **not automatic**. Prepend one line to the system prompt: "You have no tools in this conversation. The user runs every command and pastes the results; work only from what is pasted." Without it, a local 27B model was measured emitting fabricated tool calls in about 2 of 10 runs; with it, 0 of 10. Allow roughly 4,000 output tokens: the first turn of a full investigation is long, and a 3,000-token cap was still cut off in most runs.

## Example prompts

- "Use reverse engineering to understand why this app produces this output. Give me two hypotheses before testing."
- "Reverse engineer this file format from three synthetic samples. What can actually be verified?"
- "Explain how this household gadget likely works from my photo. Distinguish visible evidence from guesses, and avoid unsafe disassembly."
- "Map the steps and feedback loops in this business workflow, and identify what evidence would confirm the bottleneck."
- "Create a clean-room behavioral specification for this local utility, with reproducible tests."

## Limits and privacy

Reverse engineering is not clairvoyance. The skill helps the agent reason methodically, but it cannot observe unavailable internals or grant access to tools the host does not expose. It instructs the agent to use only authorized resources, keep sensitive data private, and avoid dangerous physical or cybersecurity activities. You are responsible for reviewing agent-suggested commands and results.

## Verification sources

- Agent Skills specification: https://agentskills.io/specification
- Claude Code skills: https://code.claude.com/docs/en/skills
- Qwen Code skills: https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/
- Codex skills: https://learn.chatgpt.com/docs/build-skills

## Versions

- 1.3 (2026-10-29): wording polish from a second Claude Code check: quick-mode length guidance loosened for the functional model; the pre-authorization sentence in `SKILL.md` now covers the helpers too (the practice target's filename stays in the exercises file only: naming it in `SKILL.md` measured 4 of 10 fabricated tool calls on a bare chat lane); the skill-directory paragraph reads correctly after Claude Code substitutes the path; tooling and exercises say plainly that `SKILL_DIR` is a variable you set; published under the MIT licence at https://github.com/emiluzelac/universal-reverse-engineering.
- 1.2 (2026-10-29): fixes from blind test runs on Claude Code and a local Qwen lane: skill-directory wording no longer names a shell variable that does not exist; one playbook plus the always-on safety and reporting references; the bundled example is pre-authorized to run; one hypothesis-ledger and one run-log layout shared by the reporting reference and the template; the exercise no longer hints at the answer; full mode names its deliverable; small targets are excused from empty diagrams; file probe recognises `#!` scripts and plain text; scratch paths are host-neutral.
- 1.1 (2026-10-29): host-neutral wording and install table; scripts addressed through the skill directory instead of the working directory; quick/full mode selector; agent configuration folders excluded from snapshots.
- 1.0 (2026-10-29): first release, written for Qwen Code.
