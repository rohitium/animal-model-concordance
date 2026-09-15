"""Part 1: adjudication of flagged results, plus a blind re-check of a sample of verified ones (amendment A6).

A stronger model (claude-sonnet-5) reads the full PDF once per study and rules on EVERY result the verifier
did not exclude, verified and flagged alike (keep / keep with correction / drop), seeing all of the study's
results together so that like results are decided alike. The verifier is triage: results it flagged carry
its reasons; verified results carry none, so the adjudicator's decisions on them measure the verifier's
false-accept rate over all verified results, not a sample. (A 10% sample let an ancillary statistic reach
the final set in testing.)

Output: data/v04/part1/adjudicated.json, data/v04/part1/part1_quality.md
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from e2_verify import CHECKS

MODEL = "anthropic/claude-sonnet-5"
RECHECK_FRACTION, SEED = 0.10, 20260914

S = {"type": "string"}
DECISION = {"type": "object", "additionalProperties": False, "properties": {
    "id": S,
    "decision": {"type": "string", "enum": ["keep", "keep-with-correction", "drop"]},
    "drop_reason": {"type": ["string", "null"]},
    "corrected": {"type": "object", "additionalProperties": False, "properties": {
        "statement": S, "value": {"type": ["number", "null"]}, "unit": S,
        "numerator": {"type": ["number", "null"]}, "denominator": {"type": ["number", "null"]},
        "species": S, "model_type": S, "disease_area": S, "level": S, "direction": S, "pdf_page": {"type": ["integer", "null"]}},
        "required": ["statement", "value", "unit", "numerator", "denominator", "species", "model_type", "disease_area", "level", "direction", "pdf_page"]},
    "rationale": S},
    "required": ["id", "decision", "drop_reason", "corrected", "rationale"]}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"decisions": {"type": "array", "items": DECISION}}, "required": ["decisions"]}

SYSTEM = """You are the final reviewer of results extracted from the attached scientific paper for a review
of how well findings in non-human animals correspond to findings in humans. You receive every extracted
result for this paper. Decide each result listed under TO DECIDE; results under CONTEXT were already excluded
by an automated check and are shown only so that like results are decided alike. Return one decision per TO DECIDE id.

- keep: correct as extracted.
- keep-with-correction: a real animal-vs-human correspondence result with some field wrong; give the
  corrected fields.
- drop: not an animal-vs-human correspondence result, not the paper's own result, or not supported by the
  paper; say why.

A correspondence result measures how well animal findings matched human findings:
- concordance or agreement rates;
- translation rates;
- sensitivity, specificity, PPV, NPV, likelihood ratios;
- correlation, similarity or composite similarity scores between animal and human data;
- counts of interventions that agreed.

NOT correspondence results:
- treatment effects in animals alone;
- p-values;
- durations;
- sample sizes;
- intermediate or ancillary statistics of an analysis (e.g. differences between correlation groups);
- figures quoted from other papers.

Treat results of the same kind the same way: if one cancer type's composite similarity score is kept, keep
the others.

Fields:
- species: an individual species or "grouped-label".
- model_type: induced | engineered | spontaneous-lab | spontaneous-companion (client-owned or pet animals
  with naturally occurring disease, including their tumour samples) | healthy | mixed-or-not-stated.
- disease_area: the human condition's area (oncology, immunology-inflammation, infectious-disease,
  cardiovascular, metabolic-endocrine, renal, liver-gi, neurology, psychiatry-addiction,
  pain-musculoskeletal, respiratory, ophthalmology, haematology, dermatology, reproductive-developmental,
  cross-cutting-toxicology, or a new area name).
- level: A = intervention outcomes in animals vs humans; B = animal toxicity/safety vs human adverse
  effects; C = biological similarity without intervention outcome.
- direction: animal-corresponded | animal-did-not-correspond | mixed | not-applicable.
- corrected: always filled; repeat the values when unchanged.
- rationale: two sentences at most, citing the page.
Answer with JSON only."""

FIELDS = ("statement", "metric", "value", "unit", "ci_low", "ci_high", "numerator", "denominator",
          "denominator_counts", "species", "species_as_reported", "level", "direction", "quote", "pdf_page")

def main():
    """Every result of every eligible study is adjudicated, excluded ones included: the exclusion audit
    (e4_audit_excluded.py) found 15 of 59 verifier exclusions kept by the adjudicator (exact 95% CI 15–38%), above the
    10% threshold set before that audit. Studies adjudicated earlier on their non-excluded results get one additional
    call ("|excl") for their excluded results only; all other studies get a single call ("|all") for everything."""
    heads = load("part1/headlines.json")
    ver = load("part1/verified.json")
    out = load("part1/adjudicated.json")
    by_study = collections.defaultdict(list)
    for pm, h in heads.items():
        if h.get("status") == "done" and h.get("eligible"):
            for it in h["items"]:
                if it["id"] in ver:
                    by_study[pm].append(it)
    jobs = []
    for pm, its in sorted(by_study.items()):
        excluded = [i for i in its if ver[i["id"]]["status"] == "excluded"]
        if f"{pm}|all" in out and "error" not in out[f"{pm}|all"]:
            done = set(out[f"{pm}|all"]["decisions"])
            if excluded and f"{pm}|excl" not in out and any(i["id"] not in done for i in excluded):
                jobs.append((pm, "excl"))
        else:
            jobs.append((pm, "all"))
    print(f"adjudicating: {sum(1 for j in jobs if j[1]=='all')} studies (all results) + "
          f"{sum(1 for j in jobs if j[1]=='excl')} studies (excluded results only)", flush=True)

    def fmt(i):
        st = ver[i["id"]]["status"]
        extra = {"automated_check_raised": ver[i["id"]]["reasons"]} if st in ("needs-adjudication", "excluded") else {}
        return {"id": i["id"], **{k: i[k] for k in FIELDS}, **extra}

    def run(job):
        pm, kind = job
        its = by_study[pm]
        if kind == "all":
            decide, context = its, []
        else:
            done = set(out[f"{pm}|all"]["decisions"])
            decide = [i for i in its if ver[i["id"]]["status"] == "excluded" and i["id"] not in done]
            context = [i for i in its if i not in decide]
        user = (f"PMID: {pm}\n\nTO DECIDE:\n{json.dumps([fmt(i) for i in decide], indent=1)}\n\n"
                f"CONTEXT (already decided; shown so like results are decided alike):\n{json.dumps([fmt(i) for i in context], indent=1)}")
        r, _ = ask(MODEL, SYSTEM, user, SCHEMA, pm=pm, max_tokens=16000, deadline_s=480)
        got = {d["id"]: d for d in r["decisions"]}
        return {"kind": kind, "decisions": got, "missing": [i["id"] for i in decide if i["id"] not in got],
                "model": MODEL, "date": today()}
    for b in range(0, len(jobs), 50):   # save after every batch so an interrupted run loses at most one batch
        res = pmap(run, jobs[b:b + 50], workers=24, label=f"adjudicate batch {b // 50 + 1}/{-(-len(jobs) // 50)}")
        for (pm, kind), r in res.items():
            out[f"{pm}|{kind}"] = r
        save(out, "part1/adjudicated.json")

    dec = {}
    for k, r in out.items():
        if (k.endswith("|all") or k.endswith("|excl")) and "error" not in r:
            dec.update(r["decisions"])
    items = {i["id"]: i for its in by_study.values() for i in its}
    def substantive(iid, d):
        it, c = items[iid], d["corrected"]
        return d["decision"] == "drop" or (d["decision"] == "keep-with-correction" and (
            c["value"] != it["value"] or c["species"] != it["species"] or (c["level"] or "")[:1].upper() != (it["level"] or "")[:1]))
    by_status = collections.defaultdict(list)
    for iid, d in dec.items():
        if iid in ver:
            by_status[ver[iid]["status"]].append((iid, d))
    fa = sum(1 for iid, d in by_status["verified"] if substantive(iid, d))
    fe = sum(1 for iid, d in by_status["excluded"] if d["decision"] in ("keep", "keep-with-correction"))
    nv, ne = len(by_status["verified"]), len(by_status["excluded"])
    L = ["# Part 1 quality", "", f"Generated {today()} by `analysis/v04/e3_adjudicate.py` (adjudicator {MODEL}).", "",
         f"- studies: {len(by_study)}; results extracted: {sum(len(v) for v in by_study.values())}; results adjudicated: {len(dec)}",
         f"- verifier triage: {dict(collections.Counter(v['status'] for v in ver.values()))}",
         f"- adjudicator on flagged results: {dict(collections.Counter(d['decision'] for _, d in by_status['needs-adjudication']))}",
         f"- adjudicator on verified results: {dict(collections.Counter(d['decision'] for _, d in by_status['verified']))}",
         f"- adjudicator on excluded results: {dict(collections.Counter(d['decision'] for _, d in by_status['excluded']))}",
         f"- verifier false accepts (verified results dropped, or corrected in value, species or level): {fa}/{nv}" + (f" = {fa/nv:.0%}" if nv else ""),
         f"- verifier false exclusions (excluded results the adjudicator kept): {fe}/{ne}" + (f" = {fe/ne:.0%}" if ne else ""),
         f"- adjudication calls failed: {sum(1 for r in out.values() if 'error' in r)}; decisions missing: "
         f"{sum(len(r.get('missing', [])) for r in out.values())}", "", f"Cost (uncached): ${COST['usd']:.2f}"]
    open(os.path.join(V04, "part1", "part1_quality.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
