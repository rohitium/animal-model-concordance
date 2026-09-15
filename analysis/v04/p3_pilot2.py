"""Step 1b, pilot 2 — drug pairs rebuilt on reference-data snapshots (amendment A5).

For each qualifying candidate, in seeded screening order, until 10 pairs have corresponding human
evidence:
  A. Two models read the veterinary record and label every intervention as test / comparator /
     background / placebo, and record the TEST agent's result (§7.4 fields). One pair per test agent.
  B. Lookup (no model): the test agent must resolve in the US human-medicine index built from
     Drugs@FDA and openFDA labels. Unresolved -> counted as absent from US human medicine, not paired.
  C. Retrieval (no model): from the local snapshots, the agent's FDA applications and labels, and every
     interventional ClinicalTrials.gov study in which the agent is in an EXPERIMENTAL arm.
  D. Two models judge which of the retrieved human conditions and label indications correspond to
     the veterinary indication, choosing only from the retrieved lists. Agreed choices are used;
     disagreements are flagged. Both may also say the disease has no human form.
  E. Human classification from the highest evidence level present (A5 §4): US approval for a
     corresponding indication > phase 3 > phase 2 > earlier. At phase levels two models read each
     matched trial's structured primary outcomes and analyses, and a registered reason for stopping.
  F. Classification in code: §7.4 at 20% / 10% / any response, F4 combination, pair label.
Efficacy only in this pilot; safety is recorded as deferred.

Output: data/v04/pilot2/pairs.json, data/v04/pilot2/pilot2_report.md
"""
import sys, os, re, json, sqlite3, threading, collections, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from f4_human_index import lookup, lookup_all, norm
from p1_pilot_screen import efetch_abstracts

TARGET_PAIRS = 10
WAVE = 12
MAX_CONDITIONS_SHOWN = 500
MAX_TRIALS_READ_PER_LEVEL = 15
THRESHOLDS = {"primary_orr20": 20.0, "sens_orr10": 10.0, "sens_any_response": 0.0001}
DB = J("data", "raw", "snapshots", "aact", "aact_subset.sqlite")
_api = ThreadPoolExecutor(max_workers=96)
_work = ThreadPoolExecutor(max_workers=64)
_ncbi = threading.Semaphore(3)
_db_local = threading.local()

def db():
    if not hasattr(_db_local, "con"):
        _db_local.con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, check_same_thread=False)
    return _db_local.con

def both(t, system, user, schema, max_tokens=12000, deadline_s=300):
    """Both model roles at once. On failure returns (None, "<error text>") so the reason is recorded."""
    fa = _api.submit(ask, LADDER[t]["A"], system, user, schema, None, max_tokens, 4, deadline_s)
    fb = _api.submit(ask, LADDER[t]["B"], system, user, schema, None, max_tokens, 4, deadline_s)
    try:
        return fa.result()[0], fb.result()[0]
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:200]}"

# --- A. veterinary record: roles and the test agent's result -----------------------------------
VET = {"type": "object", "additionalProperties": False, "properties": {
    "interventions": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
        "name": {"type": "string"},
        "role": {"type": "string", "enum": ["test", "comparator", "background", "placebo-or-vehicle"]}},
        "required": ["name", "role"]}},
    "indication": {"type": ["string", "null"]},
    "design": {"type": "string", "enum": ["randomized-controlled", "single-arm", "dose-escalation", "observational",
               "other", "not-stated"]},
    "comparator": {"type": "string", "enum": ["placebo-or-untreated", "active", "historical", "none", "not-stated"]},
    "trial_aim": {"type": "string", "enum": ["superiority", "non-inferiority-or-equivalence", "not-stated"]},
    "oncology": {"type": "boolean"},
    "primary_endpoint_met": {"type": "string", "enum": ["yes", "no", "not-applicable", "unclear"]},
    "noninferiority_margin_met": {"type": "string", "enum": ["yes", "no", "not-applicable", "unclear"]},
    "objective_response_rate_percent": {"type": ["number", "null"]},
    "any_objective_response": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "validated_outcome_improved": {"type": "string", "enum": ["yes", "no", "not-applicable", "unclear"]},
    "efficacy_quote": {"type": ["string", "null"]}},
    "required": ["interventions", "indication", "design", "comparator", "trial_aim", "oncology", "primary_endpoint_met",
                 "noninferiority_margin_met", "objective_response_rate_percent", "any_objective_response",
                 "validated_outcome_improved", "efficacy_quote"]}
VET_SYS = """Read this record of a study in animals. Answer only from the record; use "unclear" or
null when it does not say.
interventions: every treatment named. role "test" = the intervention whose effect the study set out
  to evaluate; "comparator" = an active treatment it was compared against; "background" = given to
  all groups; "placebo-or-vehicle" = inactive control.
primary_endpoint_met: for controlled trials, "yes" only if the record says the test intervention met
  its primary endpoint or was significantly better on it than the comparator.
noninferiority_margin_met: for non-inferiority or equivalence trials only.
objective_response_rate_percent: cancer studies; complete + partial responses as a percentage of
  treated animals, if stated or computable from stated counts.
validated_outcome_improved: non-cancer, uncontrolled studies: a pre-specified clinical outcome improved.
efficacy_quote: copy the sentence with the main efficacy result exactly, or null.
Answer with JSON only."""

# --- D. correspondence of human conditions / label indications --------------------------------
CORR = {"type": "object", "additionalProperties": False, "properties": {
    "no_human_form_of_disease": {"type": "boolean"},
    "corresponding_condition_numbers": {"type": "array", "items": {"type": "integer"}},
    "corresponding_label_keys": {"type": "array", "items": {"type": "string"}},
    "note": {"type": "string"}},
    "required": ["no_human_form_of_disease", "corresponding_condition_numbers", "corresponding_label_keys", "note"]}
CORR_SYS = """A drug was tested in animals with a naturally occurring disease (VETERINARY INDICATION).
You are given the human conditions under which the same drug has been studied in registered clinical
trials, and the indications on its US human drug labels.
corresponding_condition_numbers: the NUMBERS of every listed human condition that is the same disease
  as the veterinary indication or the direct human counterpart of it (same organ and disease
  process). Do not include conditions that merely share a symptom or drug class. Numbers only.
corresponding_label_keys: the keys (e.g. "L3") of labels whose indications include that disease.
note: one sentence.
no_human_form_of_disease: true only if the veterinary disease has no counterpart disease in humans.
Choose only from what is listed. Answer with JSON only."""

# --- D0. does the veterinary disease have a human form? (once per candidate, not per ingredient) ---
HF = {"type": "object", "additionalProperties": False, "properties": {
    "human_form_exists": {"type": "boolean"}, "human_counterpart": {"type": ["string", "null"]}, "note": {"type": "string"}},
    "required": ["human_form_exists", "human_counterpart", "note"]}
HF_SYS = """Does the veterinary disease named below have a counterpart disease in humans (the same
disease, or the same organ and disease process)? Examples of diseases with no human form: canine
transmissible venereal tumour, feline infectious peritonitis. Parasitic or infectious diseases have a
human form only if humans are infected by the same or a directly analogous organism in the same organ.
human_counterpart: its name, or null. Answer with JSON only."""

# --- E. human trial read ----------------------------------------------------------------------
TRIAL = {"type": "object", "additionalProperties": False, "properties": {
    "drug_in_tested_arm": {"type": "boolean"},
    "primary_endpoint_met": {"type": "string", "enum": ["yes", "no", "unclear", "no-results-posted"]},
    "noninferiority_trial": {"type": "boolean"},
    "stopped_for_lack_of_efficacy": {"type": "boolean"},
    "basis": {"type": "string"}},
    "required": ["drug_in_tested_arm", "primary_endpoint_met", "noninferiority_trial", "stopped_for_lack_of_efficacy", "basis"]}
TRIAL_SYS = """You are given structured data from one ClinicalTrials.gov record: design, arms,
primary outcomes, statistical analyses of primary outcomes, and status. Judge only from it.
drug_in_tested_arm: the named DRUG is part of the intervention being tested, not only the comparator
  or background therapy given to every arm.
primary_endpoint_met: "yes" if a statistical analysis of a primary outcome shows the tested arm met
  it (superiority p < 0.05, or a non-inferiority margin met); "no" if the analyses show it was not met;
  "unclear" if analyses are absent or ambiguous; "no-results-posted" if there are no results.
stopped_for_lack_of_efficacy: the reason for stopping states futility or lack of efficacy.
basis: cite the numbers or text you relied on; no adjectives. Answer with JSON only."""

PHASE_LEVEL = {"PHASE3": 2, "PHASE2/PHASE3": 2, "PHASE4": 2, "PHASE2": 3, "PHASE1/PHASE2": 3, "PHASE1": 4, "EARLY_PHASE1": 4}

def trial_record(nct, ingredient):
    c = db()
    s = c.execute("SELECT brief_title, overall_status, phase, enrollment, why_stopped, results_first_posted_date "
                  "FROM studies WHERE nct_id=?", (nct,)).fetchone()
    d = c.execute("SELECT allocation, intervention_model, primary_purpose, masking FROM designs WHERE nct_id=?", (nct,)).fetchone()
    arms = c.execute("SELECT g.group_type, g.title, GROUP_CONCAT(i.name, ' + ') FROM design_groups g "
                     "LEFT JOIN design_group_interventions x ON x.design_group_id=g.id "
                     "LEFT JOIN interventions i ON i.id=x.intervention_id WHERE g.nct_id=? GROUP BY g.id", (nct,)).fetchall()
    outs = c.execute("SELECT id, title, time_frame FROM outcomes WHERE nct_id=?", (nct,)).fetchall()
    lines = [f"NCT: {nct}", f"DRUG: {ingredient}", f"TITLE: {s[0]}", f"STATUS: {s[1]}; PHASE: {s[2]}; ENROLLMENT: {s[3]}",
             f"WHY STOPPED: {s[4]}", f"RESULTS POSTED: {s[5]}",
             f"DESIGN: allocation={d[0] if d else None}; model={d[1] if d else None}; purpose={d[2] if d else None}", "ARMS:"]
    lines += [f"  - [{a[0]}] {a[1]}: {a[2]}" for a in arms]
    lines.append("PRIMARY OUTCOMES AND ANALYSES:")
    for oid, title, tf in outs:
        lines.append(f"  * {title} (time frame: {tf})")
        for a in c.execute("SELECT non_inferiority_type, param_type, param_value, p_value_modifier, p_value, ci_percent, "
                           "ci_lower_limit, ci_upper_limit, method, groups_description FROM outcome_analyses WHERE outcome_id=?", (oid,)):
            lines.append(f"      analysis: type={a[0]}; {a[1]}={a[2]}; p{a[3] or '='}{a[4]}; CI{a[5]}% [{a[6]}, {a[7]}]; "
                         f"method={a[8]}; groups={(a[9] or '')[:200]}")
    return "\n".join(lines), {"phase": s[2], "status": s[1], "results": bool(s[5]), "why_stopped": s[4]}

def human_trials(ingredient):
    rows = db().execute(
        "SELECT DISTINCT l.nct_id FROM ingredient_links l "
        "JOIN design_group_interventions x ON x.intervention_id=l.intervention_id "
        "JOIN design_groups g ON g.id=x.design_group_id "
        "JOIN studies s ON s.nct_id=l.nct_id "
        "WHERE l.ingredient=? AND g.group_type='EXPERIMENTAL' AND s.study_type='INTERVENTIONAL'", (ingredient,)).fetchall()
    ncts = [r[0] for r in rows]
    conds = collections.Counter()
    by_cond = collections.defaultdict(set)
    for nct in ncts:
        for (name,) in db().execute("SELECT name FROM conditions WHERE nct_id=?", (nct,)):
            conds[name] += 1
            by_cond[name].add(nct)
    return ncts, conds, by_cond

# --- F. classification -------------------------------------------------------------------------
def classify_vet(v, thr):
    if v["design"] == "randomized-controlled" or v["comparator"] in ("placebo-or-untreated", "active"):
        if v["trial_aim"] == "non-inferiority-or-equivalence" and v["noninferiority_margin_met"] in ("yes", "no"):
            return "positive" if v["noninferiority_margin_met"] == "yes" else "negative"
        if v["primary_endpoint_met"] == "yes":
            return "positive"
        if v["primary_endpoint_met"] == "no":
            return "negative" if v["comparator"] == "placebo-or-untreated" else "indeterminate"
        return "indeterminate"
    if v["design"] in ("single-arm", "dose-escalation"):
        if v["oncology"]:
            orr = v["objective_response_rate_percent"]
            if orr is not None:
                return "positive" if orr >= thr else "indeterminate"
            if thr < 1 and v["any_objective_response"] == "yes":
                return "positive"
        elif v["validated_outcome_improved"] == "yes":
            return "positive"
    return "indeterminate"

def combine(labels):
    s = {l for l in labels if l and l != "indeterminate"}
    return "indeterminate" if not s else ("positive" if s == {"positive"} else "negative" if s == {"negative"} else "mixed")

def pair_label(a, h):
    if "indeterminate" in (a, h): return "indeterminate"
    if "mixed" in (a, h): return "mixed"
    return "concordant" if a == h else "discordant"

def roles_key(v):
    keys = set()
    for i in v["interventions"]:
        if i["role"] == "test":
            found = lookup_all(i["name"])
            keys |= {f[0] for f in found} if found else {norm(i["name"])}
    return sorted(keys)

# --- per candidate -----------------------------------------------------------------------------
def process(c, t, index, abstracts):
    pm = c["id"][5:]
    ab = abstracts.get(pm, {})
    if not ab:
        return [{"candidate": c["id"], "rank": c["rank"], "title": c["title"], "status": "error",
                 "flags": ["abstract not retrieved"]}]
    text = f"{ab.get('title','')}\n{ab.get('abstract','')}"
    va, vb = both(t, VET_SYS, text, VET)
    base = {"candidate": c["id"], "rank": c["rank"], "title": c["title"], "species": c["A"]["species"], "tier": t, "date": today()}
    if va is None:
        return [{**base, "status": "error", "flags": [f"veterinary extraction failed: {vb}"]}]
    flags = []
    if roles_key(va) != roles_key(vb):
        flags.append(f"models disagree on test agent: A={roles_key(va)} B={roles_key(vb)}")
    tests = [i["name"] for i in va["interventions"] if i["role"] == "test"]
    if not tests:
        return [{**base, "status": "no-test-agent-identified", "flags": flags, "vet": {"A": va, "B": vb}}]
    out, units, seen = [], [], set()
    for name in tests:
        found = lookup_all(name)
        if not found:
            out.append({**base, "test_agent": name, "ingredient": None, "match_kind": None, "indication": va["indication"],
                        "vet": {"A": va, "B": vb}, "flags": list(flags), "status": "agent-absent-from-us-human-medicine"})
        for ing, matched, kind in found:
            if ing not in seen:
                seen.add(ing)
                units.append((name, ing, matched, kind, len(found)))
    hfa, hfb = both(t, HF_SYS, f"VETERINARY DISEASE: {va['indication']} (species: {c['A']['species']})", HF, 8000)
    if hfa is None:
        return out + [{**base, "test_agent": u[0], "ingredient": u[1], "status": "error",
                       "flags": flags + [f"human-form judgement failed: {hfb}"]} for u in units]
    human_form = {"A": hfa, "B": hfb}
    if hfa["human_form_exists"] != hfb["human_form_exists"]:
        flags.append(f"models disagree on whether the disease has a human form (A={hfa['human_form_exists']}, B={hfb['human_form_exists']})")
    if not hfa["human_form_exists"] and not hfb["human_form_exists"]:
        return out + [{**base, "test_agent": u[0], "ingredient": u[1], "indication": va["indication"], "vet": {"A": va, "B": vb},
                       "human_form": human_form, "flags": list(flags), "status": "no-human-form-of-disease"} for u in units]
    for name, ing, matched, kind, n_in_name in units:
        rec = {**base, "test_agent": name, "ingredient": ing, "matched_text": matched, "match_kind": kind,
               "indication": va["indication"], "vet": {"A": va, "B": vb}, "flags": list(flags)}
        if n_in_name > 1:
            rec["flags"].append(f"test agent is a combination ({n_in_name} US human ingredients); one pair per ingredient")
        if kind == "salt-stripped":
            rec["flags"].append(f"agent matched after salt stripping: {matched} -> {ing}")
        entry = index[ing]
        apps = {k: v for k, v in entry["applications"].items() if v["type"] in ("NDA", "BLA")}
        labels = {f"L{i}": {"set_id": sid, **lab} for i, (sid, lab) in enumerate(
            sorted(((s, l) for s, l in entry["labels"].items() if l["product_type"] == "HUMAN PRESCRIPTION DRUG"
                    and l["indications"]), key=lambda x: x[1]["effective_time"], reverse=True)[:12])}
        ncts, conds, by_cond = human_trials(ing)
        shown = [n for n, _ in conds.most_common(MAX_CONDITIONS_SHOWN)]
        user = (f"DRUG: {ing}\nVETERINARY INDICATION: {va['indication']} (species: {c['A']['species']})\n\n"
                f"HUMAN TRIAL CONDITIONS ({len(shown)} of {len(conds)} distinct, most frequent first):\n" +
                "\n".join(f"{i}. {n}" for i, n in enumerate(shown, 1)) + "\n\nUS HUMAN LABELS:\n" +
                "\n".join(f"[{k}] {v['brand']} ({v['application_number']}): {v['indications'][:1200]}" for k, v in labels.items()))
        ca, cb = both(t, CORR_SYS, user, CORR, max_tokens=16000, deadline_s=300)
        if ca is None:
            out.append({**rec, "status": "error", "flags": rec["flags"] + [f"correspondence judgement failed: {cb}"]}); continue
        rec["human_form"] = human_form
        num = lambda x: {shown[k - 1] for k in x["corresponding_condition_numbers"] if 1 <= k <= len(shown)}
        bad_nums = [k for x in (ca, cb) for k in x["corresponding_condition_numbers"] if not 1 <= k <= len(shown)]
        agreed_conds = sorted(num(ca) & num(cb))
        only_one = sorted(num(ca) ^ num(cb))
        agreed_labels = sorted(set(ca["corresponding_label_keys"]) & set(cb["corresponding_label_keys"]) & set(labels))
        if only_one: rec["flags"].append(f"condition correspondence disputed for {len(only_one)} condition(s): {only_one[:6]}")
        if bad_nums: rec["flags"].append(f"model returned condition numbers outside the list (ignored): {bad_nums[:6]}")
        label_disputed = sorted((set(ca["corresponding_label_keys"]) ^ set(cb["corresponding_label_keys"])) & set(labels))
        if label_disputed: rec["flags"].append(f"label correspondence disputed: {label_disputed}")
        matched = sorted(set().union(*[by_cond[n] for n in agreed_conds])) if agreed_conds else []
        rec.update({"fda_applications": apps, "labels_shown": {k: {kk: vv for kk, vv in v.items() if kk != "indications"} for k, v in labels.items()},
                    "corresponding_labels": agreed_labels, "human_trials_total": len(ncts),
                    "conditions_total": len(conds), "corresponding_conditions": agreed_conds,
                    "matched_trials": len(matched), "correspondence": {"A": ca, "B": cb}})
        # E. hierarchy
        levels = collections.defaultdict(list)
        if agreed_labels:
            levels[1] = [{"source": "fda-label", "label": labels[k], "classification": "positive"} for k in agreed_labels]
        meta = {}
        for nct in matched:
            _, m = trial_record(nct, ing)
            meta[nct] = m
            lv = PHASE_LEVEL.get(m["phase"] or "", 5)
            levels[lv].append(nct)
        top = min((l for l in levels if levels[l]), default=None)
        human_label, evidence = "indeterminate", []
        if top == 1:
            human_label, evidence = "positive", levels[1]
        elif top:
            chosen = sorted(levels[top], key=lambda n: (not meta[n]["results"], n))[:MAX_TRIALS_READ_PER_LEVEL]
            if len(levels[top]) > len(chosen):
                rec["flags"].append(f"level {top}: {len(levels[top])} trials, read first {len(chosen)} (results-posted first)")
            futs = {}
            for nct in chosen:
                txt, _ = trial_record(nct, ing)
                futs[nct] = _work.submit(both, t, TRIAL_SYS, txt, TRIAL, 8000)
            labs = []
            for nct, f in futs.items():
                ta, tb = f.result()
                if ta is None:
                    rec["flags"].append(f"{nct}: trial read failed: {tb}"); continue
                lab_a = ("negative" if ta["stopped_for_lack_of_efficacy"] else
                         {"yes": "positive", "no": "negative"}.get(ta["primary_endpoint_met"], "indeterminate")) if ta["drug_in_tested_arm"] else None
                lab_b = ("negative" if tb["stopped_for_lack_of_efficacy"] else
                         {"yes": "positive", "no": "negative"}.get(tb["primary_endpoint_met"], "indeterminate")) if tb["drug_in_tested_arm"] else None
                if lab_a != lab_b:
                    rec["flags"].append(f"{nct}: models disagree (A={lab_a}, B={lab_b})")
                final = lab_a if lab_a == lab_b else "indeterminate"
                evidence.append({"nct": nct, **meta[nct], "A": ta, "B": tb, "classification": final})
                if final: labs.append(final)
            human_label = combine(labs)
        rec.update({"human_top_level": top, "human_level_counts": {str(k): len(v) for k, v in levels.items()},
                    "human_evidence": evidence, "status": "pair" if top else "no-corresponding-human-evidence"})
        vet_diff = [k for k in ("design", "comparator", "trial_aim", "primary_endpoint_met", "objective_response_rate_percent",
                                "noninferiority_margin_met", "validated_outcome_improved") if va[k] != vb[k]]
        if vet_diff:
            rec["flags"].append(f"veterinary extraction disagreement on {vet_diff}")
        cls = {}
        for key, thr in THRESHOLDS.items():
            a = classify_vet(va, thr) if not vet_diff else combine([classify_vet(va, thr), classify_vet(vb, thr)])
            cls[key] = {"animal": a, "human": human_label, "pair": pair_label(a, human_label) if top else None}
        rec["classification"] = cls
        rec["safety"] = "deferred in pilot 2"
        out.append(rec)
    return out

def main():
    screen = load("pilot/screen.json")
    cand = [{**v, "rank": r} for r, v in enumerate(screen.values()) if v["qualifies"] and v["id"].startswith("PMID:")]
    t = tier("pilot")
    index = load("frames/human_index.json")
    pairs = load("pilot2/pairs.json")
    done = {p["candidate"] for p in pairs.values() if p["status"] != "error"}
    npair = lambda: len({p["candidate"] for p in pairs.values() if p["status"] == "pair"})
    # One batched fetch for every candidate's abstract (cached), instead of one NCBI call per candidate,
    # which drew HTTP 429 under parallel load.
    abstracts = {}
    ids = [c["id"][5:] for c in cand]
    for attempt in range(5):
        try:
            abstracts = efetch_abstracts(ids); break
        except Exception as e:
            print(f"abstract fetch retry {attempt+1}: {e}", flush=True); time.sleep(3 * (attempt + 1))

    def settled():
        """The pilot set is the first TARGET_PAIRS pairs in screening order. It is settled only when that
        many pairs exist AND every candidate ranked before the last of them has a non-error outcome."""
        ranked = sorted({(p["rank"], p["candidate"]) for p in pairs.values() if p["status"] == "pair"})
        if len(ranked) < TARGET_PAIRS:
            return False
        cutoff = ranked[TARGET_PAIRS - 1][0]
        status = collections.defaultdict(set)
        for p in pairs.values():
            status[p["candidate"]].add(p["status"])
        return all(c["id"] in status and "error" not in status[c["id"]] for c in cand if c["rank"] <= cutoff)

    attempts = collections.Counter()
    MAX_ATTEMPTS = 2   # a candidate failing twice is recorded as unresolved, reported, and no longer retried

    i = 0
    with ThreadPoolExecutor(max_workers=WAVE) as ex:
        while not settled():
            pending = [c for c in cand if attempts[c["id"]] < MAX_ATTEMPTS and
                       c["id"] not in {p["candidate"] for p in pairs.values() if p["status"] != "error"}]
            if not pending or i > 3 * len(cand):
                break
            wave = pending[:WAVE]
            i += WAVE
            for c in wave:
                attempts[c["id"]] += 1
            futs = {ex.submit(process, c, t, index, abstracts): c for c in wave}
            for f in as_completed(futs):
                c = futs[f]
                try:
                    recs = f.result()
                except Exception as e:
                    recs = [{"candidate": c["id"], "rank": c["rank"], "title": c["title"], "status": "error",
                             "flags": [f"processing failed: {type(e).__name__}: {str(e)[:200]}"]}]
                for k in [k for k in pairs if k.startswith(c["id"] + "|")]:
                    del pairs[k]
                for r in recs:
                    if r["status"] == "error" and attempts[c["id"]] >= MAX_ATTEMPTS:
                        r["status"] = "error-unresolved"
                        r["flags"] = r.get("flags", []) + [f"failed on {MAX_ATTEMPTS} attempts; not retried"]
                    pairs[f"{r['candidate']}|{r.get('ingredient') or r.get('test_agent') or '-'}"] = r
                    print(f"  {r['candidate']} {r.get('test_agent')} -> {r.get('ingredient')} | {r['status']} | "
                          f"trials {r.get('human_trials_total','-')} matched {r.get('matched_trials','-')} top level {r.get('human_top_level','-')} | "
                          f"pair20 {((r.get('classification') or {}).get('primary_orr20') or {}).get('pair')} | flags {len(r.get('flags', []))}   ${COST['usd']:.3f}", flush=True)
                save(pairs, "pilot2/pairs.json")
    if not settled():
        print(f"NOTE: qualifying candidates exhausted with {npair()} pairs; extend the screen (p1_pilot_screen.py) to continue")
    ranked = sorted((p for p in pairs.values() if p["status"] == "pair"), key=lambda p: p["rank"])
    keep_c = []
    for p in ranked:
        if p["candidate"] not in keep_c and len(keep_c) < TARGET_PAIRS:
            keep_c.append(p["candidate"])
    for p in pairs.values():
        p["pilot_set"] = p["status"] == "pair" and p["candidate"] in keep_c
    save(pairs, "pilot2/pairs.json")
    report(pairs, cand)

def report(pairs, cand):
    st = collections.Counter(p["status"] for p in pairs.values())
    L = ["# Step 1b — pilot 2 (reference-data snapshots, amendment A5)", "",
         f"Generated {today()} by `analysis/v04/p3_pilot2.py`. Efficacy only; safety deferred.", "",
         "## Denominator", "", f"- qualifying candidates available (screen of 120): {len(cand)}",
         f"- candidates processed: {len({p['candidate'] for p in pairs.values()})}"]
    L += [f"- {k}: {v}" for k, v in st.most_common()]
    L += ["", "## Pilot set (first 10 candidates with a pair, in screening order)", "",
          "| candidate | species | test agent → ingredient | indication | human evidence level | trials matched / total | animal 20% | human | pair 20% | 10% | any | flags |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    lvl = {1: "US approval", 2: "phase 3/4", 3: "phase 2", 4: "phase 1", 5: "phase n/a"}
    for p in sorted((p for p in pairs.values() if p.get("pilot_set")), key=lambda p: p["rank"]):
        c = p["classification"]
        L.append(f"| {p['candidate']} | {p['species']} | {p['test_agent']} → {p['ingredient']} | {p['indication']} | "
                 f"{lvl.get(p['human_top_level'])} | {p['matched_trials']} / {p['human_trials_total']} | {c['primary_orr20']['animal']} | "
                 f"{c['primary_orr20']['human']} | {c['primary_orr20']['pair']} | {c['sens_orr10']['pair']} | {c['sens_any_response']['pair']} | {len(p['flags'])} |")
    for key in THRESHOLDS:
        cnt = collections.Counter(p["classification"][key]["pair"] for p in pairs.values() if p.get("pilot_set"))
        L += ["", f"**{key}:** " + ", ".join(f"{k} {v}" for k, v in cnt.most_common())]
    L += ["", f"Cost this run (uncached calls): ${COST['usd']:.3f}"]
    os.makedirs(os.path.join(V04, "pilot2"), exist_ok=True)
    open(os.path.join(V04, "pilot2", "pilot2_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
