# Animal Model Concordance with Human Clinical Outcomes

A systematic review quantifying how predictive animal models are of human clinical outcomes.

**Status:** Phase 1 (scoping search). No conclusions formed. See [PLAN.md](PLAN.md) for the protocol.

Four evidence arms, analysed separately and never pooled:

| Arm | Index test | Reference standard |
|---|---|---|
| 1 — Efficacy | Induced/engineered laboratory disease model | Human trial efficacy |
| 2 — Safety pharmacology & adverse events | ICH S7A/S7B acute functional effects | Human AEs, QT, withdrawals |
| 3 — Toxicology | GLP repeat-dose, genotox, carcinogenicity, reprotox | Human target-organ toxicity |
| 4 — Veterinary / spontaneous disease | Naturally occurring disease in client-owned animals | Corresponding human result |

Every claim in this repository resolves to a PMID, DOI, NCT, or regulatory document ID.

## Layout
- `PLAN.md` — protocol (current: v0.3)
- `protocol/` — search strings with run dates and hit counts, PRISMA flow, amendments, archived protocol versions
- `data/` — search exports, screening decisions, extracted records, JSON database
- `analysis/` — re-runnable analysis code
- `figures/`, `site/`, `docs/`, `references/`
