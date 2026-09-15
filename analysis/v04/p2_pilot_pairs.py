"""Step 1b, part 2 — build and classify pilot drug pairs (PLAN.md v0.4 §7.3-7.4).

For each qualifying candidate, in the seeded screening order, until 10 pairs have a human result:
  1. Two models name the human-medicine form of each agent and the human counterpart of the
     indication. These are search terms only; nothing downstream trusts them as facts.
  2. Human evidence is retrieved, not recalled: PubMed human clinical studies of the agent in the
     condition, ClinicalTrials.gov registrations, and FDA drug labels (openFDA).
  3. Two models extract, from each retrieved record, the fields §7.4 needs (design, whether an RCT
     met its primary endpoint, objective response rate, safety signal) with exact quotes.
  4. Classification is deterministic code applying §7.4, at the primary ORR threshold (20%) and
     the two pre-specified sensitivity thresholds (10%; any response).
Every disagreement between the two models is kept as a flag for human review.

Output: data/v04/pilot/pairs.json, data/v04/pilot/pilot_report.md
"""
import sys, os, re, json, time, urllib.request, urllib.parse, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
import pubmed
from p1_pilot_screen import efetch_abstracts

TARGET_PAIRS = 10
MAX_HUMAN_RECORDS = 12
THRESHOLDS = {"primary_orr20": 20.0, "sens_orr10": 10.0, "sens_any_response": 0.0001}

# --- 1. search terms -------------------------------------------------------------------------
TERMS = {"type": "object", "additionalProperties": False, "properties": {
    "agents": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
        "as_written": {"type": "string"},
        "human_generic_name": {"type": ["string", "null"]},
        "human_equivalent_note": {"type": "string"}},
        "required": ["as_written", "human_generic_name", "human_equivalent_note"]}},
    "human_condition": {"type": ["string", "null"]},
    "condition_search_terms": {"type": "array", "items": {"type": "string"}}},
    "required": ["agents", "human_condition", "condition_search_terms"]}
TERMS_SYS = """A veterinary study treated animals with the agents below for the condition below.
For each agent give the generic name of the same molecule (or the same-target human product if
the veterinary product is a species-specific version of a human antibody or protein) as used in
human medicine, or null if there is none. Give the human counterpart of the condition and 1-3
PubMed search terms for it. These are search terms; say "uncertain" in the note when unsure.
Answer with JSON only."""

# --- 3. per-record extraction ----------------------------------------------------------------
REC = {"type": "object", "additionalProperties": False, "properties": {
    "relevant": {"type": "boolean"},
    "population": {"type": "string", "enum": ["human", "dog", "cat", "other", "unclear"]},
    "agent_tested": {"type": "boolean"},
    "condition_matches": {"type": "string", "enum": ["same", "related", "different", "unclear"]},
    "design": {"type": "string", "enum": ["randomized-controlled", "single-arm", "dose-escalation",
               "observational", "review-or-other", "not-stated"]},
    "n": {"type": ["integer", "null"]},
    "oncology": {"type": "boolean"},
    "rct_met_primary_endpoint": {"type": "string", "enum": ["yes", "no", "not-applicable", "unclear"]},
    "objective_response_rate_percent": {"type": ["number", "null"]},
    "any_objective_response": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "validated_outcome_improved": {"type": "string", "enum": ["yes", "no", "not-applicable", "unclear"]},
    "stopped_for_lack_of_efficacy": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "safety_signal": {"type": "string", "enum": ["signal", "no-signal", "indeterminate"]},
    "safety_organ_system": {"type": ["string", "null"]},
    "efficacy_quote": {"type": ["string", "null"]},
    "safety_quote": {"type": ["string", "null"]}},
    "required": ["relevant", "population", "agent_tested", "condition_matches", "design", "n", "oncology",
                 "rct_met_primary_endpoint", "objective_response_rate_percent", "any_objective_response",
                 "validated_outcome_improved", "stopped_for_lack_of_efficacy", "safety_signal",
                 "safety_organ_system", "efficacy_quote", "safety_quote"]}
REC_SYS = """Extract from this record what was done and found. Answer only from the record; use
"unclear" or null when it does not say.
relevant: the record reports original results of giving AGENT to patients or animals with
  CONDITION (or a closely related condition). Reviews, protocols without results, and preclinical
  laboratory studies are not relevant.
rct_met_primary_endpoint: for randomized controlled trials only; "yes" only if the record says the
  primary endpoint was met / significantly improved.
objective_response_rate_percent: complete + partial responses as a percentage of treated subjects,
  if stated or directly computable from stated counts.
validated_outcome_improved: non-cancer studies; a pre-specified or validated clinical outcome
  measure improved.
safety_signal: "signal" if dose-limiting toxicity, serious or treatment-limiting adverse events,
  or label-relevant toxicity is reported; "no-signal" if the record states treatment was well
  tolerated without such events; else "indeterminate".
Quotes: copy the exact sentence, or null.
Answer with JSON only."""

def search_human(agent, cond_terms):
    cond = " OR ".join(f'"{c}"[tiab]' for c in cond_terms) or "humans[mh]"
    q = (f'("{agent}"[tiab] OR "{agent}"[nm]) AND ({cond}) AND humans[mh] NOT (dogs[mh] OR cats[mh]) '
         f'AND ("Clinical Trial"[pt] OR "clinical trial"[tiab] OR "phase II"[tiab] OR "phase III"[tiab] '
         f'OR "phase I"[tiab] OR randomized[tiab])')
    n, ids, _ = pubmed.esearch(q, retmax=MAX_HUMAN_RECORDS, sort="relevance")
    return q, n, ids

def ctgov(agent, condition):
    q = urllib.parse.urlencode({"query.intr": agent, "query.cond": condition or "", "pageSize": 50,
                                "fields": "NCTId,BriefTitle,Phase,OverallStatus,HasResults,WhyStopped"})
    cp = os.path.join(CACHE, "text", f"ctgov_{sha(q)[:20]}.json")
    if os.path.exists(cp):
        return json.load(open(cp))
    d = json.loads(urllib.request.urlopen(f"https://clinicaltrials.gov/api/v2/studies?{q}", timeout=60).read())
    rows = []
    for s in d.get("studies", []):
        p = s.get("protocolSection", {})
        rows.append({"nct": p.get("identificationModule", {}).get("nctId"),
                     "title": p.get("identificationModule", {}).get("briefTitle"),
                     "phase": p.get("designModule", {}).get("phases"),
                     "status": p.get("statusModule", {}).get("overallStatus"),
                     "why_stopped": p.get("statusModule", {}).get("whyStopped"),
                     "has_results": s.get("hasResults")})
    json.dump(rows, open(cp, "w"))
    return rows

def fda_label(agent):
    q = urllib.parse.urlencode({"search": f'openfda.generic_name:"{agent}"', "limit": 3})
    cp = os.path.join(CACHE, "text", f"openfda_{sha(q)[:20]}.json")
    if os.path.exists(cp):
        return json.load(open(cp))
    try:
        d = json.loads(urllib.request.urlopen(f"https://api.fda.gov/drug/label.json?{q}", timeout=60).read())
        rows = [{"brand": (r.get("openfda", {}).get("brand_name") or [None])[0],
                 "indications": " ".join(r.get("indications_and_usage", []))[:1500]} for r in d.get("results", [])]
    except urllib.error.HTTPError as e:
        rows = [] if e.code == 404 else [{"error": f"HTTP {e.code}"}]
    json.dump(rows, open(cp, "w"))
    return rows

# --- 4. deterministic classification (§7.4) --------------------------------------------------
def classify_record(r, thr):
    if not r.get("relevant") or not r.get("agent_tested"):
        return None
    if r["design"] == "randomized-controlled" and r["rct_met_primary_endpoint"] in ("yes", "no"):
        return "positive" if r["rct_met_primary_endpoint"] == "yes" else "negative"
    if r["stopped_for_lack_of_efficacy"] == "yes":
        return "negative"
    if r["design"] in ("single-arm", "dose-escalation"):
        if r["oncology"]:
            orr = r["objective_response_rate_percent"]
            if orr is None and thr < 1 and r["any_objective_response"] == "yes":
                return "positive"
            if orr is not None:
                return "positive" if orr >= thr else "indeterminate"
        elif r["validated_outcome_improved"] == "yes":
            return "positive"
    return "indeterminate"

def combine(labels):
    """F4: discordant/negative only when all available evidence points that way."""
    s = {l for l in labels if l and l != "indeterminate"}
    if not s:
        return "indeterminate"
    if s == {"positive"}:
        return "positive"
    if s == {"negative"}:
        return "negative"
    return "mixed"

def pair_label(animal, human):
    if "indeterminate" in (animal, human):
        return "indeterminate"
    if "mixed" in (animal, human):
        return "mixed"
    return "concordant" if animal == human else "discordant"

def safety_combine(records):
    s = {r["safety_signal"] for r in records if r and r.get("relevant") and r["safety_signal"] != "indeterminate"}
    return "indeterminate" if not s else ("mixed" if len(s) > 1 else s.pop())

def consensus(a, b, fields):
    """Field-level agreement between the two models' extractions of one record."""
    return [f for f in fields if a.get(f) != b.get(f)]

KEY_FIELDS = ["relevant", "agent_tested", "design", "rct_met_primary_endpoint",
              "objective_response_rate_percent", "stopped_for_lack_of_efficacy", "safety_signal"]

# Three layers of parallelism: candidates -> human records -> API calls. Each layer has its own
# pool so a blocked outer task never waits on a slot in its own pool; the API-slot semaphore in
# common.ask caps real concurrent calls.
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
_api_pool = ThreadPoolExecutor(max_workers=96)
_rec_pool = ThreadPoolExecutor(max_workers=48)
_ncbi = threading.Semaphore(3)          # NCBI allows ~3 requests/second without an API key

def ncbi(fn, *a):
    for attempt in range(5):
        try:
            with _ncbi:
                return fn(*a)
        except Exception:
            if attempt == 4:
                raise
            time.sleep(1.5 * (attempt + 1))

def both(t, system, user, schema, max_tokens=8000):
    fa = _api_pool.submit(ask, LADDER[t]["A"], system, user, schema, None, max_tokens)
    fb = _api_pool.submit(ask, LADDER[t]["B"], system, user, schema, None, max_tokens)
    return fa.result()[0], fb.result()[0]

def extract_both(t, text, agent, condition):
    """A failed call (after ask's retries) yields (None, None) and is flagged, never fatal."""
    try:
        return both(t, REC_SYS, f"AGENT: {agent}\nCONDITION: {condition}\n\nRECORD:\n{text}", REC)
    except Exception:
        return None, None

def process(c, t):
    a = c["A"]
    agents, indication, species = a["agents"], a["indication"], a["species"]
    flags = []
    if sorted(map(str.lower, a["agents"])) != sorted(map(str.lower, c["B"]["agents"])):
        flags.append(f"screen models disagree on agents: A={a['agents']} B={c['B']['agents']}")
    if c["id"].startswith("PMID:"):
        ab = ncbi(efetch_abstracts, [c["id"][5:]])[c["id"][5:]]
        text_animal = f"{ab['title']}\n{ab['abstract']}"
    else:
        cotc = {("COTC:" + x["trial_id"]): x for x in load("frames/cotc.json")["trials"]}[c["id"]]
        text_animal = f"{cotc['title']}\n{cotc['purpose']}\nPublications: {'; '.join(cotc['publications'])}"

    terms_f = _rec_pool.submit(both, t, TERMS_SYS, f"AGENTS: {agents}\nCONDITION: {indication}\nSPECIES: {species}", TERMS, 4000)
    animal_f = _rec_pool.submit(extract_both, t, text_animal, ", ".join(agents), indication)
    terms_a, terms_b = terms_f.result()
    names = sorted({x["human_generic_name"].lower() for tt in (terms_a, terms_b) for x in tt["agents"] if x["human_generic_name"]})
    cond_terms = sorted({s for tt in (terms_a, terms_b) for s in tt["condition_search_terms"]})[:4]
    human_condition = terms_a["human_condition"] or terms_b["human_condition"]
    base = {"candidate": c["id"], "title": c["title"], "year": c.get("year"), "species": species,
            "agents": agents, "indication": indication, "human_agent_names": names,
            "human_condition": human_condition, "search_terms": {"A": terms_a, "B": terms_b},
            "rank": c["rank"], "tier": t, "date": today()}
    if not names:
        animal_f.cancel()
        return {**base, "status": "no-human-counterpart-agent", "flags": flags}

    animal_a, animal_b = animal_f.result()
    if animal_a is None or animal_b is None:
        return {**base, "status": "error", "flags": flags + ["animal-side extraction failed after retries"]}
    animal_diff = consensus(animal_a, animal_b, KEY_FIELDS)
    if animal_diff:
        flags.append(f"animal-side extraction disagreement on {animal_diff}")

    searches, jobs = [], []
    for nm in names:
        q, n, ids = ncbi(search_human, nm, cond_terms)
        searches.append({"agent": nm, "query": q, "hits": n, "retrieved": ids})
        abst = ncbi(efetch_abstracts, ids) if ids else {}
        for pm in ids:
            txt = f"{abst.get(pm, {}).get('title','')}\n{abst.get(pm, {}).get('abstract','')}"
            jobs.append((nm, pm, abst.get(pm, {}), _rec_pool.submit(extract_both, t, txt, nm, human_condition)))
    reg_f = {nm: _rec_pool.submit(ctgov, nm, human_condition) for nm in names}
    lab_f = {nm: _rec_pool.submit(fda_label, nm) for nm in names}
    human = []
    for nm, pm, meta, f in jobs:
        ra, rb = f.result()
        if ra is None or rb is None:
            flags.append(f"human record {pm}: extraction failed after retries (not counted)")
            continue
        human.append({"pmid": pm, "agent": nm, "title": meta.get("title"), "year": meta.get("year"),
                      "A": ra, "B": rb, "disagree": consensus(ra, rb, KEY_FIELDS)})
    registry = {nm: f.result() for nm, f in reg_f.items()}
    labels = {nm: f.result() for nm, f in lab_f.items()}

    rel = [h for h in human if h["A"]["relevant"] and h["B"]["relevant"] and h["A"]["population"] == "human"]
    for h in human:
        if h["A"]["relevant"] != h["B"]["relevant"]:
            flags.append(f"human record {h['pmid']}: models disagree on relevance")
        elif h["disagree"] and h["A"]["relevant"]:
            flags.append(f"human record {h['pmid']}: disagreement on {h['disagree']}")
    cls = {}
    for key, thr in THRESHOLDS.items():
        an = combine([classify_record(animal_a, thr)]) if not animal_diff else \
             combine([classify_record(animal_a, thr), classify_record(animal_b, thr)])
        hu = combine([classify_record(h["A"], thr) for h in rel])
        cls[key] = {"animal": an, "human": hu, "pair": pair_label(an, hu)}
    safety = {"animal": safety_combine([animal_a]), "human": safety_combine([h["A"] for h in rel])}
    safety["pair"] = pair_label(*(("positive" if x == "signal" else "negative" if x == "no-signal" else x)
                                  for x in (safety["animal"], safety["human"])))
    return {**base, "animal_extraction": {"A": animal_a, "B": animal_b}, "human_searches": searches,
            "human_records": human, "human_records_relevant": len(rel), "clinicaltrials_gov": registry,
            "fda_labels": labels, "classification": cls, "safety": safety, "flags": flags,
            "status": "pair" if rel else "no-human-result-retrieved"}

WAVE = 12

def main():
    screen = load("pilot/screen.json")
    # screen.json preserves the seeded screening order; rank is the position in that order
    cand = []
    for rank, v in enumerate(screen.values()):
        if v["qualifies"]:
            cand.append({**v, "rank": rank})
    t = tier("pilot")
    pairs = load("pilot/pairs.json")
    i = 0
    with ThreadPoolExecutor(max_workers=WAVE) as ex:
        # Errored candidates are retried first: the pilot set is "first N pairs in screening order",
        # so an unresolved error ahead of the Nth pair would make that set wrong.
        retry = [c for c in cand if c["id"] in pairs and pairs[c["id"]]["status"] == "error"]
        futs = {ex.submit(process, c, t): c for c in retry}
        for f in as_completed(futs):
            c = futs[f]
            try:
                rec = f.result()
            except Exception as e:
                rec = {"candidate": c["id"], "title": c["title"], "rank": c["rank"], "status": "error",
                       "flags": [f"processing failed: {type(e).__name__}: {str(e)[:200]}"]}
            pairs[c["id"]] = rec
            save(pairs, "pilot/pairs.json")
            print(f"  retry {c['id']}: {rec['status']} | relevant human {rec.get('human_records_relevant', 0)}", flush=True)
        while i < len(cand) and sum(1 for p in pairs.values() if p["status"] == "pair") < TARGET_PAIRS:
            wave = [c for c in cand[i:i + WAVE] if c["id"] not in pairs or pairs[c["id"]]["status"] == "error"]
            i += WAVE
            futs = {ex.submit(process, c, t): c for c in wave}
            for f in as_completed(futs):
                c = futs[f]
                try:
                    rec = f.result()
                except Exception as e:
                    rec = {"candidate": c["id"], "title": c["title"], "rank": c["rank"], "status": "error",
                           "flags": [f"processing failed: {type(e).__name__}: {str(e)[:200]}"]}
                pairs[c["id"]] = rec
                save(pairs, "pilot/pairs.json")
                lab = rec.get("classification", {}).get("primary_orr20", {}).get("pair", "-")
                print(f"  {c['id']}: {c['A']['agents']} -> {rec.get('human_agent_names')} | {rec['status']} | "
                      f"relevant human {rec.get('human_records_relevant', 0)} | pair(20%) {lab} | flags {len(rec.get('flags', []))}"
                      f"   ${COST['usd']:.3f}", flush=True)
    # The pilot set is the first TARGET_PAIRS pairs in screening order, not the first to finish.
    ranked = sorted((p for p in pairs.values() if p["status"] == "pair"), key=lambda p: p["rank"])
    keep = {p["candidate"] for p in ranked[:TARGET_PAIRS]}
    for p in pairs.values():
        p["pilot_set"] = p["candidate"] in keep
    save(pairs, "pilot/pairs.json")
    report(pairs, screen)

def report(pairs, screen):
    lines = ["# Step 1b — drug-pair pilot", "",
             f"Generated {today()} by `analysis/v04/p2_pilot_pairs.py`. Tier-1 models throughout.", "",
             "## Denominator", "",
             f"- screened from frames (seeded random order): {len(screen)}",
             f"- qualifying (both models: intervention, spontaneous disease, dog/cat, drug/biologic/cell/vaccine): "
             f"{sum(1 for v in screen.values() if v['qualifies'])}",
             f"- screening disagreements flagged: {sum(1 for v in screen.values() if v['flag'])}",
             f"- candidates processed for human counterpart: {len(pairs)}",
             f"- no human-medicine agent named by either model: {sum(1 for p in pairs.values() if p['status']=='no-human-counterpart-agent')}",
             f"- human agent named but no relevant human clinical record retrieved: {sum(1 for p in pairs.values() if p['status']=='no-human-result-retrieved')}",
             f"- pairs (animal + ≥1 relevant human record): {sum(1 for p in pairs.values() if p['status']=='pair')}",
             f"- processing errors: {sum(1 for p in pairs.values() if p['status']=='error')}",
             f"- pilot set: first {TARGET_PAIRS} pairs in screening order", "",
             "## Pairs", "",
             "| candidate | species | agent → human | indication | animal (20%) | human (20%) | pair 20% | pair 10% | pair any | safety pair | flags |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in sorted(pairs.values(), key=lambda p: p["rank"]):
        if not p.get("pilot_set"):
            continue
        c = p["classification"]
        lines.append(f"| {p['candidate']} | {p['species']} | {', '.join(p['agents'])} → {', '.join(p['human_agent_names'])} | "
                     f"{p['indication']} | {c['primary_orr20']['animal']} | {c['primary_orr20']['human']} | "
                     f"{c['primary_orr20']['pair']} | {c['sens_orr10']['pair']} | {c['sens_any_response']['pair']} | "
                     f"{p['safety']['pair']} | {len(p['flags'])} |")
    for key in THRESHOLDS:
        cnt = collections.Counter(p["classification"][key]["pair"] for p in pairs.values() if p.get("pilot_set"))
        lines += ["", f"**{key}:** " + ", ".join(f"{k} {v}" for k, v in cnt.most_common())]
    lines += ["", f"Cost this run (uncached calls): ${COST['usd']:.3f}"]
    open(os.path.join(V04, "pilot", "pilot_report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
