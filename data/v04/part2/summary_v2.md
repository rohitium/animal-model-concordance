# Dog and cat drug pairs: summary v2 (after quality pass)

Built 2026-09-14 by `analysis/v04/d4_quality.py`.

Concordance = concordant / (concordant + discordant), exact 95% CI. Mixed and indeterminate are counted, never dropped.

| stratum | pairs | concordant | discordant | mixed | indeterminate | concordance (95% CI) |
|---|---|---|---|---|---|---|
| Primary (drugs, biologics, vaccines, cell/gene therapies) | 586 | 152 | 33 | 62 | 339 | 82% (76%–87%) |
| Primary: disease-modifying use | 407 | 96 | 20 | 39 | 252 | 83% (75%–89%) |
| Primary: symptomatic or preventive use | 179 | 56 | 13 | 23 | 87 | 81% (70%–90%) |
| Primary: human approval before the veterinary evidence | 440 | 124 | 25 | 46 | 245 | 83% (76%–89%) |
| Primary: human approval after the veterinary evidence | 19 | 7 | 0 | 2 | 10 | 100% (59%–100%) |
| Primary: no US human approval | 127 | 21 | 8 | 14 | 84 | 72% (53%–87%) |
| Primary, disease-modifying: dog | 316 | 65 | 14 | 27 | 210 | 82% (72%–90%) |
| Primary, disease-modifying: cat | 63 | 19 | 5 | 7 | 32 | 79% (58%–93%) |
| Excluded from primary: supplements, minerals, devices, regimens, non-treatments | 201 | 38 | 14 | 46 | 103 | 73% (59%–84%) |
| Class analogues (separate) | 15 | 3 | 1 | 1 | 10 | 75% (19%–99%) |

**Label reliability (blind re-judgement by google/gemini-2.5-pro, 40 random primary pairs):** agreement 88%, Cohen's kappa 0.764.

Confusion (original → second judge): concordant→concordant: 10; concordant→indeterminate: 2; discordant→discordant: 1; discordant→mixed: 1; indeterminate→indeterminate: 23; indeterminate→mixed: 1; mixed→indeterminate: 1; mixed→mixed: 1

Treatment types among classified pairs: {'small-molecule-drug': 559, 'biologic': 34, 'dietary-supplement': 81, 'mineral-or-element': 33, 'procedure-or-regimen': 48, 'cell-or-gene-therapy': 9, 'device-or-material': 23, 'not-a-treatment': 16}

**Not yet produced:** Q4 (within-drug comparison with laboratory models, protocol §7.6); F1 cannot be stated yet.
