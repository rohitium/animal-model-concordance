# Editing the site

Every sentence on the site lives in this folder, as markdown. Edit these files, rebuild, and the
site changes. You never need to touch Python to change wording, add a section, or reorder the
report.

| File | Page |
|---|---|
| `report.md` | the main report at `/` |
| `results.md` | the results browser |
| `pairs.md` | the drug-pair browser |
| `spotcheck.md` | the spot-check page |
| `study.md` | the wrapper around every one of the 406 study pages |

## Rebuild and preview

```bash
python3 analysis/v04/s1_build_site.py
python3 -m http.server 8811 --directory site/v04_build
```

Then open <http://localhost:8811>. Pushing to `main` deploys whatever is committed.

## Numbers write themselves

Never type a figure that the data already knows. Write the token and it is filled in at build time,
correctly formatted, so your prose cannot drift out of step with the corpus.

| Token | Currently | Meaning |
|---|---|---|
| `{{n_results}}` | 1,494 | results kept after adjudication |
| `{{n_studies}}` | 406 | studies those results come from |
| `{{n_level_a}}` `{{n_level_b}}` `{{n_level_c}}` | 422 / 107 / 965 | results per evidence level |
| `{{n_corresponded}}` | 1,032 | results where the animal finding matched |
| `{{n_not_corresponded}}` | 348 | results where it did not |
| `{{n_mixed}}` | 110 | mixed results |
| `{{n_unresolved}}` | 894 | results whose species could not be resolved |
| `{{n_pairs}}` | 803 | classified dog and cat drug pairs |
| `{{n_single_reviewer}}` | 769 | results adjudicated by the single unblinded reviewer |
| `{{n_extracted}}` | 3,562 | candidate results extracted from full text |
| `{{n_extraction_studies}}` | 577 | studies whose full text was read |
| `{{n_eligible}}` | 570 | of those, judged eligible at that stage |
| `{{n_limitations}}` | 88 | distinct entries in the limitations register |
| `{{built_date}}` | today | build date |

Figures that come from the analysis reports rather than from the record set — the 34% / 10%
verification rates, the 33% coverage estimate, the Q4 counts, the 79% reader audit — are written out
as text. They change only when those analyses are re-run, and the report tables next to them carry
the same numbers.

## Blocks the builder draws

Put one of these on a line by itself and the builder inserts the generated thing. They are the only
parts you cannot write by hand.

| Token | What appears |
|---|---|
| `{{figures}}` | the row of headline figures |
| `{{level_table}}` | results by evidence level |
| `{{heatmap}}` | the evidence map |
| `{{pairs_strata}}` | the drug-pair strata table with confidence intervals |
| `{{q4_tables}}` | the companion-vs-laboratory tables |
| `{{recall}}` | the capture–recapture coverage figures |
| `{{results_table}}` `{{pairs_table}}` | the searchable browsers |
| `{{spotcheck_items}}` | the 40 sampled results |
| `{{study_header}}` `{{study_results}}` | per-study title block and results (in `study.md` only) |

## Writing

Ordinary markdown: `**bold**`, `*italic*`, `[link](results.html)`, `-` bullets, `1.` numbered
lists, `##` headings, and tables.

Three callouts, for the three jobs the site actually has:

```
::: lede
The standfirst under the title.
:::

::: note Why there is no headline percentage
A boxed caution. The words after "note" become its heading.
:::

::: small
Fine print — caveats, definitions, provenance.
:::
```

## Sections and the rail

On the report, every `##` heading becomes an entry in the left-hand rail automatically. Add a
section and it appears; reorder them and the rail follows.

Give a heading a stable anchor with `{#id}`, so links from elsewhere keep working:

```
## Dog and cat drug pairs {#pairs}
```

If the heading is too long for the rail, give the rail a shorter label after a pipe:

```
## Companion animals vs laboratory models {#q4|Companion vs laboratory}
```

## The one rule

The site's claim is that every figure on it is traceable to the data. Prose that asserts a number
the data does not support breaks that claim more seriously than an ugly sentence does. If you want
to say something the tokens cannot express, say it and flag it to me, and I will check whether the
records actually support it before it ships.
