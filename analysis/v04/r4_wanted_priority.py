"""Rank full texts that open-access routes could not supply, so the user's manual effort goes where it matters.

Priority, in order:
  1. strict-screen decision: include before uncertain (no-abstract advances count as uncertain)
  2. evidence type: efficacy-translation, toxicology-safety, safety-pharmacology, companion-animal before
     disease-biology and unclassified (the page-15 claims rest mostly on the first four)
  3. citations (OpenAlex cited_by), higher first

Outputs: docs/fulltext_wanted_v04_priority.md (top 60, with DOI links), docs/fulltext_wanted_v04.md (all, ranked)
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

TYPE_RANK = {"efficacy-translation": 0, "toxicology-safety": 0, "safety-pharmacology": 0, "companion-animal": 0,
             "disease-biology": 1, "none": 2}
TOP = 60

def main():
    status = load("retrieval/fulltext_status.json")
    strict = load("retrieval/screen_strict.json")
    cands = load("retrieval/candidates.json")
    by_name = {(c.get("pmid") or c.get("openalex")): (k, c) for k, c in cands.items()}
    rows = []
    for name, st in status.items():
        if st["status"] != "not-found" or name not in by_name:
            continue
        k, c = by_name[name]
        s = strict.get(k, {})
        dec = s.get("decision") if s.get("decision") in ("include", "uncertain") else "uncertain"
        rows.append({"key": name, "decision": dec, "type": s.get("evidence_type", "none"), "cited_by": c.get("cited_by") or 0,
                     "year": c.get("year"), "title": c.get("title") or "", "doi": c.get("doi") or "", "journal": c.get("journal") or ""})
    rows.sort(key=lambda r: (r["decision"] != "include", TYPE_RANK.get(r["type"], 2), -r["cited_by"]))
    hdr = "| # | key (save as data/raw/fulltext/<key>.pdf) | year | cited | type | title | journal | DOI |\n|---|---|---|---|---|---|---|---|\n"
    line = lambda i, r: (f"| {i} | {r['key']} | {r['year']} | {r['cited_by']} | {r['type']} | {r['title'][:110]} | "
                         f"{r['journal'][:40]} | {r['doi']} |\n")
    with open(J("docs", "fulltext_wanted_v04_priority.md"), "w") as f:
        f.write(f"# Full texts wanted: top {TOP}\n\nOpen-access routes found no PDF for {len(rows)} screened-in studies. "
                "These are the ones most likely to change the page-15 table: strict-screen includes, efficacy/toxicology/"
                "safety/companion-animal evidence first, then by citations. Supplying these covers the highest-value gaps; "
                "the full ranked list is in `fulltext_wanted_v04.md`.\n\n" + hdr)
        for i, r in enumerate(rows[:TOP], 1):
            f.write(line(i, r))
    with open(J("docs", "fulltext_wanted_v04.md"), "w") as f:
        f.write(f"# Full texts wanted (all {len(rows)}, ranked)\n\n" + hdr)
        for i, r in enumerate(rows, 1):
            f.write(line(i, r))
    print(f"wanted: {len(rows)}; by decision {dict(collections.Counter(r['decision'] for r in rows))}; "
          f"by type {dict(collections.Counter(r['type'] for r in rows))}")

if __name__ == "__main__":
    main()
