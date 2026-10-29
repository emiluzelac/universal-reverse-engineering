# Protocol and connected-system investigation

This playbook applies to APIs, message formats, integration behavior, and network protocols in user-controlled or explicitly authorized environments.

## Passive starting point

Collect existing documentation, request/response examples with secrets redacted, schemas, exported captures, endpoint descriptions, and logs. Do not collect credentials or intercept unrelated traffic. Do not replay requests to a production service without permission.

## Model the protocol

1. Define actors and roles, entry/exit points, framing, and transport (if known).
2. Separate handshake, authentication *as a conceptual phase*, normal operations, errors, retries, shutdown, and recovery. Never attempt to bypass authentication.
3. Construct a state machine: states, inputs/messages, state transitions, timeouts, and responses.
4. Map each observed field to potential function; mark unknown fields explicitly. Avoid inferring a complete protocol from one trace.
5. If authorized to test in staging, vary one benign parameter per request and record differential responses. Use bounded rates and synthetic data only.
6. Investigate idempotence, message ordering, encoding, checksums, pagination, version negotiation, and failure behavior where relevant.

## Report

Provide a message schema with observed and inferred fields separately, a state transition table, a sequence diagram in text or Mermaid, and a list of falsifiable test cases. Avoid claiming compatibility until a separate known implementation passes the test matrix.
