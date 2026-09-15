# Q4: companion animals vs laboratory models, within drug (draft)

Built 2026-09-14 by `analysis/v04/d5_lab_models.py`.

- primary pairs with a classifiable human side: 343
- laboratory side (primary rule): {'mixed': 41, 'indeterminate': 88, 'positive': 205, 'negative': 9}
- laboratory side (unanimous rule): {'mixed': 124, 'indeterminate': 88, 'positive': 124, 'negative': 7}

## primary rule: laboratory side positive/negative when at least 75% of studies agree

- pairs where companion, laboratory and human sides are all positive or negative: 108

| | laboratory concordant | laboratory discordant |
|---|---|---|
| **companion concordant** | 86 | 4 |
| **companion discordant** | 14 | 4 |

- companion-animal concordance: 90/108 = 83%; laboratory-model concordance: 100/108 = 93%
- pairs where only one agreed with humans: 18; companion animals were the one in 4 (22%, exact 95% CI 6%–48%)

**F1 statement:** where the two disagreed, laboratory models matched the human outcome more often than companion animals.

## sensitivity: laboratory side positive/negative only when every study agrees

- pairs where companion, laboratory and human sides are all positive or negative: 65

| | laboratory concordant | laboratory discordant |
|---|---|---|
| **companion concordant** | 54 | 1 |
| **companion discordant** | 7 | 3 |

- companion-animal concordance: 55/65 = 85%; laboratory-model concordance: 61/65 = 94%
- pairs where only one agreed with humans: 8; companion animals were the one in 1 (12%, exact 95% CI 0%–53%)

**F1 statement:** concordance with human outcomes did not differ detectably between companion animals with naturally occurring disease and laboratory models of the same drug and condition.

## Breakdown (primary rule): where the comparison is informative

| subset | pairs | companion animals matched humans | laboratory models matched humans |
|---|---|---|---|
| human result positive | 104 | 89/104 (86%) | 100/104 (96%) |
| human result negative | 4 | 1/4 (25%) | 0/4 (0%) |
| drug approved in humans before the veterinary evidence | 90 | 78/90 (87%) | 84/90 (93%) |
| drug approved in humans after the veterinary evidence | 2 | 2/2 (100%) | 2/2 (100%) |
| no US human approval | 16 | 10/16 (62%) | 14/16 (88%) |

Laboratory sides are almost uniformly positive, so agreement on human-positive drugs is expected whatever the model's predictive value. Only the human-negative row tests prediction of failure.
Laboratory reader: gemini-2.5-flash, audited 79% correct (42/53 reads; q4_reader_audit.md).


Caveat: laboratory efficacy literature is biased towards positive results, which inflates laboratory agreement whenever the human result is positive; laboratory sides are read from abstracts.
