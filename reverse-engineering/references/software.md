# Software and file-format reverse engineering

Use this playbook for source repositories, applications, libraries, binaries, local files, and data structures.

## Discovery (passive first)

1. Confirm the target path and user authorization. Do not execute an unfamiliar binary or run installation hooks as a first step.
2. Inventory architecture: README, manifest files, directory tree, file types, entry points, modules, exported interfaces, data schema, configuration, tests. Never print environment secrets or API keys.
3. Identify the primary behavior to reproduce/explain. Draw its dataflow from trigger or request to persistent state and external effects.
4. Trace a *single* representative input to its output; annotate actual functions and file/line locations. If code is unavailable, treat the program as a black box and define testable hypotheses.
5. Build a dependency and trust-boundary diagram. Separate first-party logic, third-party dependencies, operating system facilities, and remote services.
6. Scale the inventory to the target. For a small black box, the input/output table *is* the architecture and the dependency picture is one line; do not produce diagrams that would be empty.

## Tests and reconstruction

- Prefer supplied tests, fixture files, synthetic test inputs, and an isolated user-approved sandbox.
- For black-box interfaces, construct an input/output table: ordinary, null/empty, boundary, malformed, duplicate, repeated, and state-dependent inputs.
- For data formats, determine header, offsets, endianness, field types, length encoding, framing, checksums, and versioning. Verify with at least two independently varying samples.
- For algorithms, consider transformation order, normalization, rounding, integer overflow, caching, non-determinism, randomness, and error semantics.
- For web apps, investigate routing, API contracts, database reads/writes, caching, and rendering separately. Do not probe another party's production APIs without permission.
- For binaries, use safe, non-executing metadata inspection when permitted. Discuss disassembly only in a legitimate software-interoperability, debugging, preservation, or defensive context. Never provide credential-extraction, control-bypass, or weaponization workflows.

## Deliverables

- Architecture and call/dataflow diagram (when the target has more than one component).
- Behavioral specification with known inputs, outputs, state transitions, and error cases.
- Evidence matrix linking every consequential conclusion to an observation.
- Optional clean-room implementation plan with tests. A compatibility claim requires independent validation.

## Useful challenge questions

- What must be true immediately before this output can occur?
- Which variable could distinguish two competing explanations?
- Is this behavior implemented locally, by a dependency, or by a remote service?
- Can two inputs produce identical output but different hidden state?
- What observed behavior would falsify the current model?
