# Self-test exercises

## 1: Black-box number machine (offline, beginner)

The bundled `examples/number_machine.py` is a harmless practice target and is pre-authorized to run. `SKILL_DIR` is a shell variable you set yourself to the folder holding `SKILL.md`; see [tooling](tooling.md) for how to find that folder.

```bash
python3 "$SKILL_DIR/examples/number_machine.py" 5
python3 "$SKILL_DIR/examples/number_machine.py" 8
python3 "$SKILL_DIR/examples/number_machine.py" -2
```

Treat it as an oracle: run it and observe, but do not read its source during the blind phase. Find the rule that maps input to output. Predict before every run, keep the hypothesis ledger and run log from [reporting](reporting.md), and choose inputs that split your live hypotheses rather than confirm them. Stop when your rule has predicted at least ten fresh inputs of your own choosing, including edge cases, without a miss. Then read the source and record exactly where the model was right, wrong, or undecidable from outside.

## 2: Folder transformation (beginner/intermediate)

Use `snapshot.py capture` on a disposable test folder, manually change one file in that folder, capture again, and compare. Explain precisely what the before/after evidence supports and what it does not support. Do not mutate a valuable repository just for this exercise.

## 3: Everyday device (no electronics needed)

Provide a photo or description of a hand-operated stapler. Ask for a functional block diagram, alternate hypotheses for the feeding mechanism, and safe external observations that could distinguish them. Explain why appearance alone does not prove the internal mechanism.

## Success criteria

- The agent separates observed facts, inferences, and unknowns.
- It predicts results before running the next test.
- It proposes at least one discriminating experiment.
- It neither invents tool results nor makes risky or unauthorized suggestions.
- Its final explanation makes sense to someone who is simply curious how things work.
