"""Part 1: audit of verifier exclusions (amendment A6).

The verifier (gpt-5-mini) excludes a result when it is confident the number is not an animal-vs-human correspondence
result, or not the paper's own, and the value is located. Excluded results are never adjudicated, so a verifier that
is too strict would silently remove genuine evidence. Here the adjudicator (claude-sonnet-5) re-decides a seeded
random sample of excluded results, grouped by study, blind to the verifier's reasons.

False-exclusion rate = excluded results the adjudicator keeps (with or without correction), with exact 95% CI.
Decision rule, stated before the run: if the rate's upper CI bound exceeds 10%, every excluded result is adjudicated.

Output: data/v04/part1/excluded_audit.json, data/v04/part1/excluded_audit.md
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from e3_adjudicate import MODEL, SYSTEM, SCHEMA, FIELDS
from s7_import_review import clopper_pearson

N, SEED = 60, 20260915

def main():
    heads = load("part1/headlines.json")
    ver = load("part1/verified.json")
    items = {it["id"]: (pm, it) for pm, h in heads.items() if h.get("status") == "done" and h.get("eligible") for it in h["items"]}
    excluded = sorted(i for i, v in ver.items() if v["status"] == "excluded" and i in items)
    sample = random.Random(SEED).sample(excluded, min(N, len(excluded)))
    by_study = collections.defaultdict(list)
    for iid in sample:
        by_study[items[iid][0]].append(items[iid][1])
    out = load("part1/excluded_audit.json")
    todo = [pm for pm in sorted(by_study) if pm not in out]
    print(f"auditing {len(sample)} of {len(excluded)} excluded results in {len(by_study)} studies", flush=True)

    def run(pm):
        decide = by_study[pm]
        user = (f"PMID: {pm}\n\nTO DECIDE:\n{json.dumps([{'id': i['id'], **{k: i[k] for k in FIELDS}} for i in decide], indent=1)}\n\n"
                f"CONTEXT:\n[]")
        r, _ = ask(MODEL, SYSTEM, user, SCHEMA, pm=pm, max_tokens=12000, deadline_s=480)
        return {"decisions": {d["id"]: d for d in r["decisions"]}}
    res = pmap(run, todo, workers=16, label="excluded-audit")
    out.update({pm: r for pm, r in res.items() if "error" not in r})
    save(out, "part1/excluded_audit.json")

    dec = {iid: d for r in out.values() for iid, d in r["decisions"].items() if iid in sample}
    kept = [iid for iid, d in dec.items() if d["decision"] in ("keep", "keep-with-correction")]
    n = len(dec)
    lo, hi = clopper_pearson(len(kept), n) if n else (None, None)
    verdict = ("upper bound above 10%: adjudicate every excluded result" if n and hi > 0.10
               else "upper bound at or below 10%: verifier exclusions stand")
    L = ["# Audit of verifier exclusions", "", f"Run {today()} by `analysis/v04/e4_audit_excluded.py`, adjudicator {MODEL}, seed {SEED}.", "",
         f"- excluded results: {len(excluded)}; audited: {n} in {len(by_study)} studies",
         f"- adjudicator decisions: {dict(collections.Counter(d['decision'] for d in dec.values()))}",
         f"- false-exclusion rate: {len(kept)}/{n}" + (f" = {len(kept)/n:.0%} (exact 95% CI {lo:.0%}–{hi:.0%})" if n else ""),
         f"- decision rule (set before the run): {verdict}", "", "## Wrongly excluded (kept by the adjudicator)", ""]
    for iid in kept:
        pm, it = items[iid]
        L.append(f"- {iid}: {it['statement'][:140]} | verifier said: {'; '.join(ver[iid]['reasons'])[:160]}")
    L += ["", f"Cost (uncached): ${COST['usd']:.2f}"]
    open(os.path.join(V04, "part1", "excluded_audit.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:9]))

if __name__ == "__main__":
    main()
