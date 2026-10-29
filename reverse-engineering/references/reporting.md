# Reporting and evidence standards

## Source-of-truth priority

Direct measurements and original artifacts > independent repeat tests > authoritative technical documentation > credible secondary explanations > analogy and informed conjecture. This is a working heuristic, not an excuse to ignore contradictory evidence.

## Two tables, not one

A **hypothesis ledger** tracks explanations. A **run log** tracks experiments. Keep both in full mode. A small task may merge them into one short table, but keep the input column.

### Hypothesis ledger

`ID | hypothesis | predicts | would be falsified by | status | confidence`

IDs `H1`, `H2`, … Statuses: `UNTESTED`, `SUPPORTED`, `DISCONFIRMED`, `INCONCLUSIVE`. A supported hypothesis is not necessarily proven or unique. Add a new row when a hypothesis is replaced; do not silently edit the old one.

### Run log

`Run | input or condition | prediction (and which H) | observed | status | source`

IDs `R1`, `R2`, … Write the prediction before the run, then the observation. `source` is the exact command, measurement, file and line, or screenshot. When running programs, record stdout, stderr and exit code separately.

## Evidence matrix fields

`Claim ID | claim | evidence ID/path/line | type (observed/inferred/verified) | alternative | confidence | limitations`

## Validation checklist

- Is the scope named? Are we inspecting the same version/model as the user asked about?
- Does every central claim have an observation or a labeled assumption?
- Were alternative hypotheses considered and potentially falsifying tests defined?
- Are experiment conditions, inputs, outputs, and side effects reproducible?
- Were safety, ownership, privacy, and authorization boundaries respected?
- Are the user's original question and remaining unknowns addressed in ordinary language?

## Example inference

Observed: two sample inputs yield the same output. Inferred: the system may normalize inputs. Alternative: outputs may be cached or truncated. Test: vary only letter case with a new value. This example illustrates why two samples rarely prove an algorithm.

The report layout is `templates/report.md`; scale it down for small tasks.
