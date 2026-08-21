"""Regenerate docs/fulltext_wanted.md from what is actually on disk.

Written as a script rather than a one-off because a hand-made list goes stale the
moment a file is added. Run after dropping any new full text into data/raw/fulltext/.
"""
import json, os, glob, sys
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
db = json.load(open(J("data","db","studies.json")))
CLS = json.load(open(J("data","db","classification.json")))
meta = json.load(open(J("data","db","metadata.json")))
have = {os.path.basename(p).rsplit(".",1)[0] for p in glob.glob(J("data","raw","fulltext","*"))}
# Only list studies that are ELIGIBLE under rubric r3. Listing excluded records
# (in silico, in vitro, human-only) sends the reader chasing papers this review
# will not use.
need = [p for p in db if p not in have and db[p].get("eligible") is not False]
excluded_missing = [p for p in db if p not in have and db[p].get("eligible") is False]
rows = sorted(((db[p].get("cited_by") or 0, db[p].get("year") or 0, p) for p in need), reverse=True)

def title_of(pm):
    return db[pm].get("title") or (meta.get(pm) or {}).get("title") or "(title not retrieved)"
def journal_of(pm):
    return db[pm].get("journal") or (meta.get(pm) or {}).get("journal_full") or "—"

elig = [p for p in db if db[p].get("eligible") is not False]
out = ["# Full texts still needed", "",
 f"**{len(need)}** eligible studies lack full text.",
 f"({len(elig)} eligible of {len(db)} screened; {len([p for p in elig if p in have])} eligible already held.)",
 "",
 f"{len(excluded_missing)} further records without full text were **excluded** under rubric r3 "
 "(in silico only, in vitro only, human only, or reporting no animal-to-human agreement "
 "statistic) and are deliberately omitted below &mdash; they are not needed.",
 "", "Save each as `data/raw/fulltext/<PMID>.pdf` (or `.xml`), then run:", "",
 "```bash", "python3 analysis/14_extract_fulltext.py", "python3 analysis/20_measurements.py",
 "python3 analysis/19_reclassify.py", "python3 analysis/21_wanted_list.py",
 "python3 analysis/15_build_site.py", "```", "",
 "Files are gitignored and never published; only extracted data reaches the site.", "",
 "| PMID | Cites | Year | Arm | Journal | Title | DOI |", "|---|---|---|---|---|---|---|"]
for c, y, pm in rows:
    d = (meta.get(pm) or {}).get("doi")
    doi = f"[{d}](https://doi.org/{d})" if d else "—"
    cl = CLS.get(pm) or {}
    arm = cl.get("arm") or "—"
    out.append(f"| [{pm}](https://pubmed.ncbi.nlm.nih.gov/{pm}/) | {c} | {y or '—'} | {arm} | "
               f"{journal_of(pm)} | {title_of(pm)} | {doi} |")
open(J("docs","fulltext_wanted.md"), "w").write("\n".join(out) + "\n")
print(f"eligible {len(elig)}/{len(db)}; eligible held {len([p for p in elig if p in have])}; "
      f"still needed {len(need)}; excluded-and-missing omitted {len(excluded_missing)}")
