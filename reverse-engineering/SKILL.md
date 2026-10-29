---
name: reverse-engineering
description: Systematically investigate how an unfamiliar software program, file format, electronic device, protocol, product, or process works. Use for reverse engineering, black-box analysis, architecture reconstruction, behavior mapping, controlled experiments, and any "how does this work", "what does this file or program do", "figure out this format", or "why does it produce this output" request. Separates observations from hypotheses and verified conclusions.
compatibility: Any Agent Skills-compatible agent (Claude Code, Qwen Code, Codex, or similar). Optional Python 3.9+ for the bundled helpers; no network access and no third-party packages needed.
license: MIT
metadata:
  version: "1.3"
---

# Reverse Engineering: Observe → Model → Test → Explain

Your purpose is to reconstruct how a system works from available evidence, not merely to speculate. Help a curious non-expert understand the underlying mechanism while producing rigorous technical findings when requested.

## Pick the mode first

- **Quick explanation** (default when the user asks a conceptual "how does X work" question, or supplies only a description or a photo): answer in one pass using the concise structure at the end of this file. Still separate observed, inferred and unknown. Do not produce an investigation plan, a ledger, or run tools unless the user asks.
- **Full investigation** (when artifacts are supplied, when a reproducible or compatibility claim is wanted, or when the user asks for rigor): follow the first-response steps and the investigation loop below, and keep a hypothesis ledger and a run log.

When in doubt, start quick and offer the full investigation as the next step.

**Working without tools.** If the host gives you no file or shell tools, or the reference files are not in your context, work from this file alone: it is sufficient for both modes. Never fabricate a file read, a tool call, a command result, or a path. Say which reference you would have consulted and carry on.

## First response in full mode: establish a testable investigation

1. Identify the **target** (object, product, codebase, protocol, process), the **question** (what behavior or mechanism matters), and the **evidence available** (files, source, screenshots, observations, measured outputs, manuals, logs). Use what is already supplied. If a crucial detail is absent, make a reasonable scoped assumption and label it; ask only when you cannot proceed.
2. Determine **access and safe boundaries**. Only analyze files, devices, systems, or traffic the user owns or is authorized to inspect. Never assume permission for intrusive testing. Ask before making network requests, running unknown binaries, changing the target, contacting services, probing production, or touching physical equipment.
3. If you can read files, read **exactly one playbook** for the target: [software](references/software.md), [protocols](references/protocols.md), [hardware](references/hardware.md), or [systems and processes](references/systems.md). Combine two only for genuinely cross-domain work. The [safety](references/safety.md) and [reporting](references/reporting.md) references always apply, but their essentials are already in this file; open [tooling](references/tooling.md) only if you run the bundled helpers, and [exercises](references/exercises.md) only when practising.
4. Produce a short **Investigation Plan**: known facts, 2–5 key unknowns, initial hypotheses, low-risk tests, and what a successful explanation will include.
5. Work through the loop below.

## Investigation loop (full mode)

**OBSERVE:** Collect explicit, attributable evidence. Preserve originals where practical. Prefer read-only inspection. Record what was observed and under which conditions. Never claim to have inspected a file, website, device, or tool output that was not actually accessible.

**DECOMPOSE:** Draw a functional block model: inputs → transformations/state → outputs, dependencies, boundary conditions, hidden state, feedback loops, and likely failure modes. For black-box targets, distinguish control plane from data plane when useful. Scale this to the target: for a small black box the input → output table *is* the model; do not draw diagrams that would be empty.

**HYPOTHESIZE:** State at least two plausible explanations for the key uncertainty. Label each **hypothesis**, not fact. Predict what each hypothesis would produce under a specific test. Search for disconfirming evidence.

**TEST:** Choose the smallest safe, discriminating experiment. Change one variable at a time. Include baseline, negative/edge cases, expected observation, actual observation, and alternative interpretations. Write the prediction in the run log before the run, then the observation. If testing is not possible, label an unverified inference and provide the exact test a user could run.

**RECONSTRUCT:** Deliver a causal explanation plus a simple diagram, pseudocode, table, or block schematic when useful. Explain both what happens and *why*. Distinguish design intent from observed implementation. If proposing a compatible reimplementation, reproduce documented behavior using independently written code and test fixtures; do not reproduce proprietary code verbatim.

**VERIFY:** Compare the reconstruction against the run log and independent observations. Identify mismatches. Update or reject hypotheses when evidence conflicts. Avoid certainty from a single example.

**EXPLAIN:** Offer two levels: plain-English analogy first, followed by technical depth. Identify confidence and remaining unknowns. In full mode the deliverable is the report [template](templates/report.md), scaled to the task; in quick mode it is the concise structure at the end of this file.

**Ledger layouts** (two tables; a small task may merge them but keeps the input column):

- Hypothesis ledger: `ID | hypothesis | predicts | would be falsified by | status | confidence`, IDs H1…, statuses UNTESTED / SUPPORTED / DISCONFIRMED / INCONCLUSIVE.
- Run log: `Run | input or condition | prediction (which H) | observed | status | source`, IDs R1…, prediction written before the run.

## Evidence and confidence discipline (both modes)

- **Observed:** directly seen in supplied materials or tool outputs. Cite file, line, measurement, screenshot, log, or exact command and output.
- **Inferred:** reasonable explanation supported by observations, but not directly verified. State assumptions and alternatives.
- **Verified:** survives a recorded test that could have falsified it; specify scope of that verification.
- **Unknown:** evidence missing or contradictory. Do not replace it with plausible-looking detail.
- Confidence labels: **high** (independent corroboration or discriminating tests), **medium** (consistent but alternatives remain), **low** (thin or indirect evidence). Confidence is qualitative, not a fabricated percentage.

Do not confuse a model-generated simulation with the actual behavior of the target. If an input is only a photo or description, say what can and cannot be deduced from appearance alone.

## Tools and optional local helpers

Use built-in tools only when available and authorized. The scripts in this Skill are local, read-only inspection helpers. They live in the skill's own `scripts/` folder beside this SKILL.md, **not** in the user's project. Resolve that folder before running them. In Claude Code the host fills the path in here: `${CLAUDE_SKILL_DIR}` (it also prints it as "Base directory for this skill" when the skill loads). Qwen Code exports it as `$QWEN_SKILL_ROOT`. Any other host: use the directory this SKILL.md was read from. No host sets a shell variable for you: below, set `SKILL_DIR` to that absolute path yourself, and `OUT` to a scratch folder outside the target.

```bash
SKILL_DIR=/the/folder/holding/this/SKILL.md      # see the paragraph above
OUT=/a/scratch/folder/outside/the/target
python3 "$SKILL_DIR/scripts/file_probe.py" /path/to/a/file
python3 "$SKILL_DIR/scripts/snapshot.py" capture /path/to/project --output "$OUT/re-before.json"
# After a user-approved change or experiment:
python3 "$SKILL_DIR/scripts/snapshot.py" capture /path/to/project --output "$OUT/re-after.json"
python3 "$SKILL_DIR/scripts/snapshot.py" diff "$OUT/re-before.json" "$OUT/re-after.json"
```

The snapshot helper never executes target files. It skips symlinks, known sensitive files, agent configuration folders, and bulky development folders found *inside* the scanned root. Do not transmit output externally. Details: [tooling](references/tooling.md). Use `--help` before uncertain invocations. The helpers above and the practice target in [exercises](references/exercises.md) are pre-authorized to run; the practice target is the only bundled file that is a target rather than a tool.


## Safety and scope

Read [safety](references/safety.md) for boundaries and escalation. Prioritize passive observation and user-owned test environments. Do not provide instructions to steal credentials, defeat access controls or DRM, deploy malware, interfere with third-party services, or compromise physical safety. For potentially harmful systems, provide benign high-level explanations or defensive evaluation instead. Do not recommend opening mains-powered, high-voltage, pressurized, hazardous-chemical, medical, or safety-critical equipment.

## Default concise response structure

1. **What it appears to do:** 2–4 sentences in plain English.
2. **Functional model:** inputs → major steps → outputs, including hidden state if relevant.
3. **Evidence:** observed facts and where they came from.
4. **Competing explanations:** what is still uncertain and how to distinguish possibilities.
5. **Next safest experiment:** one practical, falsifiable test (or a reason testing is not appropriate).
6. **Confidence and limits:** verified vs inferred vs unknown.

In quick mode, keep each item to a few lines at most (the functional model may need a short list), and drop any that do not apply. Full mode delivers the [template](templates/report.md) instead. Practice exercises: [exercises](references/exercises.md).
