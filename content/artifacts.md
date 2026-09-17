# Artifact text

The wording *inside* the generated tables, figures and browsers. The numbers come from the data;
every word around them is here.

Format: `## section`, then `key :: text`. Leave the keys alone, edit the text after `::`. Tokens
like `{{n_results}}` work here exactly as they do in the page files; `{{max}}` in the heatmap
legend is the largest cell count.

## figures

n_results :: Results
n_studies :: Studies
n_level_a :: Intervention outcomes (Evidence Level A)
n_level_b :: Toxicity and safety (Evidence Level B)
n_level_c :: Disease biology (Evidence Level C)

## level_table

caption :: Results
level :: Evidence level
studies :: Studies
results :: Results
corresponded :: Concordant
did_not :: Discordant
mixed :: Mixed
label_a :: Intervention outcomes
label_b :: Toxicity and safety
label_c :: Disease biology

## heatmap

row_header :: Disease area
total :: All
legend_low :: Fewer studies
legend_high :: More ({{max}} at most)
legend_note :: Superscript = highest evidence level in the cell (click a cell to see those results)
cell_title :: {{area}} · {{species}}: {{n}} studies, highest evidence level {{level}}

## directions

animal-corresponded :: Concordant
animal-did-not-correspond :: Discordant
mixed :: Mixed
not-applicable :: Not applicable

## results_table

placeholder :: Search findings, studies, species…
empty :: Nothing matches those filters.
reset :: Reset
noun :: results
col_st :: Finding
col_lv :: Level
col_sp :: Species
col_ar :: Disease area
col_dr :: Direction
col_vn :: Value
col_ti :: Study
filter_lv :: Level
filter_sp :: Species
filter_ar :: Disease area
filter_dr :: Direction

## pairs_table

placeholder :: Search by drug, indication or evidence…
empty :: Nothing matches those filters.
reset :: Reset
noun :: pairs
hint :: Click a row to see the evidence behind the verdict.
col_ag :: Drug
col_sp :: Species
col_ind :: Veterinary indication
col_vd :: Verdict
col_vet :: Veterinary
col_hu :: Human
col_ty :: Type
col_ti :: Timing
filter_vd :: Verdict
filter_ar :: Condition area
filter_ev :: Human evidence
filter_sp :: Species
filter_ty :: Type
filter_ti :: Timing
detail_vet :: What the veterinary evidence showed
detail_human :: What the human evidence showed
detail_caveats :: Caveats
detail_vet_records :: Veterinary studies behind this verdict
detail_human_records :: Human evidence cited
detail_none :: No human evidence was retrieved, so the pair is indeterminate, not discordant.
detail_toplevel :: Strongest human evidence found
ev_us-approval :: US label indication
ev_phase-3-or-meta-analysis :: Phase 3 trial or meta-analysis
ev_phase-2 :: Phase 2 trial
ev_earlier :: Earlier-phase or observational
ev_none :: No human evidence retrieved
ev_note :: A US label means the FDA reviewed controlled trials.

## caninisation

fig_candidates :: Candidates
fig_route1 :: Approved, mechanism unclaimed in dogs or cats
fig_route2 :: Approved, mechanism already worked
fig_route3 :: Shelved for a verified non-clinical reason
fig_watch :: Pipeline watch list
lag_caption :: Years from human approval to the veterinary evidence, for the 499 pairs with both dates.
lag_note :: Bars are drugs veterinary medicine took decades to adopt.
route1_name :: Route 1 · Approved, mechanism unclaimed in dogs or cats
route1_desc :: Approved in humans. No companion-animal product works this mechanism.
route2_name :: Route 2 · Approved, mechanism already worked
route2_desc :: Approved in humans, but a companion-animal product already works this mechanism.
route3_name :: Route 3 · Shelved for a verified non-clinical reason
route3_desc :: Stopped for supply, portfolio or corporate reasons.
watch_name :: Held back · Human pipeline, not yet approved
watch_desc :: Phase 2 and Phase 3 assets, still active. No approval yet.
areas_conc :: dog results corresponded
areas_levela :: are intervention outcomes
areas_studies :: studies
areas_cands :: candidates
crowding_caption :: Companion-animal programs per indication
noun :: molecules
placeholder :: Search by molecule, target, company or indication…
empty :: Nothing matches those filters.
reset :: Reset
col_drug :: Molecule
col_target :: Target
col_area :: Condition area
col_route :: Route
col_stage :: Human stage
col_comp :: Companion-animal programs
filter_area :: Condition area
filter_route :: Route
filter_stage :: Human stage
col_ind :: Human indication
detail_presence :: What is known about companion-animal presence
detail_mechanism :: Mechanism in companion animals
detail_mechanism_none :: No companion-animal program works this mechanism.
detail_condition :: Corresponding condition in dogs or cats
detail_condition_none :: No corresponding companion-animal condition was mapped for this indication.
detail_patents :: Patent filings on this mechanism in companion animals
detail_halted :: Halted or written-off companion-animal programs on this mechanism
detail_vetlit :: Veterinary literature (PubMed)
detail_vetlit_none :: No veterinary publications found under this molecule's name.
detail_corpus :: This review's own drug-pair records
detail_notchecked :: No registry of approved veterinary drugs is machine-readable. A drug approved for dogs outside our list shows as not found (for now).
pairsflow_caption :: Which species got there first, and how the evidence came out.
pairsflow_note :: Most pairs are human medicines adopted into veterinary practice later.
detail_ind :: Human indication
detail_ev :: Dog evidence for this condition area
detail_comp :: Companion-animal programs on this target
detail_comp_none :: No program targets this in dogs or cats.
detail_safety :: Species safety caution
detail_precedent :: Class precedent in companion animals
detail_disc :: Why the human program stopped
detail_formulary :: Already in routine veterinary use as a generic.
detail_vague :: The human indication is too general to place a specific companion-animal tumor type.
detail_source :: Program source

## q4

matrix_caption :: Where companion animals and laboratory models agreed with the human outcome, across the {n} pairs with a clear answer on all three sides
comp_yes :: Companion matched
comp_no :: Companion did not
lab_yes :: Laboratory matched
lab_no :: Laboratory did not
rate_comp :: companion animals matched humans
rate_lab :: laboratory models matched humans
rate_disc :: pairs where only one agreed
disc_note :: Of those, companion animals were right in {b} ({pct}, 95% CI {lo}–{hi}).
breakdown_caption :: Where the comparison is informative
col_subset :: Subset
col_pairs :: Pairs
col_comp :: Companion matched
col_lab :: Laboratory matched
tests :: tests prediction
sensitivity :: Counting a laboratory side only when every study agrees: {n} pairs, companion {c}, laboratory {l}. {st}
reader :: Laboratory side read from abstracts by

## tables

rows :: Rows
all :: All

## study

pubmed :: PubMed
doi :: DOI
openalex :: OpenAlex record

## strata

definition :: Concordance counts only pairs that could be called either way. Mixed and indeterminate pairs are shown but excluded from the percentage.
of :: of {c} that could be called
pairs :: pairs
concordant :: Concordant
discordant :: Discordant
mixed :: Mixed
indeterminate :: Indeterminate
reliability :: A second model re-judged {p} random primary pairs blind: {a} agreement, Cohen's kappa {k}.
