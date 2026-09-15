"""Stage 3 — mechanical location in the PDF text layer and alignment of the two extractions
(PLAN.md v0.4 §8.1 stages 1-2).

Location uses no model: each value, count and quote is searched for on every page of the PDF's text
layer. Alignment pairs each comparison from extractor A with its counterpart from extractor B, so
that agreement between them can be checked field by field.

Input: s2_extract.json. Output: data/v04/s3_items.json (one item per aligned comparison).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

QUOTE_OK = 0.6      # share of the quote's word 4-grams found on one page

def as_fraction(c):
    """Value on a common 0-1 scale where that is meaningful, for comparing A with B."""
    v = c.get("value")
    if v is None:
        return None
    if c.get("unit") == "percent":
        return v / 100.0
    return v

def located(pm, c):
    loc = locate(pm, [c.get("value")], c.get("quote"))
    counts = [x for x in (c.get("numerator"), c.get("denominator")) if x is not None]
    loc["pages_counts"] = locate(pm, counts, None)["pages_all_values"] if counts else []
    vp = set(loc["pages_all_values"])
    q_ok = loc["quote_score"] >= QUOTE_OK
    if c.get("value") is None:
        loc["status"] = "quote-found" if q_ok else "not-found"
    elif vp and q_ok and loc["best_quote_page"] in vp:
        loc["status"] = "value-and-quote-same-page"
    elif vp and q_ok:
        loc["status"] = "value-and-quote-different-pages"
    elif vp:
        loc["status"] = "value-only"
    elif q_ok:
        loc["status"] = "quote-only"
    else:
        loc["status"] = "not-found"
    return loc

def similarity(a, b):
    """Score for pairing two comparisons; None when they cannot be the same result."""
    fa, fb = as_fraction(a), as_fraction(b)
    if (fa is None) != (fb is None):
        return None
    s = 0.0
    if fa is not None:
        if abs(fa - fb) > max(0.005, 0.01 * abs(fa)):
            return None
        s += 3
    s += 1.5 * (a["species"] == b["species"])
    s += 1.0 * (a["metric"] == b["metric"])
    s += 0.5 * (a["level"] == b["level"])
    s += 1.0 * quote_score(a["quote"], b["quote"]) + 1.0 * quote_score(b["quote"], a["quote"])
    if fa is None and s < 2.0:          # qualitative: need real textual overlap
        return None
    return s

FIELDS = ["species", "species_as_reported", "model_type", "index_test_kind", "level", "metric",
          "disease_area", "provenance", "unit", "numerator", "denominator", "ci_low", "ci_high"]

def dedupe(lst):
    """Collapse one extractor's repeats of the same result (same value, species and metric, with
    overlapping quotes), keeping the first. Tier-1 Gemini repeated results several times, which
    otherwise surface as spurious 'found by only one extractor' flags. Returns (kept, n_dropped)."""
    kept = []
    for c in lst:
        dup = False
        for k in kept:
            if (as_fraction(c) == as_fraction(k) and c["species"] == k["species"] and c["metric"] == k["metric"]
                    and c.get("numerator") == k.get("numerator") and c.get("denominator") == k.get("denominator")
                    and (quote_score(c["quote"], k["quote"]) >= 0.5 or quote_score(k["quote"], c["quote"]) >= 0.5
                         or c["quote"][:40] == k["quote"][:40])):
                dup = True
                break
        if not dup:
            kept.append(c)
    return kept, len(lst) - len(kept)

def main():
    ext = load("s2_extract.json")
    items = []
    dropped = {"A": 0, "B": 0}
    for pm, rec in sorted(ext.items()):
        A = [] if "error" in rec["A"]["result"] else rec["A"]["result"]["comparisons"]
        B = [] if "error" in rec["B"]["result"] else rec["B"]["result"]["comparisons"]
        A, da = dedupe(A)
        B, db_ = dedupe(B)
        dropped["A"] += da
        dropped["B"] += db_
        cand = []
        for i, a in enumerate(A):
            for j, b in enumerate(B):
                sc = similarity(a, b)
                if sc is not None:
                    cand.append((sc, i, j))
        used_a, used_b, pairs = set(), set(), []
        for sc, i, j in sorted(cand, reverse=True):
            if i in used_a or j in used_b:
                continue
            used_a.add(i); used_b.add(j); pairs.append((i, j))
        pairs += [(i, None) for i in range(len(A)) if i not in used_a]
        pairs += [(None, j) for j in range(len(B)) if j not in used_b]
        for k, (i, j) in enumerate(pairs):
            a = A[i] if i is not None else None
            b = B[j] if j is not None else None
            item = {"id": f"{pm}-{k:03d}", "pmid": pm, "A": a, "B": b,
                    "A_index": i, "B_index": j,
                    "models": {"A": rec["A"]["model"], "B": rec["B"]["model"]},
                    "tier": rec["A"]["tier"]}
            if a and b:
                item["disagreements"] = [f for f in FIELDS if a.get(f) != b.get(f)]
            item["locate"] = {r: located(pm, x) for r, x in (("A", a), ("B", b)) if x}
            items.append(item)
        print(f"  {pm}: A={len(A)} B={len(B)} matched={sum(1 for i,j in pairs if i is not None and j is not None)}")
    save(items, "s3_items.json")
    import collections
    both = [x for x in items if x["A"] and x["B"]]
    print(f"within-extractor duplicates collapsed: {dropped}")
    print(f"items {len(items)}: both={len(both)} A-only={sum(1 for x in items if x['A'] and not x['B'])} "
          f"B-only={sum(1 for x in items if x['B'] and not x['A'])}")
    print("location (A):", dict(collections.Counter(x["locate"]["A"]["status"] for x in items if "A" in x["locate"])))

if __name__ == "__main__":
    main()
