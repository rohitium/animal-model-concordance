"""Part 1 study list (amendment A6): every screened-in record with a full-text PDF, plus the v0.4 stage-1
includes. Records advanced by screening but without a PDF are counted and listed in
docs/fulltext_wanted_v04.md; they enter when the user supplies the PDF and this is re-run.

Output: data/v04/part1/studies.json, data/v04/part1/studies_report.md
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

def main():
    screen = load("retrieval/screen.json")
    strict = load("retrieval/screen_strict.json")
    cands = load("retrieval/candidates.json")
    ft = load("retrieval/fulltext_status.json")
    scope = load("s1_scope.json")
    studies, no_pdf = {}, 0
    theme = collections.Counter()
    for k, r in strict.items():
        if "error" in r or r.get("decision") not in ("include", "uncertain") or k not in cands:
            continue
        c = cands[k]
        name = c.get("pmid") or c.get("openalex")
        if pdf_path(name):
            studies[name] = {"title": c["title"], "year": c.get("year"), "journal": c.get("journal"),
                             "doi": c.get("doi"), "openalex": c.get("openalex"), "sources": c.get("sources"),
                             "screen_theme": r.get("evidence_type")}
            theme[studies[name]["screen_theme"]] += 1
        else:
            no_pdf += 1
    for pm, r in scope.items():
        if r.get("decision") in ("include", "include-provisional") and pm not in studies and pdf_path(pm):
            studies[pm] = {"title": r.get("title"), "year": r.get("year"), "sources": ["v0.3-corpus"], "screen_theme": None}
    save(studies, "part1/studies.json")
    L = ["# Part 1 study list", "", f"Built {today()} by `analysis/v04/p1_build_studies.py`.", "",
         f"- advanced by first screening pass: {sum(1 for r in screen.values() if r.get('advance'))}",
         f"- passed strict second pass: {sum(1 for r in strict.values() if 'error' not in r and r.get('decision') in ('include', 'uncertain'))}",
         f"- with a PDF (entering extraction): {len(studies)}",
         f"- advanced but no open-access PDF (listed in docs/fulltext_wanted_v04.md): {no_pdf}", "", "## By screening theme", ""]
    L += [f"- {k}: {v}" for k, v in theme.most_common()]
    open(os.path.join(V04, "part1", "studies_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
