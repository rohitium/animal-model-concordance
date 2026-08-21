"""PubMed proximity search ("a b"[tiab:~N]) as the precision instrument.
Test candidate proximity cores for yield and for anchor coverage."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pubmed
CAND = [
 '"animal human concordance"[tiab:~15]',
 '"animal clinical concordance"[tiab:~15]',
 '"animal human predict"[tiab:~10]',
 '"animal model predict human"[tiab:~10]',
 '"animal patient predict"[tiab:~12]',
 '"preclinical clinical translation"[tiab:~10]',
 '"preclinical clinical concordance"[tiab:~12]',
 '"preclinical clinical predict"[tiab:~10]',
 '"animal studies clinical trials"[tiab:~12]',
 '"animal experiments clinical trials"[tiab:~12]',
 '"mouse human translate"[tiab:~10]',
 '"species concordance"[tiab:~8]',
 '"translation animals humans"[tiab:~10]',
 '"animals humans extrapolation"[tiab:~12]',
 '"animal model validity"[tiab:~8]',
 '"dog human cancer"[tiab:~12]',
 '"comparative oncology dog human"[tiab:~15]',
 '"toxicity animals humans"[tiab:~12]',
 '"nonclinical clinical safety"[tiab:~10]',
]
ANCH = {"hackam2006":"17032985","perel2007":"17175568","contopoulos2008":"18772421",
 "vanderworp2010":"20361020","pound2018":"30404629","leenaars2019":"31307492",
 "bracken2009":"19297654","wall2008":"17988725","mak2014":"24489990","howells2010":"20485296",
 "olson2000":"11029269","clark2018":"29730448","bailey2015":"26753942","redfern2003":"12667944",
 "monticello2017":"28893587","seok2013":"23401516","takao2015":"25092317","perrin2014":"24678540",
 "paoloni_khanna2008":"18202698","kol2015":"26446953","fan_khanna2015":"29061942",
 "marshall2023":"36883244","sena2010":"20361022"}
print(f"{'proximity core':46s} {'hits':>8s}  anchors hit")
union_hits = set()
for c in CAND:
    n = pubmed.esearch(c)[0]
    got = [k for k, p in ANCH.items() if pubmed.esearch(f"({c}) AND {p}[uid]")[0]]
    union_hits.update(got)
    print(f"{c:46s} {n:>8,}  {','.join(got) or '-'}")
print(f"\nUnion of proximity cores covers {len(union_hits)}/{len(ANCH)} sampled anchors")
print("Not covered:", sorted(set(ANCH) - union_hits))
