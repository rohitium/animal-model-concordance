"""v4: multi-strand design. No single string achieves both sensitivity and precision
for this question, because the literature has no consistent vocabulary. Instead:
a union of narrow, individually-precise strands. Recall is measured on the union."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries

PROX = ['"animal human concordance"[tiab:~15]','"animal clinical concordance"[tiab:~15]',
 '"animal human predict"[tiab:~10]','"animal model predict human"[tiab:~10]',
 '"animal patient predict"[tiab:~12]','"preclinical clinical translation"[tiab:~10]',
 '"preclinical clinical concordance"[tiab:~12]','"preclinical clinical predict"[tiab:~10]',
 '"animal studies clinical trials"[tiab:~12]','"animal experiments clinical trials"[tiab:~12]',
 '"mouse human translate"[tiab:~10]','"species concordance"[tiab:~8]',
 '"translation animals humans"[tiab:~10]','"animals humans extrapolation"[tiab:~12]',
 '"animal model validity"[tiab:~8]','"dog human cancer"[tiab:~12]',
 '"comparative oncology dog human"[tiab:~15]','"toxicity animals humans"[tiab:~12]',
 '"nonclinical clinical safety"[tiab:~10]',
 # added to cover vocabularies the first pass showed were missing
 '"animal model human disease"[tiab:~12]','"translational animal research"[tiab:~10]',
 '"lost in translation"[ti]','"animal research clinical benefit"[tiab:~15]',
 '"systematic review animal studies"[tiab:~12]','"meta-analysis animal"[tiab:~10]',
 '"comparative oncology"[tiab]','"naturally occurring canine"[tiab:~8]',
 '"spontaneous tumors dogs"[tiab:~10]','"companion animal model"[tiab:~10]',
 '"animal model reproducibility"[tiab:~12]','"preclinical research quality"[tiab:~12]',
 '"animal to human translation"[tiab:~10]','"translational success rate"[tiab:~8]',
 '"drug development attrition animal"[tiab:~15]','"first-in-human preclinical"[tiab:~10]']

A = "(" + queries.B1_ANIMAL.replace("\n"," ") + ")"
H = "(" + queries.B3_HUMAN.replace("\n"," ") + ")"
V = "(" + queries.B6_VET.replace("\n"," ") + ")"

STRANDS = {
 "s1_proximity": "(" + " OR ".join(PROX) + ")",
 "s2_mesh_transl": f'"Translational Research, Biomedical"[Mesh] AND {A} AND {H}',
 "s3_concordance": f'(concordan*[tiab] OR discordan*[tiab] OR "predictive validity"[tiab] '
                   f'OR "predictivity"[tiab] OR "translatability"[tiab] OR "external validity"[tiab]) '
                   f'AND {A} AND {H}',
 "s4_species_diff": f'("species differences"[tiab] OR "species difference"[tiab] OR '
                    f'"cross-species"[tiab] OR interspecies[tiab] OR "Species Specificity"[Mesh]) '
                    f'AND (predict*[tiab] OR translat*[tiab] OR extrapolat*[tiab] OR concordan*[tiab]) AND {H}',
 "s5_vet": f'{V} AND {A} AND {H} AND (translat*[tiab] OR predict*[tiab] OR concordan*[tiab] '
           f'OR "comparative oncology"[tiab] OR "One Health"[tiab])',
 "s6_tox_conc": f'(toxicolog*[tiab] OR toxicity[tiab] OR "Toxicity Tests"[Mesh]) AND '
                f'(concordan*[tiab] OR predictiv*[tiab] OR "predictive value"[tiab]) AND {A} AND {H}',
 "s7_safetypharm": f'("safety pharmacology"[tiab] OR hERG[tiab] OR torsade*[tiab] OR "QT prolongation"[tiab]) '
                   f'AND (predict*[tiab] OR concordan*[tiab] OR translat*[tiab]) AND {A}',
}
DATE = queries.DATE
for k in STRANDS: STRANDS[k] = "(" + STRANDS[k] + ")" + DATE
UNION = "(" + " OR ".join("(" + v + ")" for v in STRANDS.values()) + ")"

ANCHORS = [("hackam2006","17032985"),("perel2007","17175568"),("contopoulos2008","18772421"),
 ("vanderworp2010","20361020"),("pound2018","30404629"),("leenaars2019","31307492"),
 ("bracken2009","19297654"),("wall2008","17988725"),("mak2014","24489990"),
 ("howells2010","20485296"),("marshall2023","36883244"),("sena2010","20361022"),
 ("begley2012","22460880"),("prinz2011","21892149"),("freedman2015","25670378"),
 ("olson2000","11029269"),("monticello2017","28893587"),("clark2018","29730448"),
 ("bailey2015","26753942"),("redfern2003","12667944"),("hay2014","24406927"),
 ("wong2019","29394327"),("cummings2014","25024750"),("seok2013","23401516"),
 ("takao2015","25092317"),("perrin2014","24678540"),("paoloni_khanna2008","18202698"),
 ("kol2015","26446953"),("fan_khanna2015","29061942")]

print("=== STRAND SIZES ===")
tot = {}
for k, q in STRANDS.items():
    tot[k] = pubmed.esearch(q)[0]
    print(f"  {k:18s} {tot[k]:>9,}")
n_union = pubmed.esearch(UNION)[0]
print(f"  {'UNION':18s} {n_union:>9,}")

print("\n=== RECALL ON UNION ===")
hit, miss = [], []
for k, p in ANCHORS:
    ok = bool(pubmed.esearch(f"({UNION}) AND {p}[uid]")[0])
    (hit if ok else miss).append(k)
    print(f"  {'OK ' if ok else 'MISS'} {k}")
print(f"\nRecall: {len(hit)}/{len(ANCHORS)} = {len(hit)/len(ANCHORS):.1%}")
print("Missed:", miss or "none")
json.dump({"strands": STRANDS, "union": UNION, "sizes": tot, "union_size": n_union,
           "recall": len(hit)/len(ANCHORS), "missed": miss},
          open(os.path.join(os.path.dirname(__file__),"..","data","raw","scoping_run_v4.json"),"w"), indent=1)
