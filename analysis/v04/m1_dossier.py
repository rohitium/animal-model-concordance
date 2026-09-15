"""Manual adjudication, step 1: print compact dossiers for studies whose adjudication call failed (no API calls).

After API credit ran out, the reviewing agent adjudicates the remaining studies in-session by reading each study's
extracted results against the PDF text layer, applying the same criteria as the model adjudicator (e3_adjudicate.SYSTEM).

Priority order: strict-screen evidence type efficacy / toxicology / safety pharmacology / companion animal first,
then disease biology; within each, more-cited first.

Usage: python3 m1_dossier.py START COUNT   → prints dossiers for pending studies [START, START+COUNT)
       python3 m1_dossier.py --count       → prints how many remain
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa  (load, pages, quote_score; no network use)

RANK = {"efficacy-translation": 0, "toxicology-safety": 0, "safety-pharmacology": 0, "companion-animal": 0, "disease-biology": 1}

def pending():
    heads = load("part1/headlines.json"); ver = load("part1/verified.json"); adj = load("part1/adjudicated.json")
    strict = load("retrieval/screen_strict.json"); cands = load("retrieval/candidates.json"); studies = load("part1/studies.json")
    by_name = {(c.get("pmid") or c.get("openalex")): k for k, c in cands.items()}
    out = []
    for pm, h in heads.items():
        if h.get("status") != "done" or not h.get("eligible"):
            continue
        ok = any(k in adj and "error" not in adj[k] for k in (f"{pm}|all",))
        if ok or f"{pm}|manual" in adj:
            continue
        k = by_name.get(pm)
        typ = (strict.get(k) or {}).get("evidence_type", "none") if k else "none"
        cites = (cands.get(k) or {}).get("cited_by") or 0
        out.append((RANK.get(typ, 2), -cites, pm, typ))
    out.sort()
    return out, heads, ver, studies

def snippet(pm, page, quote, width=450):
    pg = pages(pm)
    if not page or not (1 <= page <= len(pg)):
        return ""
    t = re.sub(r"\s+", " ", pg[page - 1])
    q = re.sub(r"\s+", " ", quote or "")[:60]
    i = t.find(q[:30]) if q else -1
    if i < 0:
        words = [w for w in re.findall(r"[A-Za-z]{5,}", quote or "")][:4]
        i = max((t.find(w) for w in words), default=-1)
    if i < 0:
        return t[:width * 2]
    return t[max(0, i - width): i + width]

def main():
    todo, heads, ver, studies = pending()
    if sys.argv[1:2] == ["--count"]:
        print(f"{len(todo)} studies pending; by type {dict(collections.Counter(t for *_, t in todo))}")
        return
    start, count = int(sys.argv[1]), int(sys.argv[2])
    for rank, negc, pm, typ in todo[start:start + count]:
        h = heads[pm]
        print(f"\n=== {pm} | {typ} | cited {-negc} | {(studies.get(pm) or {}).get('title', '')[:120]}")
        print(f"design={h.get('design')}")
        shown = set()
        for it in h["items"]:
            v = ver.get(it["id"], {})
            page = it["locate"].get("best_quote_page") or it.get("pdf_page")
            print(f"- {it['id'].rsplit('-', 1)[1]} [{v.get('status','?')[:4]}] {it['level'][:1]} sp={it['species']} mt={it.get('model_type')} "
                  f"area={it.get('disease_area')} val={it['value']} {it['unit']} n={it['numerator']}/{it['denominator']} dir={it['direction']}")
            print(f"  S: {it['statement'][:200]}")
            q = (it.get('quote') or '')[:200]
            if (page, q) not in shown:
                print(f"  Q(p{page}): {q}")
                if v.get("reasons"):
                    print(f"  verifier: {v['reasons'][0][:90]}")
                ctx = snippet(pm, page, it.get("quote"), width=250)
                if ctx:
                    print(f"  CTX: {ctx[:500]}")
                shown.add((page, q))

if __name__ == "__main__":
    main()
