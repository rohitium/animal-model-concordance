"""Q4 (protocol §7.6): within-drug comparison of companion-animal and laboratory-model concordance with humans.

For every primary efficacy pair (drug, biologic, vaccine, cell/gene therapy; see d4_quality.py) whose human side
is classifiable (positive, negative or mixed):
  1. PubMed search for studies of the same drug in induced or engineered LABORATORY animal models of the same
     condition (mice, rats, rabbits, laboratory dogs, pigs, primates), excluding client-owned/naturally
     occurring disease. Up to 30 records by relevance.
  2. A fast model reads each abstract: is it an in vivo efficacy study in an induced/engineered laboratory
     model of this condition, testing this drug; result positive / negative / unclear.
  3. Laboratory side in code. Primary rule: positive or negative when at least 75% of classifiable studies agree,
     mixed otherwise. Sensitivity: unanimous rule. (A first run with the unanimous rule, a reader that credited
     studies using the drug only as a benchmark, and adverse effects counted as failures was invalid; kept as
     lab_models_first_run_invalid.json.)
  4. Paired comparison on pairs where the companion-animal, laboratory and human sides are all positive or
     negative: companion concordant vs laboratory concordant, per drug × condition. Reported as the difference
     in concordance proportions with an exact McNemar-style 95% CI on the discordant cells, and stated plainly
     per F1 whichever way it falls.
Caveat carried into the output: laboratory efficacy literature is strongly biased towards positive results
(publication bias, L7), which inflates laboratory agreement wherever the human result is positive.

Output: data/v04/part2/lab_models.json, data/v04/part2/q4_report.md
"""
import sys, os, re, collections, threading
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
import pubmed
from d1_candidates import efetch
from s7_import_review import clopper_pearson

READ_MODEL = "google/gemini-2.5-flash"   # escalated from flash-lite (§8.2): flash-lite credited PTU used to induce disease, comparator studies and other conditions (lab_models_flashlite.json; audit in q4_reader_audit.md)
MAX_LAB = 30
_ncbi = threading.Semaphore(3)
PRIMARY_TYPES = {"small-molecule-drug", "biologic", "vaccine", "cell-or-gene-therapy"}

READ = {"type": "object", "additionalProperties": False, "properties": {
    "lab_model_efficacy_study": {"type": "boolean"},
    "model": {"type": "string"},
    "result": {"type": "string", "enum": ["positive", "negative", "unclear"]},
    "result_sentence": {"type": ["string", "null"]}},
    "required": ["lab_model_efficacy_study", "model", "result", "result_sentence"]}
READ_SYS = """Is this record an in vivo efficacy study in LABORATORY animals in which CONDITION was induced (surgery,
chemicals, diet, infection, implanted tumours including xenografts) or genetically engineered, AND in which DRUG
itself is the treatment under test? Answer false when DRUG is only a comparator, benchmark, positive control,
background or co-treatment for another compound (e.g. "comparable to the benchmark dexamethasone"), when the
condition studied is a different one, and for animals with naturally occurring disease, human studies, in vitro
studies, and pharmacokinetic, mechanism-only or toxicity-only studies. model: species and model as written.
result: positive if DRUG improved the condition's main efficacy outcome versus control; negative if it did not
improve it; unclear otherwise. Adverse effects of DRUG are not an efficacy result. result_sentence: copied, or
null. JSON only."""

SUPERMAJORITY = 0.75   # primary rule for a laboratory literature of many studies; unanimity reported as sensitivity

def combine(labels, rule="supermajority"):
    """Laboratory side from many studies. unanimous: positive/negative only if every classifiable study agrees.
    supermajority: positive/negative if at least 75% of classifiable studies agree, mixed otherwise."""
    c = collections.Counter(l for l in labels if l in ("positive", "negative"))
    n = sum(c.values())
    if n == 0:
        return "indeterminate"
    if rule == "unanimous":
        return "positive" if c["negative"] == 0 else "negative" if c["positive"] == 0 else "mixed"
    if c["positive"] / n >= SUPERMAJORITY:
        return "positive"
    if c["negative"] / n >= SUPERMAJORITY:
        return "negative"
    return "mixed"

def exact_diff_ci(b, c, alpha=0.05):
    """Paired difference (b - c)/n_discordant framing: CI for the share of discordant pairs favouring companion
    animals, via Clopper–Pearson on b of (b + c). Returns (share, lo, hi)."""
    n = b + c
    if n == 0:
        return None, None, None
    lo, hi = clopper_pearson(b, n, alpha)
    return b / n, lo, hi

def main():
    pairs = load("part2/pairs.json")
    attrs = load("part2/pair_attributes.json")
    out = load("part2/lab_models.json")
    targets = [k for k, p in pairs.items() if p.get("status") == "classified" and not p.get("flag")
               and p.get("pair_type", "efficacy") == "efficacy" and p["relation"] != "class-analogue"
               and attrs.get(k, {}).get("type") in PRIMARY_TYPES and p["judgement"]["human"] in ("positive", "negative", "mixed")]
    todo = [k for k in targets if k not in out]
    print(f"Q4 laboratory evidence: {len(targets)} pairs with a classifiable human side; {len(todo)} to build", flush=True)

    def build(k):
        p = pairs[k]
        names = p["ingredient"].split("+")
        cond_terms = p["terms"]["pubmed_condition_terms"][:3] or [p["terms"]["human_condition"]]
        drug = "(" + " OR ".join(f'"{x.lower()}"[tiab] OR "{x.lower()}"[nm]' for x in names) + ")"
        cond = "(" + " OR ".join(f'"{c}"[tiab]' for c in cond_terms) + ")"
        query = (f'{drug} AND {cond} AND ("Disease Models, Animal"[mh] OR "Mice"[mh] OR "Rats"[mh] OR mice[tiab] OR rats[tiab] '
                 f'OR murine[tiab] OR xenograft*[tiab] OR "animal model*"[tiab]) NOT ("client-owned"[tiab] OR "naturally occurring"[tiab] '
                 f'OR "pet dogs"[tiab]) NOT humans[mh:noexp]')
        with _ncbi:
            n, ids, _ = pubmed.esearch(query, retmax=MAX_LAB, sort="relevance")
            ab = efetch(ids)
        reads = {}
        for pm in ids:
            a = ab.get(pm)
            if a and a["abstract"]:
                try:
                    reads[pm], _ = ask(READ_MODEL, READ_SYS, f"DRUG: {' / '.join(names)}\nCONDITION: {p['terms']['human_condition']}\n\n{a['title']}\n{a['abstract']}",
                                       READ, max_tokens=800, deadline_s=60)
                except Exception as e:
                    reads[pm] = {"error": str(e)[:100]}
        lab = [r for r in reads.values() if r.get("lab_model_efficacy_study")]
        return {"query": query, "hits": n, "retrieved": ids, "reads": reads, "n_lab_studies": len(lab),
                "lab_side": combine([r["result"] for r in lab]),
                "lab_side_unanimous": combine([r["result"] for r in lab], "unanimous"), "date": today()}
    res = pmap(build, todo, workers=12, label="lab")
    out.update({k: r for k, r in res.items() if "error" not in r})
    save(out, "part2/lab_models.json")

    rules_out = []
    for rule_key, rule_name in (("lab_side", "primary rule: laboratory side positive/negative when at least 75% of studies agree"),
                                ("lab_side_unanimous", "sensitivity: laboratory side positive/negative only when every study agrees")):
        rules_out.append(compare(targets, pairs, out, rule_key, rule_name))
    L = ["# Q4: companion animals vs laboratory models, within drug (draft)", "", f"Built {today()} by `analysis/v04/d5_lab_models.py`.", "",
         f"- primary pairs with a classifiable human side: {len(targets)}",
         f"- laboratory side (primary rule): {dict(collections.Counter(out[k]['lab_side'] for k in targets if k in out))}",
         f"- laboratory side (unanimous rule): {dict(collections.Counter(out[k].get('lab_side_unanimous') for k in targets if k in out))}", ""]
    for block in rules_out:
        L += block
    L += breakdown(targets, pairs, out)
    L += ["", "Caveat: laboratory efficacy literature is biased towards positive results, which inflates laboratory agreement "
          "whenever the human result is positive; laboratory sides are read from abstracts."]
    open(os.path.join(V04, "part2", "q4_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

def breakdown(targets, pairs, out):
    """Where the comparison is informative. A laboratory literature that is almost always positive agrees with a
    positive human result automatically; predictive value shows only where the human result is negative."""
    attrs = load("part2/pair_attributes.json")
    side = lambda x: x if x in ("positive", "negative") else None
    rows = []
    for k in targets:
        if k not in out:
            continue
        j = pairs[k]["judgement"]
        h, c, l = side(j["human"]), side(j["veterinary"]), side(out[k]["lab_side"])
        if h and c and l:
            rows.append((h, c == h, l == h, attrs.get(k, {}).get("timing")))
    def line(title, rs):
        n = len(rs)
        if not n:
            return f"| {title} | 0 | — | — |"
        return f"| {title} | {n} | {sum(r[1] for r in rs)}/{n} ({sum(r[1] for r in rs)/n:.0%}) | {sum(r[2] for r in rs)}/{n} ({sum(r[2] for r in rs)/n:.0%}) |"
    L = ["## Breakdown (primary rule): where the comparison is informative", "",
         "| subset | pairs | companion animals matched humans | laboratory models matched humans |", "|---|---|---|---|",
         line("human result positive", [r for r in rows if r[0] == "positive"]),
         line("human result negative", [r for r in rows if r[0] == "negative"]),
         line("drug approved in humans before the veterinary evidence", [r for r in rows if r[3] == "human-approval-before-veterinary-evidence"]),
         line("drug approved in humans after the veterinary evidence", [r for r in rows if r[3] == "human-approval-after-veterinary-evidence"]),
         line("no US human approval", [r for r in rows if r[3] == "no-us-approval"]), "",
         "Laboratory sides are almost uniformly positive, so agreement on human-positive drugs is expected whatever the model's "
         "predictive value. Only the human-negative row tests prediction of failure.",
         "Laboratory reader: gemini-2.5-flash, audited 79% correct (42/53 reads; q4_reader_audit.md).", ""]
    return L

def compare(targets, pairs, out, rule_key, rule_name):
    def label(side, human):
        if side not in ("positive", "negative") or human not in ("positive", "negative"):
            return None
        return side == human
    both = []
    for k in targets:
        if k not in out:
            continue
        p = pairs[k]; j = p["judgement"]
        comp, labc = label(j["veterinary"], j["human"]), label(out[k].get(rule_key), j["human"])
        if comp is not None and labc is not None:
            both.append((k, comp, labc))
    a = sum(1 for _, c, l in both if c and l); b = sum(1 for _, c, l in both if c and not l)
    c_ = sum(1 for _, c, l in both if not c and l); d = sum(1 for _, c, l in both if not c and not l)
    n = len(both)
    comp_rate = (a + b) / n if n else None
    lab_rate = (a + c_) / n if n else None
    share, lo, hi = exact_diff_ci(b, c_)
    L = [f"## {rule_name}", "", f"- pairs where companion, laboratory and human sides are all positive or negative: {n}", ""]
    if n:
        L += ["| | laboratory concordant | laboratory discordant |", "|---|---|---|",
              f"| **companion concordant** | {a} | {b} |", f"| **companion discordant** | {c_} | {d} |", "",
              f"- companion-animal concordance: {a+b}/{n} = {comp_rate:.0%}; laboratory-model concordance: {a+c_}/{n} = {lab_rate:.0%}",
              f"- pairs where only one agreed with humans: {b + c_}; companion animals were the one in {b} "
              + (f"({share:.0%}, exact 95% CI {lo:.0%}–{hi:.0%})" if share is not None else "(none)"), ""]
        if share is None or (lo <= 0.5 <= hi):
            L.append("**F1 statement:** concordance with human outcomes did not differ detectably between companion animals with "
                     "naturally occurring disease and laboratory models of the same drug and condition.")
        elif lo > 0.5:
            L.append("**F1 statement:** where the two disagreed, companion animals matched the human outcome more often than laboratory models.")
        else:
            L.append("**F1 statement:** where the two disagreed, laboratory models matched the human outcome more often than companion animals.")
    return L + [""]

if __name__ == "__main__":
    main()
