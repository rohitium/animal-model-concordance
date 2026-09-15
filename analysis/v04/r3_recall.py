"""Recall of the expanded search by capture–recapture (amendment A6; replaces the held-out check, L76).

Two retrieval mechanisms ran independently: citation chasing (backward + forward from seeds) and theme
queries in PubMed. Among studies finally judged eligible (e1 eligible and at least one final result), let
  n1 = found by citation chasing, n2 = found by queries, m = found by both.
Chapman's estimator of the total number of eligible studies reachable by either kind of search is
  N = (n1+1)(n2+1)/(m+1) - 1,  var = (n1+1)(n2+1)(n1-m)(n2-m) / ((m+1)^2 (m+2)),
and recall of the union is (n1 + n2 - m) / N.

Assumption, stated in the output: the two mechanisms find eligible studies independently. Citation
chasing and keyword queries plausibly miss different kinds of study, but positive dependence (both favour
well-known papers) biases N downward, i.e. recall upward; the estimate is an upper bound on recall.
Seeds are excluded from the counts because they were found by construction.

Output: data/v04/retrieval/recall.md
"""
import sys, os, math, json, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

def main():
    cands = load("retrieval/candidates.json")
    rows = load("part1/final_results.json", [])
    eligible = {r["pmid"] for r in rows if r["status"] == "final"}
    by_name = {}
    for k, c in cands.items():
        by_name[c.get("pmid") or c.get("openalex")] = c
    n1 = n2 = m = 0; seeds = 0; unknown = 0
    for s in eligible:
        c = by_name.get(s)
        if not c:
            unknown += 1; continue
        src = {x.split(":")[0] for x in c["sources"]}
        if "seed" in src:
            seeds += 1; continue
        cit = bool(src & {"backward", "forward"}); q = "query" in src
        n1 += cit; n2 += q; m += cit and q
    L = ["# Recall of the expanded search (capture–recapture)", "", f"Computed {today()} by `analysis/v04/r3_recall.py`.", "",
         f"- eligible studies with a final result: {len(eligible)} (seeds excluded: {seeds}; not from expanded retrieval: {unknown})",
         f"- found by citation chasing: {n1}; by queries: {n2}; by both: {m}"]
    if m > 0:
        N = (n1 + 1) * (n2 + 1) / (m + 1) - 1
        var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m) / ((m + 1) ** 2 * (m + 2))
        se = math.sqrt(var)
        union = n1 + n2 - m
        lo, hi = max(union, N - 1.96 * se), N + 1.96 * se
        L += [f"- estimated eligible studies reachable (Chapman): {N:.0f} (95% CI {lo:.0f}–{hi:.0f})",
              f"- estimated recall of the union: {union/N:.0%} (95% CI {union/hi:.0%}–{min(1, union/lo):.0%})"]
    else:
        L.append("- no overlap between mechanisms: recall cannot be estimated this way")
    L += ["", "Assumes the two mechanisms find eligible studies independently; positive dependence makes this an upper bound on recall."]
    open(os.path.join(V04, "retrieval", "recall.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
