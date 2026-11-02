# FormSy SOP Improvement Data

This repository publishes experimental design, evaluation summaries, rule drafts, and conclusions used to improve the FormSy SOP process.

It intentionally does **not** publish the complete prompt corpus, raw model outputs, runtime logs, model files, local absolute paths, credentials, or private project materials. Those artifacts remain in the local evidence archive. This repository records what was tested and what the measured outcomes were, not a full reproducibility bundle.

## Scope

The current release covers the 2026-11-02 design-review ablation series:

1. Baseline / equal-length neutral material / `formsy-sop` `origin/main` material.
2. Direct append of draft rule additions.
3. Rule additions integrated near related PC/TC rules.
4. Short fact card, machine gate, and one-round targeted revision.

## Directory

- `reports/` — final experiment reports.
- `protocols/` — frozen experiment protocol, rule drafts, and conflict checks.
- `summaries/` — machine-readable scoring and gate summaries.

## Evidence boundary

- These are offline static design evaluations for one real requirement case and three seeds per arm.
- They do not prove code correctness, deployment readiness, end-user acceptance, or effectiveness for every domain.
- Reports retain failed and interrupted runs as evidence; they do not silently replace or re-rank samples.

## Provenance

Source SOP revision used for the main comparison:

- Repository: `https://github.com/FormSyAI/formsy-sop`
- Branch: `origin/main`
- Commit: `fb65db5c91e33e7197af146265979d84e5eba674`
- Date observed: 2026-11-02

## License

No license has been selected yet. All rights are reserved until an explicit license is added.
