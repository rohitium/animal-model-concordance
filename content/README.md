# Editing the site

Every sentence on the site lives in this folder, as markdown. Edit these files, rebuild, and the
site changes. You never need to touch Python to change wording, add a section, or reorder a page.

| File | Page |
|---|---|
| `report.md` | the main report at `/` |
| `results.md` | the results browser |
| `pairs.md` | the drug-pair browser |
| `caninisation.md` | program selection — licensing human molecules for dogs and cats |
| `spotcheck.md` | the spot-check page |
| `study.md` | the wrapper around every per-study page |
| `artifacts.md` | the wording *inside* generated tables, charts and browsers |

`artifacts.md` is the one that is not a page. Everything the builder draws — column headers, filter
labels, chart captions, the text inside an expanded table row — takes its words from there, in the
form `key :: text` under a `## section` heading. Edit the text after `::` and leave the key alone.

## Rebuild and preview

```bash
python3 analysis/v04/s1_build_site.py && python3 -m http.server 8811 --directory site/v04_build
```

Then open <http://localhost:8811>. Pushing to `main` deploys whatever is committed.

## Numbers write themselves

Never type a figure the data already knows. Write the token and it is filled in at build time,
correctly formatted, so your prose cannot drift out of step with the corpus.

This table deliberately does **not** list current values. An earlier version did, and the values
went stale within a week while the prose around them stayed right — which is exactly the failure the
tokens exist to prevent. To see what a token currently resolves to, build the site and look.

**The corpus**

| Token | Meaning |
|---|---|
| `{{n_results}}` | results kept after adjudication |
| `{{n_studies}}` | studies those results come from |
| `{{n_distinct_findings}}` | distinct findings, counting rows that share a quote once |
| `{{n_level_a}}` `{{n_level_b}}` `{{n_level_c}}` | results per evidence level |
| `{{n_corresponded}}` `{{n_not_corresponded}}` `{{n_mixed}}` | results by direction |
| `{{n_unresolved}}` | results whose species could not be resolved |
| `{{n_single_reviewer}}` | results adjudicated by the single unblinded reviewer |
| `{{n_extracted}}` | candidate results extracted from full text |
| `{{n_extraction_studies}}` | studies whose full text was read |
| `{{n_eligible}}` | of those, judged eligible at that stage |
| `{{n_limitations}}` | distinct entries in the limitations register |
| `{{built_date}}` | build date |

**Drug pairs**

| Token | Meaning |
|---|---|
| `{{n_pairs}}` | classified dog and cat drug pairs |
| `{{n_human_first}}` | pairs where human approval came before the veterinary evidence |
| `{{n_vet_first}}` | pairs where the veterinary evidence came first |
| `{{median_lag}}` | median years between human approval and veterinary evidence |
| `{{n_lag_pairs}}` | pairs where both dates are known |

**Program selection**

| Token | Meaning |
|---|---|
| `{{n_human_programs}}` `{{n_pet_programs}}` | programs in the two supplied lists |
| `{{n_candidates}}` | candidates presented |
| `{{n_route1}}` `{{n_route2}}` `{{n_route3}}` | candidates per route |
| `{{n_watch}}` | pipeline assets held back for want of an approval |
| `{{n_formulary}}` | route-1 molecules already in routine veterinary use as generics |
| `{{n_occupied}}` | candidates whose mechanism a companion-animal program works |
| `{{n_mech_open}}` | candidates with an open mechanism inside a contested condition |
| `{{n_used_no_programme}}` | candidates used or studied in dogs with no branded program |
| `{{n_nothing_found}}` | candidates returning nothing on any presence check |
| `{{n_unclassified}}` | candidates whose mechanism is not in the curated map |

## Blocks the builder draws

Put one of these on a line by itself and the builder inserts the generated thing. These are the only
parts you cannot write by hand.

| Token | What appears | Page |
|---|---|---|
| `{{figures}}` | a row of headline figures | available, not currently used |
| `{{level_table}}` | results by evidence level | report |
| `{{heatmap}}` | the evidence map | report |
| `{{pairs_strata}}` | the drug-pair strata table with confidence intervals | report |
| `{{q4_tables}}` | the companion-vs-laboratory tables | report |
| `{{recall}}` | the capture–recapture coverage figures | report |
| `{{results_table}}` | the searchable results browser | results |
| `{{pairs_flow}}` | the flow diagram of timing against verdict | pairs |
| `{{pairs_table}}` | the searchable pair browser | pairs |
| `{{cand_figures}}` | a row of headline figures | available, not currently used |
| `{{cand_routes}}` | the route cards | caninisation |
| `{{cand_presence}}` | what the presence checks found | caninisation |
| `{{cand_lag}}` | the human-to-veterinary lag histogram | caninisation |
| `{{cand_areas}}` | condition areas ranked on dog evidence | caninisation |
| `{{cand_crowding}}` | companion-animal programs per indication | caninisation |
| `{{cand_funnel}}` | how the candidate list was cut | caninisation |
| `{{cand_table}}` | the searchable candidate browser | caninisation |
| `{{spotcheck_items}}` | the sampled results | spotcheck |
| `{{study_header}}` `{{study_results}}` | per-study title block and results | study |

## Writing

Ordinary markdown: `**bold**`, `*italic*`, `[link](results.html)`, `-` bullets, `1.` numbered
lists, `##` headings, and tables.

Three callouts:

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

`::: dek` puts a small uppercase eyebrow above the title.

## Sections and the rail

On pages with a left-hand rail, every `##` heading becomes an entry automatically. Add a section and
it appears; reorder them and the rail follows.

Give a heading a stable anchor with `{#id}`, so links from elsewhere keep working:

```
## Dog and cat drug pairs {#pairs}
```

If the heading is too long for the rail, give the rail a shorter label after a pipe:

```
## Companion animals vs laboratory models {#q4|Companion vs laboratory}
```

## The one rule

The site's claim is that every figure on it is traceable to the data, and every statement of absence
names the sources that were searched. Prose that asserts a number the data does not support breaks
that claim more seriously than an ugly sentence does — and prose that says "there is no X" when what
was established is "we did not find X in these sources" breaks it worst of all. If you want to say
something the tokens cannot express, say it and flag it, and the records get checked before it ships.
