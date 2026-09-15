# Artifact text

The wording *inside* the generated tables, figures and browsers. The numbers come from the data;
every word around them is here.

Format: `## section`, then `key :: text`. Leave the keys alone, edit the text after `::`. Tokens
like `{{n_results}}` work here exactly as they do in the page files; `{{max}}` in the heatmap
legend is the largest cell count.

## figures

n_results :: results kept after checking
n_studies :: studies
n_level_a :: level A · intervention outcomes
n_level_b :: level B · toxicity and safety
n_level_c :: level C · disease biology

## level_table

caption :: Results by evidence level, and how they came out.
level :: Evidence level
studies :: studies
results :: results
corresponded :: corresponded
did_not :: did not
mixed :: mixed
label_a :: intervention outcomes
label_b :: toxicity and safety
label_c :: disease biology

## heatmap

row_header :: disease area
total :: all
legend_low :: fewer studies
legend_high :: more ({{max}} at most)
legend_note :: superscript = highest evidence level in the cell · click a cell to see those results
cell_title :: {{area}} · {{species}}: {{n}} studies, highest evidence level {{level}}

## directions

animal-corresponded :: corresponded
animal-did-not-correspond :: did not correspond
mixed :: mixed
not-applicable :: not applicable

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
