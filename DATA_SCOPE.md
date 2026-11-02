# Data scope and privacy boundary

## Included

- Experiment protocols.
- Rule drafts and conflict checks.
- Human review score summaries.
- Machine-gate score summaries.
- Final experiment reports.
- Case-level descriptions used in those documents.

## Excluded

- Full prompts.
- Raw model outputs and thinking traces.
- Runtime stdout/stderr logs.
- Model binaries and tokenizer outputs.
- Local user paths in raw form.
- Credentials, tokens, cookies, or private keys.
- Any material that could not be verified as safe for public disclosure.

## Reason

The purpose is to document method, measured outcomes, and rule improvements without publishing potentially reusable customer/business content or a large raw inference corpus. Raw evidence remains in the local archive and can be reviewed separately under an authorized environment.

## Risk statement

The reports may contain short excerpts and summaries of a test requirement. They do not claim that the underlying business case is public or that the SOP conclusions generalize beyond the tested model, case, seeds, and runtime.
