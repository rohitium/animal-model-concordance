"""Resolve the §5.4 anchor set to PMIDs. Each anchor gets a targeted query; results
are printed for manual verification before being written to protocol/anchors.json."""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
import pubmed

ANCHORS = [
 # (key, category, query)
 ("hackam2006","efficacy",'Hackam DG[au] AND 2006[dp] AND animal[tiab]'),
 ("perel2007","efficacy",'Perel P[au] AND 2007[dp] AND animal[tiab]'),
 ("contopoulos2008","efficacy",'Contopoulos-Ioannidis DG[au] AND 2008[dp] AND (translation[tiab] OR promises[tiab])'),
 ("vanderworp2010","efficacy",'"van der Worp HB"[au] AND 2010[dp] AND animal[tiab]'),
 ("pound2018","efficacy",'Pound P[au] AND Ritskes-Hoitinga M[au] AND 2018[dp]'),
 ("leenaars2019","efficacy",'Leenaars CHC[au] AND 2019[dp] AND translational[tiab]'),
 ("bracken2009","efficacy",'Bracken MB[au] AND 2009[dp] AND animal[tiab]'),
 ("wall2008","efficacy",'Wall RJ[au] AND Shani M[au] AND 2008[dp]'),
 ("sena2010","bias",'Sena ES[au] AND 2010[dp] AND publication bias[tiab]'),
 ("begley2012","bias",'Begley CG[au] AND Ellis LM[au] AND 2012[dp]'),
 ("prinz2011","bias",'Prinz F[au] AND 2011[dp] AND (Believe it or not[ti] OR drug target[tiab])'),
 ("freedman2015","bias",'Freedman LP[au] AND 2015[dp] AND reproducibility[tiab]'),
 ("olson2000","tox",'Olson H[au] AND 2000[dp] AND (concordance[tiab] OR toxicity[tiab])'),
 ("monticello2017","tox",'Monticello TM[au] AND 2017[dp]'),
 ("clark2018","tox",'Clark M[au] AND Steger-Hartmann T[au] AND 2018[dp]'),
 ("bailey_nhp","tox",'Bailey J[au] AND (non-human primate[tiab] OR nonhuman primate[tiab]) AND predict*[tiab]'),
 ("redfern_safetypharm","tox",'Redfern WS[au] AND (safety pharmacology[tiab] OR QT[tiab])'),
 ("hay2014","attrition",'Hay M[au] AND 2014[dp] AND clinical development success[tiab]'),
 ("wong2019","attrition",'Wong CH[au] AND Lo AW[au] AND (2018[dp] OR 2019[dp])'),
 ("cummings_ad","attrition",'Cummings JL[au] AND Alzheimer[tiab] AND (drug development pipeline[tiab] OR failures[tiab])'),
 ("seok2013","contested",'Seok J[au] AND 2013[dp] AND (genomic responses[tiab] OR inflammatory diseases[tiab])'),
 ("takao2015","contested",'Takao K[au] AND Miyakawa T[au] AND 2015[dp]'),
 ("perrin2014","contested",'Perrin S[au] AND 2014[dp] AND (Preclinical research[ti] OR ALS[tiab])'),
 ("stair_nxy059","contested",'(NXY-059[tiab] AND (SAINT[tiab] OR stroke[tiab]))'),
 ("paoloni_khanna","vet",'Paoloni M[au] AND Khanna C[au] AND comparative oncology[tiab]'),
 ("leblanc_cotc","vet",'LeBlanc AK[au] AND (comparative oncology[tiab] OR Comparative Oncology Trials Consortium[tiab])'),
 ("kol2015","vet",'Kol A[au] AND (companion animal*[tiab] OR veterinary[tiab]) AND translational[tiab]'),
 ("vcog_ctcae","vet",'VCOG-CTCAE[tiab] OR (veterinary cooperative oncology group[tiab] AND adverse event*[tiab])'),
 ("recist_vet","vet",'(RECIST[tiab] AND (canine[tiab] OR dog*[tiab]) AND (solid tumo*[tiab] OR response evaluation[tiab]))'),
]

rows = []
for key, cat, q in ANCHORS:
    n, ids, _ = pubmed.esearch(q, retmax=5)
    summ = pubmed.esummary(ids)
    rows.append({"key": key, "category": cat, "query": q, "n_hits": n,
                 "candidates": [{"pmid": p, **summ.get(p, {})} for p in ids]})

json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "anchor_candidates.json"), "w"), indent=1)
for r in rows:
    print(f"\n=== {r['key']}  [{r['category']}]  hits={r['n_hits']}")
    for c in r["candidates"]:
        au = ", ".join(c.get("authors", []))
        print(f"  {c['pmid']}  {c.get('year','')}  {c.get('journal','')}  | {au} | {c.get('title','')[:110]}")
