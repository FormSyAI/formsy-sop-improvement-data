# FormSy SOP Improvement Data

This repository publishes experiment reports, protocols, rule drafts, evaluation summaries, and complete test data used to improve the FormSy SOP process.

It intentionally does **not** publish model binaries, credentials, tokens, cookies, private keys, or unrelated private project material. Full prompts, model outputs, runtime logs, tokenizer records, gate outputs, and review records are included under `data/` as test evidence. Some command metadata contains local absolute paths because these are experiment provenance; no sensitive credential values were found.

## Scope

The current release covers the 2026-11-02 design-review ablation series:

1. Baseline / equal-length neutral material / `formsy-sop` `origin/main` material.
2. Direct append of draft rule additions.
3. Rule additions integrated near related PC/TC rules.
4. Short fact card, machine gate, and one-round targeted revision.

## Report index

- [Main three-arm ablation](reports/20261102-main-ablation-report.md): Baseline / neutral long material / `origin/main` SOP.
- [Rule additions v0.1](reports/20261102-rules-v01-append-report.md): append the full rule draft as an additional resource.
- [Rule additions v0.2](reports/20261102-rules-v02-integrated-report.md): place each rule near the related PC/TC rule.
- [Fact card + machine gate + revision](reports/20261102-factcard-gate-revision-report.md): short fact-card generation, machine gate, and one targeted revision round.

## Directory

- `reports/` — final experiment reports.
- `protocols/` — frozen experiment protocol, rule drafts, and conflict checks.
- `summaries/` — machine-readable scoring and gate summaries.
- `data/` — complete experiment materials, prompts, resource snapshots, runtime records, outputs, review records, gate records, and archive ZIP files.

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
