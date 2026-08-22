"""Collapse duplicate figures within a study.

The same result often gets extracted twice from different sentences -- "93.2% of genes
changed in the same direction" and "93% genes changed in the same direction" are one
finding, not two. Duplicates inflate counts and make the tables look padded.

Two figures in the same study are duplicates when their values agree to within 1% (or
are equal after percent/proportion rescaling) AND their descriptions overlap heavily.
The more precise entry survives: more significant digits, then the longer verbatim."""
import json, os, re, itertools, collections
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MS = json.load(open(J("data","db","measurements.json")))
import os as _os
_RP = J("data","db","figure_refined.json")
REF = json.load(open(_RP)) if _os.path.exists(_RP) else {}

STOP = set("the of a an in and or to for with between from that this is are was were on by "
           "percentage percent share proportion number rate".split())
def toks(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}

def same_value(a, b):
    """Near-identical only. A loose tolerance merged 94% and 95% NPV for different
    species, and matched unrelated figures that happened to sit close together."""
    va, vb = a.get("value"), b.get("value")
    if va is None or vb is None: return False
    if a.get("unit") != b.get("unit"): return False
    return abs(va - vb) <= max(0.25, abs(vb) * 0.005)

def precision(x, pm=None, i=None):
    """Prefer the copy that survived refinement with a self-contained sentence: keeping
    a duplicate that lacks one throws away the readable version of the finding."""
    v = x.get("value")
    dec = len(str(v).split(".")[1]) if v is not None and "." in str(v) else 0
    r = ((REF.get(pm) or {}).get(str(i)) or {}) if pm is not None else {}
    refined = 1 if (r.get("keep") and r.get("precise")) else 0
    has_denom = 1 if r.get("denominator") else 0
    return (refined, has_denom, dec, len(x.get("verbatim") or ""), len(x.get("measures") or ""))

dupes = {}
removed = 0
for pm, m in MS.items():
    if "error" in m: continue
    mm = m.get("measurements") or []
    drop = set()
    for i, jx in itertools.combinations(range(len(mm)), 2):
        if i in drop or jx in drop: continue
        a, b = mm[i], mm[jx]
        if not same_value(a, b): continue
        ta, tb = toks(a.get("measures")), toks(b.get("measures"))
        if not ta or not tb: continue
        jac = len(ta & tb) / len(ta | tb)
        if jac < 0.85: continue                      # descriptions must be near-identical
        sa, sb = toks(a.get("statistic")), toks(b.get("statistic"))
        if sa and sb and len(sa & sb) / len(sa | sb) < 0.5: continue
        # a shared source sentence is strong evidence of a genuine duplicate
        if (a.get("verbatim") or "")[:80] != (b.get("verbatim") or "")[:80] and jac < 0.95:
            continue
        loser = i if precision(a, pm, i) < precision(b, pm, jx) else jx
        drop.add(loser)
    if drop:
        dupes[pm] = sorted(drop); removed += len(drop)
# Second pass, display-level: within a study, two figures with the same unit and the
# same value to the nearest whole number are one finding shown twice (93% and 93.2%
# "genes changed in the same direction"). Distinct subgroup results that differ by a
# whole point or more (94% vs 95% NPV for different species) are preserved.
for pm, m in MS.items():
    if "error" in m: continue
    mm = m.get("measurements") or []
    drop = set(dupes.get(pm, []))
    seen = {}
    for i, x in enumerate(mm):
        v, u = x.get("value"), x.get("unit")
        if v is None or i in drop: continue
        key = (u, round(float(v)))
        if key in seen:
            j = seen[key]
            # equal values are not enough: different subgroups often coincide
            # (several species each at 63%). Descriptions must overlap too.
            ta, tb = toks(x.get("measures")), toks(mm[j].get("measures"))
            jac = len(ta & tb) / len(ta | tb) if (ta and tb) else 0
            if jac < 0.5:
                continue
            keep_i = j if precision(mm[j], pm, j) >= precision(x, pm, i) else i
            lose_i = i if keep_i == j else j
            drop.add(lose_i); seen[key] = keep_i
        else:
            seen[key] = i
    if drop:
        dupes[pm] = sorted(drop)
removed = sum(len(v) for v in dupes.values())
json.dump(dupes, open(J("data","db","duplicate_figures.json"), "w"), indent=1)
tot = sum(len(m.get("measurements") or []) for m in MS.values() if "error" not in m)
print(f"figures {tot}; duplicates marked {removed} across {len(dupes)} studies")
for pm, idx in list(dupes.items())[:6]:
    mm = MS[pm]["measurements"]
    print(f"  {pm}: dropping {idx}")
    for i in idx[:2]:
        print(f"      {mm[i]['statistic']}={mm[i]['value']} | {(mm[i]['measures'] or '')[:70]}")
