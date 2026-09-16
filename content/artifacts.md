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
