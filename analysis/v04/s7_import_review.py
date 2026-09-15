"""Stage 7 — read the reviewer's decisions back and publish the measured error rate (§8.1 stage 5, §8.4).

The review page stores decisions in its artifact database. They are exported (Artifact read_db with
out_dir) to data/v04/review/db/{resolutions,audit}/<item id>.json, and this script applies them.

Outputs: s7_final.json (every item with its final status and who decided it),
         audit_result.json (false-accept rate with exact 95% CI)
"""
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

def rows(kind):
    out = {}
    for p in glob.glob(os.path.join(V04, "review", "db", kind, "*.json")):
        d = json.load(open(p))
        body = d.get("data", d)
        out[os.path.splitext(os.path.basename(p))[0]] = body
    return out

def _betainc(a, b, x):
    """Regularised incomplete beta by continued fraction (Numerical Recipes)."""
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1 - x))
    if x > (a + 1) / (a + b + 2):
        return 1 - _betainc(b, a, 1 - x)
    f, c, d = 1.0, 1.0, 0.0
    for i in range(400):
        m = i // 2
        if i == 0: num = 1.0
        elif i % 2 == 0: num = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
        else: num = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1 + num * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1 + num / c if abs(c) > 1e-30 else 1e-30
        f *= c * d
        if abs(1 - c * d) < 1e-12: break
    return front * (f - 1) / a

def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial CI, by bisection on the beta CDF."""
    if n == 0: return (None, None)
    def solve(target, lo_side):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            val = _betainc(k, n - k + 1, mid) if lo_side else _betainc(k + 1, n - k, mid)
            if lo_side:
                (lo, hi) = (lo, mid) if val > target else (mid, hi)
            else:
                (lo, hi) = (lo, mid) if val > target else (mid, hi)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(alpha / 2, True)
    upper = 1.0 if k == n else solve(1 - alpha / 2, False)
    return (round(lower, 4), round(upper, 4))

def main():
    dec = load("s5_decisions.json")
    res, aud = rows("resolutions"), rows("audit")
    final = {}
    for iid, d in dec.items():
        r = res.get(iid)
        f = {"automated_status": d["status"], "reasons": d["reasons"]}
        if d["status"] == "flagged":
            if r and r.get("decision"):
                f["final_status"] = {"accept": "accepted-by-reviewer", "correct": "accepted-with-correction",
                                     "reject": "rejected-by-reviewer", "unsure": "unresolved"}[r["decision"]]
                f["review"] = r
            else:
                f["final_status"] = "awaiting-review"
        else:
            f["final_status"] = d["status"]
        final[iid] = f
    for iid, r in res.items():
        if iid.endswith("-scope"):
            final[iid] = {"automated_status": "study-exclusion", "review": r,
                          "final_status": {"accept": "study-exclusion-confirmed", "reject": "study-reinstated",
                                           "unsure": "unresolved"}.get(r.get("decision"), "awaiting-review")}
    save(final, "s7_final.json")

    sample = load("audit_sample.json", [])
    judged = [a for a in sample if (aud.get(a["id"]) or {}).get("correct") in ("yes", "no")]
    wrong = [a for a in judged if aud[a["id"]]["correct"] == "no"]
    lo, hi = clopper_pearson(len(wrong), len(judged))
    result = {"sample_size": len(sample), "judged": len(judged), "unsure": sum(1 for a in sample if (aud.get(a["id"]) or {}).get("correct") == "unsure"),
              "false_accepts": len(wrong), "rate": round(len(wrong) / len(judged), 4) if judged else None,
              "ci95_exact": [lo, hi], "threshold": 0.05,
              "escalate": (len(wrong) / len(judged) > 0.05) if judged else None,
              "wrong_items": [{"id": a["id"], "note": aud[a["id"]].get("note")} for a in wrong], "date": today()}
    save(result, "audit_result.json")
    import collections
    print(dict(collections.Counter(v["final_status"] for v in final.values())))
    print(f"audit: {len(wrong)}/{len(judged)} false accepts, rate {result['rate']}, exact 95% CI {lo}-{hi}")

if __name__ == "__main__":
    main()
