"""Part 2 quality pass and revised summary (amendment A6).

1. Treatment type per ingredient (one gpt-4.1-mini call each): small-molecule-drug | biologic | vaccine |
   cell-or-gene-therapy | dietary-supplement | mineral-or-element | device-or-material | procedure-or-regimen |
   not-a-treatment. Only the first four enter the primary table. Name matching had paired bone graft, platelet
   rich fibrin, "copper" (a disease: hepatic copper accumulation), supplements and regimens (CHOP).
2. Timing of US human approval relative to the veterinary evidence: the earliest original NDA/BLA approval for
   the ingredient (Drugs@FDA) vs the earliest year of its veterinary records. Strata: human approval before the
   veterinary evidence, after it, or no US approval. Descriptive only (A4): it does not change a pair's label,
   but concordance for drugs already established in humans is a different finding from agreement on drugs
   whose human outcome was not yet known.
3. Blind re-judgement: a seeded random 40 classified primary pairs are re-judged by gemini-2.5-pro from the same
   inputs as the original judge. Agreement and Cohen's kappa on the pair label are reported.

Output: data/v04/part2/quality.json, data/v04/part2/summary_v2.md
"""
import sys, os, re, random, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from s7_import_review import clopper_pearson
import d2_human_evidence as d2
from d1_candidates import efetch

TYPE_MODEL, SECOND_JUDGE = "openai/gpt-4.1-mini", "google/gemini-2.5-pro"
PRIMARY_TYPES = {"small-molecule-drug", "biologic", "vaccine", "cell-or-gene-therapy"}
SEED, N_REJUDGE = 20260914, 40

TYPE_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "treatment_type": {"type": "string", "enum": ["small-molecule-drug", "biologic", "vaccine", "cell-or-gene-therapy",
                        "dietary-supplement", "mineral-or-element", "device-or-material", "procedure-or-regimen", "not-a-treatment"]},
    "note": {"type": "string"}}, "required": ["treatment_type", "note"]}
TYPE_SYS = """Classify this name, which was matched as a treatment in a veterinary study. If several names are joined by
"+", classify what they have in common. procedure-or-regimen covers multi-drug protocols known by an acronym (e.g.
CHOP) and procedures (e.g. transarterial chemoembolization). not-a-treatment covers names that are a disease, a
body substance or a generic chemical word rather than a therapy. note: one short sentence. JSON only."""

def kappa(pairs):
    n = len(pairs)
    if not n:
        return None, None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return round(po, 3), (round((po - pe) / (1 - pe), 3) if pe < 1 else None)

def tally(ps):
    c = collections.Counter(p["judgement"]["pair"] for p in ps)
    k = c["concordant"] + c["discordant"]
    lo, hi = clopper_pearson(c["concordant"], k) if k else (None, None)
    return {"n": len(ps), **{x: c[x] for x in ("concordant", "discordant", "mixed", "indeterminate")},
            "classifiable": k, "concordance": (c["concordant"] / k) if k else None, "ci95": [lo, hi]}

def row(label, t):
    conc = f"{t['concordance']:.0%} ({t['ci95'][0]:.0%}–{t['ci95'][1]:.0%})" if t["classifiable"] else "—"
    return f"| {label} | {t['n']} | {t['concordant']} | {t['discordant']} | {t['mixed']} | {t['indeterminate']} | {conc} |"

def main():
    pairs = load("part2/pairs.json")
    cands = load("part2/candidates.json")["candidates"]
    index = load("frames/human_index.json")
    q = load("part2/quality.json", {})
    cl = {k: p for k, p in pairs.items() if p.get("status") == "classified" and not p.get("flag")}

    # 1. treatment type
    ings = sorted({p["ingredient"] for p in cl.values()} - set(q.get("types", {})))
    res = pmap(lambda i: ask(TYPE_MODEL, TYPE_SYS, f"NAME: {i}", TYPE_SCHEMA, max_tokens=300, deadline_s=60)[0], ings, workers=48, label="types")
    q.setdefault("types", {}).update({i: r for i, r in res.items() if "error" not in r})

    # 2. timing
    vet_year = collections.defaultdict(lambda: 9999)
    for c in cands:
        if c.get("year"):
            vet_year[c["record"]] = min(vet_year[c["record"]], int(c["year"]))
    for k, p in cl.items():
        yrs = [vet_year[r] for r in p["records"] if vet_year[r] < 9999]
        appr = [int(a["first_approval"][:4]) for nm in p["ingredient"].split("+") for a in (index.get(nm, {}).get("applications") or {}).values()
                if a.get("first_approval") and a.get("type") in ("NDA", "BLA")]
        p["_vet_year"] = min(yrs) if yrs else None
        p["_approval_year"] = min(appr) if appr else None
        p["_timing"] = ("no-us-approval" if not appr else "timing-unknown" if not yrs else
                        "human-approval-before-veterinary-evidence" if min(appr) < min(yrs) else "human-approval-after-veterinary-evidence")
        p["_type"] = q["types"].get(p["ingredient"], {}).get("treatment_type", "unclassified")
        p["_intent"] = "disease-modifying" if "disease" in ((p.get("terms") or {}).get("treatment_intent", "disease")).lower() else "symptomatic-or-preventive"

    # 3. blind re-judgement
    prim_all = [k for k, p in cl.items() if p.get("pair_type", "efficacy") == "efficacy" and p["relation"] != "class-analogue" and p["_type"] in PRIMARY_TYPES]
    sample = sorted(random.Random(SEED).sample(sorted(prim_all), min(N_REJUDGE, len(prim_all))))
    groups = d2.canonical_groups(cands)
    todo = [k for k in sample if k not in q.get("rejudge", {})]
    def rejudge(k):
        p = cl[k]
        key = tuple(k.split("|", 2))
        recs = groups.get(key, [])
        ab = efetch(p["relevant"] + [r["record"][5:] for r in recs if r["record"].startswith("PMID:")])
        vet_text = "\n\n".join(f"[{r['record']}] {r['title']} ({r['year']}) design={r['design']}\nEfficacy: {r['efficacy_result']}" +
                               (f"\nAbstract: {ab.get(r['record'][5:], {}).get('abstract', '')[:2500]}" if r["record"].startswith("PMID:") else "")
                               for r in recs[:6])
        human_text = "\n\n".join(f"[PMID {pm}] {ab.get(pm, {}).get('title','')} design={p['reads'][pm]['design']} phase={p['reads'][pm]['phase']}\n"
                                 f"Result: {p['reads'][pm]['result_sentence']}\nAbstract: {ab.get(pm, {}).get('abstract','')[:1800]}" for pm in p["relevant"][:20])
        label_text = "\n".join(f"[{kk}] {v['brand']} ({v['application']}): {v['indications']}" for kk, v in p["labels"].items()) or "(no US prescription label)"
        user = (f"DRUG: {p['ingredient']} (relation: {p['relation']})\nVETERINARY CONDITION: {p['veterinary_indication']}; species {', '.join(p['species'])}\n"
                f"HUMAN CONDITION: {p['terms']['human_condition']} (intent: {p['terms']['treatment_intent']})\n\nVETERINARY RECORDS:\n{vet_text}\n\n"
                f"US LABELS:\n{label_text}\n\nHUMAN RECORDS ({len(p['relevant'])} relevant):\n{human_text or '(none)'}")
        r, _ = ask(SECOND_JUDGE, d2.JUDGE_SYS, user, d2.JUDGE, max_tokens=8000, deadline_s=300)
        return r
    rj = pmap(rejudge, todo, workers=16, label="rejudge")
    q.setdefault("rejudge", {}).update({k: r for k, r in rj.items() if "error" not in r})
    save(q, "part2/quality.json")
    agree_pairs = [(cl[k]["judgement"]["pair"], q["rejudge"][k]["pair"]) for k in sample if k in q["rejudge"]]
    po, kap = kappa(agree_pairs)
    confusion = collections.Counter(agree_pairs)

    prim = [cl[k] for k in prim_all]
    strata = {
        "Primary (drugs, biologics, vaccines, cell/gene therapies)": prim,
        "Primary: disease-modifying use": [p for p in prim if p["_intent"] == "disease-modifying"],
        "Primary: symptomatic or preventive use": [p for p in prim if p["_intent"] != "disease-modifying"],
        "Primary: human approval before the veterinary evidence": [p for p in prim if p["_timing"] == "human-approval-before-veterinary-evidence"],
        "Primary: human approval after the veterinary evidence": [p for p in prim if p["_timing"] == "human-approval-after-veterinary-evidence"],
        "Primary: no US human approval": [p for p in prim if p["_timing"] == "no-us-approval"],
        "Primary, disease-modifying: dog": [p for p in prim if p["_intent"] == "disease-modifying" and p["species"] == ["dog"]],
        "Primary, disease-modifying: cat": [p for p in prim if p["_intent"] == "disease-modifying" and p["species"] == ["cat"]],
        "Excluded from primary: supplements, minerals, devices, regimens, non-treatments":
            [p for p in cl.values() if p.get("pair_type", "efficacy") == "efficacy" and p["relation"] != "class-analogue" and p["_type"] not in PRIMARY_TYPES],
        "Class analogues (separate)": [p for p in cl.values() if p["relation"] == "class-analogue"],
    }
    T = {k: tally(v) for k, v in strata.items()}
    L = ["# Dog and cat drug pairs: summary v2 (after quality pass)", "", f"Built {today()} by `analysis/v04/d4_quality.py`.", "",
         "Concordance = concordant / (concordant + discordant), exact 95% CI. Mixed and indeterminate are counted, never dropped.", "",
         "| stratum | pairs | concordant | discordant | mixed | indeterminate | concordance (95% CI) |", "|---|---|---|---|---|---|---|"]
    L += [row(k, t) for k, t in T.items()]
    L += ["", f"**Label reliability (blind re-judgement by {SECOND_JUDGE}, {len(agree_pairs)} random primary pairs):** "
          f"agreement {po:.0%}, Cohen's kappa {kap}." if agree_pairs else "", "",
          "Confusion (original → second judge): " + "; ".join(f"{a}→{b}: {n}" for (a, b), n in sorted(confusion.items())), "",
          f"Treatment types among classified pairs: {dict(collections.Counter(p['_type'] for p in cl.values()))}", "",
          "**Not yet produced:** Q4 (within-drug comparison with laboratory models, protocol §7.6); F1 cannot be stated yet."]
    open(os.path.join(V04, "part2", "summary_v2.md"), "w").write("\n".join(L) + "\n")
    save({k: {"type": p["_type"], "timing": p["_timing"], "vet_year": p["_vet_year"], "approval_year": p["_approval_year"],
              "intent": p["_intent"]} for k, p in cl.items()}, "part2/pair_attributes.json")
    print("\n".join(L))

if __name__ == "__main__":
    main()
