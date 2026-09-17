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
hint :: Click any row to see the evidence behind the verdict, with links to every study and label it rests on.
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
detail_none :: No human evidence was retrieved for this drug and indication, which is why the pair is indeterminate rather than discordant.
detail_toplevel :: Strongest human evidence found
ev_us-approval :: US label indication
ev_phase-3-or-meta-analysis :: Phase 3 trial or meta-analysis
ev_phase-2 :: Phase 2 trial
ev_earlier :: Earlier-phase or observational
ev_none :: No human evidence retrieved
ev_note :: A US label means the FDA reviewed adequate and well-controlled trials, so it is strong evidence. It is also only ever positive: a label exists because the drug worked. Pairs resting on a label can therefore disagree in one direction only.

## caninisation

fig_candidates :: Candidates
fig_route1 :: Approved, mechanism unclaimed in dogs or cats
fig_route2 :: Approved, mechanism already worked
fig_route3 :: Shelved for a verified non-clinical reason
fig_watch :: Pipeline watch list
lag_caption :: Years between human approval and the veterinary evidence, for the 499 pairs where both dates are known
lag_before :: Veterinary evidence came first
lag_note :: Each bar counts drug-and-indication pairs. Bars to the right are drugs veterinary medicine took decades to adopt.
routes_caption :: How each candidate qualifies
route1_name :: Route 1 · Approved, mechanism unclaimed in dogs or cats
route1_desc :: Both legs of human evidence established by the approval itself, and no branded companion-animal program works this mechanism. That is not the same as untried in dogs — see what each of the four presence checks found, per molecule, in the table below.
route2_name :: Route 2 · Approved, mechanism already worked
route2_desc :: The same evidence, but a companion-animal program already works this mechanism. Crowding is market validation, and the incumbents are named for each.
route3_name :: Route 3 · Shelved for a verified non-clinical reason
route3_desc :: Stopped for supply, portfolio or corporate reasons with clinical performance not the stated cause, verified by reading the source rather than the headline.
watch_name :: Held back · Human pipeline, not yet approved
watch_desc :: Phase 2 and Phase 3 assets still active. Efficacy is not yet established, so they are a watch list rather than candidates.
areas_caption :: Condition areas ranked on the review's dog evidence
areas_conc :: dog results corresponded
areas_levela :: are intervention outcomes
areas_studies :: studies
areas_cands :: candidates
crowding_caption :: Companion-animal programs per indication, from the supplied program list
crowding_note :: The most crowded indications are the validated ones. An entrant needs a better asset, not an empty field.
funnel_caption :: From supplied programs to presented candidates
table_caption :: Every presented candidate
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
detail_mechanism_none :: No companion-animal program in the supplied list works this mechanism.
detail_condition :: Corresponding condition in dogs or cats
detail_condition_none :: No corresponding companion-animal condition was mapped for this indication.
detail_patents :: Patent filings on this mechanism in companion animals
detail_halted :: Halted or written-off companion-animal programs on this mechanism
detail_vetlit :: Veterinary literature (PubMed)
detail_vetlit_none :: No veterinary publications found under this molecule's name.
detail_corpus :: This review's own drug-pair records
detail_notchecked :: Not checked: no approved-animal-drug registry is machine-readable, so a drug approved for dogs or cats outside the supplied list would not appear here. Absence of a finding is not evidence of absence.
sankey_caption :: From supplied human programs to candidates
sankey_note :: Width is proportional to the number of programs. Every branch that leaves the flow is an exclusion the page names.
pairsflow_caption :: How the classified drug pairs divide, by which species got there first and how the evidence came out
pairsflow_note :: Most pairs are human medicines adopted into veterinary practice later, so agreement mostly records adoption rather than prediction.
levelflow_caption :: Results by evidence level and how the animal finding came out
detail_ind :: Human indication
detail_ev :: Dog evidence for this condition area
detail_comp :: Companion-animal programs on this target
detail_comp_none :: No program in the supplied list targets this in dogs or cats.
detail_safety :: Species safety caution
detail_precedent :: Class precedent in companion animals
detail_disc :: Why the human program stopped
detail_formulary :: Already in routine veterinary use as a generic, so the absence of a company program does not mean an open field.
detail_vague :: The human indication is too general to place a specific companion-animal tumor type.
detail_source :: Program source
