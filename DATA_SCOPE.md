# Data scope and privacy boundary

## Included

- Experiment protocols.
- Rule drafts and conflict checks.
- Human review score summaries.
- Machine-gate score summaries.
- Final experiment reports.
- Case-level descriptions used in those documents.
- Full prompts and resource snapshots.
- Model outputs and thinking traces.
- Runtime stdout/stderr and inference metadata.
- Tokenizer audit records.
- Blind-review inputs and sealed mappings.
- Failed, interrupted, and incorrect extraction attempts.
- Immutable archive ZIP files.

## Excluded

- Model binaries.
- Credentials, tokens, cookies, or private keys.
- Any material that could not be verified as safe for public disclosure.

## Reason

The purpose is to publish the complete test evidence needed to inspect how each conclusion was reached. Model binaries are excluded because they are large and separately versioned by SHA-256.

## Risk statement

The reports and test records may contain short excerpts and summaries of a test requirement. They do not claim that the underlying business case is public or that the SOP conclusions generalize beyond the tested model, case, seeds, and runtime.
