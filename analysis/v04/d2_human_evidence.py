"""Part 2, step 2: human evidence and pair classification for each candidate drug × indication (amendment A6).

For every candidate from d1, grouped by ingredient, relation and CANONICAL veterinary condition (step 0):
  0. For each ingredient, one model call merges the free-text indications of its records into canonical
     conditions ("osteosarcoma", "canine appendicular osteosarcoma" -> one condition). Procedure-based
     indications ("ovariohysterectomy", "castration") are named by purpose ("perioperative analgesia",
     "anaesthetic induction"); records of healthy animals or non-treatment use are marked not-a-condition.
  1. One model names the corresponding human condition and 1-3 PubMed condition terms. These are search
     terms only; the classification relies on retrieved records.
  2. PubMed search, human studies of the drug in that condition, ranked by relevance. Results come from the
     highest-level publication types first (meta-analyses, RCTs, phase 3, phase 2), then other clinical
     studies. Up to 40 records per pair.
  3. A fast model marks each abstract: relevant (drug tested in that condition, original results or pooled
     analysis), design, and result sentence.
  4. A strong model (claude-sonnet-5) classifies both sides from the veterinary record, the relevant human
     abstracts and the US label indications for the ingredient, following §7.4 / A5 §4 / F4:
       - veterinary side and human side each: positive / negative / mixed / indeterminate;
       - human evidence taken from the highest level present: US approval for the indication, then
         phase 3 / pivotal RCT or meta-analysis, then phase 2, then earlier;
       - pair: concordant / discordant (all evidence opposite) / mixed / indeterminate.
     Every citation it gives must be a PMID from the retrieved set (checked in code) or a label key.

Output: data/v04/part2/pairs.json, data/v04/part2/pairs_report.md
"""
import sys, os, re, collections, threading
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
import pubmed
from d1_candidates import efetch

TERMS_MODEL, READ_MODEL, JUDGE_MODEL = "openai/gpt-4.1-mini", "google/gemini-2.5-flash-lite", "anthropic/claude-sonnet-5"
MAX_HUMAN = 40
_ncbi = threading.Semaphore(3)

TERMS = {"type": "object", "additionalProperties": False, "properties": {
    "human_condition": {"type": "string"}, "no_human_counterpart": {"type": "boolean"},
    "treatment_intent": {"type": "string"}, "pubmed_condition_terms": {"type": "array", "items": {"type": "string"}}},
    "required": ["human_condition", "no_human_counterpart", "treatment_intent", "pubmed_condition_terms"]}
TERMS_SYS = """A drug was tested in dogs or cats with a naturally occurring condition. Name the corresponding
human condition. If the treatment is symptomatic or preventive (pain relief, anaesthesia, clot prevention),
name the human condition by that purpose (e.g. "postoperative pain", "venous thromboembolism prevention")
and set treatment_intent to symptomatic or preventive; otherwise disease-modifying. For parasitic or
infectious disease, the human counterpart must involve the same organism or the same genus in the same organ
system. no_human_counterpart: true if the condition has no human counterpart under these rules.
pubmed_condition_terms: 1-3 short PubMed title/abstract terms for the human condition. JSON only."""

READ = {"type": "object", "additionalProperties": False, "properties": {
    "relevant": {"type": "boolean"}, "design": {"type": "string"}, "phase": {"type": "string"}, "result_sentence": {"type": ["string", "null"]}},
    "required": ["relevant", "design", "phase", "result_sentence"]}
READ_SYS = """Is this a report of original results (or a pooled/systematic analysis) of giving DRUG to HUMANS
with CONDITION or its direct counterpart, where DRUG is the treatment under test (not only a comparator or
background)? design: meta-analysis | randomized-controlled | single-arm | observational | review-no-data |
other. phase: phase-3 | phase-2 | phase-1 | not-stated. result_sentence: the main efficacy result, copied,
or null. JSON only."""

SIDE = {"type": "string", "enum": ["positive", "negative", "mixed", "indeterminate"]}
JUDGE = {"type": "object", "additionalProperties": False, "properties": {
    "veterinary": SIDE, "veterinary_basis": {"type": "string"},
    "human_top_level": {"type": "string", "enum": ["us-approval", "phase-3-or-meta-analysis", "phase-2", "earlier", "none"]},
    "human": SIDE, "human_basis": {"type": "string"},
    "human_citations": {"type": "array", "items": {"type": "string"}},
    "pair": {"type": "string", "enum": ["concordant", "discordant", "mixed", "indeterminate"]},
    "caveats": {"type": "string"}},
    "required": ["veterinary", "veterinary_basis", "human_top_level", "human", "human_basis", "human_citations", "pair", "caveats"]}
JUDGE_SYS = """You classify one drug pair: the same drug (or a species-specific version of the same biologic)
tested in dogs or cats with naturally occurring disease and in humans with the corresponding condition.

Veterinary side, from the veterinary record(s):
- positive: an RCT met its primary efficacy endpoint or showed the drug superior to control or comparator;
  a non-inferiority margin was met; or a single-arm cancer study had an objective response rate of at least
  20%, or a single-arm non-cancer study improved a validated outcome.
- negative: ONLY a controlled trial that failed its primary endpoint against placebo or no treatment, or
  development stopped for lack of efficacy. A single-arm study below the response threshold, a small pilot,
  a case series or any uncontrolled study is indeterminate, never negative.
- mixed: records disagree.
- indeterminate: otherwise (e.g. dose-finding or tolerability only).

Human side, using ONLY the highest level of evidence present:
  US approval for the indication (a label indication covers the condition)
  > phase 3 / pivotal RCT / meta-analysis
  > phase 2
  > earlier.
Within that level: positive if all studies are positive; negative if all are negative; mixed if both;
indeterminate if none can be classified.

Pair:
- concordant: both positive, or both negative.
- discordant: one side positive and the other negative, with no mixed evidence.
- mixed: either side is mixed.
- indeterminate: either side is indeterminate.

human_citations: PMIDs from the HUMAN RECORDS list, or label keys (e.g. L2), that the human classification
rests on. Cite nothing that is not listed. Bases: two sentences at most, with numbers. JSON only."""

CANON = {"type": "object", "additionalProperties": False, "properties": {
    "mapping": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
        "indication": {"type": "string"}, "canonical_condition": {"type": "string"}, "not_a_condition": {"type": "boolean"}},
        "required": ["indication", "canonical_condition", "not_a_condition"]}}},
    "required": ["mapping"]}
CANON_SYS = """You receive the indications, as written, of veterinary studies of one DRUG in dogs or cats. Map each
indication to a short canonical condition. Use the FEWEST distinct conditions:
- drop species words ("canine", "feline", "in cats");
- merge anatomical subtypes, stages and wording variants into the parent disease when the human counterpart
  is the same disease ("appendicular osteosarcoma", "osteosarcoma metastases" -> "osteosarcoma"; "systemic
  hypertension", "hypertension in cats" -> "hypertension"; "lower urinary tract carcinoma", "transitional
  cell carcinoma of the bladder" -> "urothelial carcinoma");
- keep conditions separate only when their human counterparts differ.
Name procedure-based uses by purpose ("ovariohysterectomy" analgesia -> "perioperative analgesia";
"induction of anaesthesia" -> "anaesthesia").
not_a_condition: true for healthy animals, pharmacokinetic or blank indications, and for non-specific
mixtures such as "cancer", "solid tumours", "malignant neoplasms", "refractory tumours".
Return one entry per input indication, copying the indication exactly. JSON only."""

def canonical_groups(cands):
    by_ing = collections.defaultdict(set)
    for c in cands:
        by_ing[c["ingredient"]].add((c["indication"] or "").strip())
    cp = os.path.join(V04, "part2", "canonical_indications.json")
    known = load(cp, {})
    todo = [i for i in by_ing if i not in known]
    def run(ing):
        r, _ = ask(TERMS_MODEL, CANON_SYS, f"DRUG: {ing}\nINDICATIONS:\n" + "\n".join(f"- {x or '(blank)'}" for x in sorted(by_ing[ing])),
                   CANON, max_tokens=6000, deadline_s=120)
        return {m["indication"]: m for m in r["mapping"]}
    res = pmap(run, todo, workers=24, label="canonical")
    for ing, m in res.items():
        known[ing] = m if "error" not in m else {}
    save(known, cp)
    groups, dropped = collections.defaultdict(list), collections.Counter()
    for c in cands:
        if not (c.get("efficacy_result") or "").strip():
            dropped["no-efficacy-result"] += 1; continue
        m = known.get(c["ingredient"], {}).get((c["indication"] or "").strip()) or known.get(c["ingredient"], {}).get("(blank)")
        if m and m["not_a_condition"]:
            dropped["not-a-condition"] += 1; continue
        cond = (m["canonical_condition"] if m else (c["indication"] or "unmapped")).strip().lower()
        if c["relation"] == "same-molecule":
            groups[(c["ingredient"], c["relation"], cond)].append(c)
        else:   # all human counterparts of one veterinary biologic or class form ONE pair (e.g. tanezumab+fasinumab)
            groups[(("VET:" + c["agent_as_written"].lower()), c["relation"], cond)].append(c)
    merged = {}
    for (ing, rel, cond), recs in groups.items():
        if ing.startswith("VET:"):
            label = "+".join(sorted({r["ingredient"] for r in recs}))
            merged.setdefault((label, rel, cond), [])
            seen = {r["record"] for r in merged[(label, rel, cond)]}
            merged[(label, rel, cond)] += [r for r in recs if r["record"] not in seen]
        else:
            merged[(ing, rel, cond)] = recs
    groups = merged
    print(f"canonical grouping: {len(groups)} drug × condition groups; dropped {dict(dropped)}", flush=True)
    return groups

def main():
    d1 = load("part2/candidates.json")
    index = load("frames/human_index.json")
    groups = canonical_groups(d1["candidates"])
    only = {x.strip().upper() for x in os.environ.get("AMC_D2_ONLY", "").split(",") if x.strip()}
    if only:   # test runs on named ingredients; the full run leaves this unset
        groups = {k: v for k, v in groups.items() if k[0] in only}
        print(f"AMC_D2_ONLY: restricted to {len(groups)} groups for {sorted(only)}", flush=True)
    out = load("part2/pairs.json")
    keys = [k for k in groups if "|".join(k) not in out]
    print(f"pairs to build: {len(keys)} (of {len(groups)} drug × indication groups)", flush=True)

    def build(key):
        ing, rel, ind = key
        recs = groups[key]
        names = ing.split("+")
        pair_type = "safety" if re.search(r"adverse|toxicit|safety|side effect", ind) else "efficacy"
        sp = sorted({r["species"] for r in recs})
        t, _ = ask(TERMS_MODEL, TERMS_SYS, f"DRUG: {ing}\nVETERINARY CONDITION: {ind} (species: {', '.join(sp)})", TERMS, max_tokens=800, deadline_s=60)
        base = {"ingredient": ing, "relation": rel, "pair_type": pair_type, "veterinary_indication": ind, "species": sp, "records": [r["record"] for r in recs],
                "sources": sorted({r["source"] for r in recs}), "terms": t, "date": today()}
        if t["no_human_counterpart"]:
            return {**base, "status": "no-human-counterpart"}
        cond = " OR ".join(f'"{x}"[tiab]' for x in t["pubmed_condition_terms"][:3]) or f'"{t["human_condition"]}"[tiab]'
        drug = "(" + " OR ".join(f'"{x.lower()}"[tiab] OR "{x.lower()}"[nm]' for x in names) + ")"
        hi = f'{drug} AND ({cond}) AND humans[mh] AND ("Meta-Analysis"[pt] OR "Randomized Controlled Trial"[pt] OR "Clinical Trial, Phase III"[pt] OR "Clinical Trial, Phase II"[pt])'
        lo = f'{drug} AND ({cond}) AND humans[mh] AND ("Clinical Trial"[pt] OR "Observational Study"[pt] OR "Systematic Review"[pt])'
        with _ncbi:
            n_hi, ids_hi, _ = pubmed.esearch(hi, retmax=MAX_HUMAN, sort="relevance")
            n_lo, ids_lo, _ = pubmed.esearch(lo, retmax=MAX_HUMAN, sort="relevance")
        ids = list(dict.fromkeys(ids_hi + ids_lo))[:MAX_HUMAN]
        with _ncbi:
            ab = efetch(ids + [r["record"][5:] for r in recs if r["record"].startswith("PMID:")])
        reads = {}
        for pm in ids:
            a = ab.get(pm)
            if a and a["abstract"]:
                try:
                    reads[pm], _ = ask(READ_MODEL, READ_SYS, f"DRUG: {ing}\nCONDITION: {t['human_condition']}\n\n{a['title']}\n{a['abstract']}", READ, max_tokens=800, deadline_s=60)
                except Exception as e:
                    reads[pm] = {"error": str(e)[:100]}
        rel_ids = [pm for pm, r in reads.items() if r.get("relevant")]
        labels = {}
        for i, (sid, lab) in enumerate(sorted(((s, l) for nm_ in names for s, l in (index.get(nm_, {}).get("labels") or {}).items()
                                               if l["product_type"] == "HUMAN PRESCRIPTION DRUG" and l["indications"]),
                                              key=lambda x: x[1]["effective_time"], reverse=True)[:6]):
            labels[f"L{i}"] = {"set_id": sid, "brand": lab["brand"], "application": lab["application_number"], "indications": lab["indications"][:1500]}
        vet_text = "\n\n".join(f"[{r['record']}] {r['title']} ({r['year']}) design={r['design']}\nEfficacy: {r['efficacy_result']}" +
                               (f"\nAbstract: {ab.get(r['record'][5:], {}).get('abstract', '')[:2500]}" if r["record"].startswith("PMID:") else "")
                               for r in recs[:6])
        human_text = "\n\n".join(f"[PMID {pm}] {ab[pm]['title']} ({ab[pm]['year']}) design={reads[pm]['design']} phase={reads[pm]['phase']}\n"
                                 f"Result: {reads[pm]['result_sentence']}\nAbstract: {ab[pm]['abstract'][:1800]}" for pm in rel_ids[:20])
        label_text = "\n".join(f"[{k}] {v['brand']} ({v['application']}): {v['indications']}" for k, v in labels.items()) or "(no US prescription label for this ingredient)"
        user = (f"DRUG: {ing} (relation: {rel})\nVETERINARY CONDITION: {ind}; species {', '.join(sp)}\n"
                f"HUMAN CONDITION: {t['human_condition']} (intent: {t['treatment_intent']})\n\n"
                f"VETERINARY RECORDS:\n{vet_text}\n\nUS LABELS:\n{label_text}\n\nHUMAN RECORDS ({len(rel_ids)} relevant of {len(ids)} retrieved):\n{human_text or '(none)'}")
        j, _ = ask(JUDGE_MODEL, JUDGE_SYS, user, JUDGE, max_tokens=4000, deadline_s=300)
        allowed = set(rel_ids) | set(labels)
        norm_c = lambda c: re.sub(r"\D", "", c) if re.search(r"\d{5,}", c) else c.strip()
        bad = [c for c in j["human_citations"] if norm_c(c) not in allowed]
        return {**base, "status": "classified", "human_query_high": hi, "human_query_low": lo, "hits_high": n_hi, "hits_low": n_lo,
                "retrieved": ids, "relevant": rel_ids, "reads": reads, "labels": labels, "judgement": j,
                "invalid_citations": bad, "flag": bool(bad)}
    res = pmap(build, keys, workers=12, label="pairs")
    for k, r in res.items():
        out["|".join(k)] = r
    save(out, "part2/pairs.json")

    cl = [p for p in out.values() if p.get("status") == "classified"]
    L = ["# Part 2 drug pairs (draft)", "", f"Built {today()} by `analysis/v04/d2_human_evidence.py` (judge {JUDGE_MODEL}).", "",
         f"- drug × indication groups: {len(out)}",
         f"- status: {dict(collections.Counter(p.get('status', 'error') for p in out.values()))}",
         f"- judgements with a citation outside the retrieved set: {sum(1 for p in cl if p['flag'])}", ""]
    for ptype, rel in [(t, r) for t in ("efficacy", "safety") for r in ("same-molecule", "species-specific-biologic", "class-analogue")]:
        sub = [p for p in cl if p["relation"] == rel and p.get("pair_type", "efficacy") == ptype]
        if not sub:
            continue
        cnt = collections.Counter(p["judgement"]["pair"] for p in sub)
        L += [f"## {ptype} · {rel}: {len(sub)} pairs — {dict(cnt)}", "",
              "| drug | vet indication | species | vet | human (level) | pair | sources |", "|---|---|---|---|---|---|---|"]
        for p in sorted(sub, key=lambda p: (p["judgement"]["pair"], p["ingredient"])):
            j = p["judgement"]
            L.append(f"| {p['ingredient']} | {p['veterinary_indication'][:50]} | {', '.join(p['species'])} | {j['veterinary']} | "
                     f"{j['human']} ({j['human_top_level']}) | **{j['pair']}** | {', '.join(s.split(':')[0] for s in p['sources'])} |")
        L.append("")
    L.append(f"Cost (uncached): ${COST['usd']:.2f}")
    open(os.path.join(V04, "part2", "pairs_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))

if __name__ == "__main__":
    main()
