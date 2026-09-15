"""Resolve a drug name to its human counterpart, deterministically (amendment A6 execution note).

A drug "exists in humans" if either:
  us-human-medicine   it resolves in the US human-medicine index (Drugs@FDA, openFDA labels), or
  investigational     it is an intervention in at least one registered interventional human trial in the
                      ClinicalTrials.gov snapshot (AACT, 2026-09-14), matched by name or by a registered
                      other name (development codes such as PCI-32765 -> ibrutinib).
Never decided by a model. Every resolution records how it was made.
"""
import os, re, sqlite3, threading, collections
from f4_human_index import lookup_all, norm, base
from common import J

DB = J("data", "raw", "snapshots", "aact", "aact_subset.sqlite")
_local = threading.local()
_cache, _lock = {}, threading.Lock()
TYPES = ("DRUG", "BIOLOGICAL", "GENETIC", "COMBINATION_PRODUCT")

def _con():
    if not hasattr(_local, "con"):
        _local.con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, check_same_thread=False)
    return _local.con

def _key_token(n):
    toks = sorted((t for t in n.split() if len(t) >= 4), key=len, reverse=True)
    return toks[0] if toks else None

def _aact(name):
    """Registered interventions whose name or other name equals `name` (normalised). Returns
    (canonical_name, n_trials, via) or None."""
    n = norm(name)
    tok = _key_token(n)
    if not tok:
        return None
    c = _con()
    hits = collections.Counter(); trials = collections.defaultdict(set); via = {}
    for iname, nct, itype in c.execute("SELECT name, nct_id, intervention_type FROM interventions WHERE name LIKE ?", (f"%{tok}%",)):
        if itype in TYPES and (norm(iname) == n or base(iname) == base(n)):
            hits[base(iname)] += 1; trials[base(iname)].add(nct); via[base(iname)] = "intervention-name"
    for oname, iname, nct, itype in c.execute(
            "SELECT o.name, i.name, i.nct_id, i.intervention_type FROM intervention_other_names o "
            "JOIN interventions i ON i.id = o.intervention_id WHERE o.name LIKE ?", (f"%{tok}%",)):
        if itype in TYPES and (norm(oname) == n or base(oname) == base(n)):
            hits[base(iname)] += 1; trials[base(iname)].add(nct); via.setdefault(base(iname), "other-name")
    if not hits:
        return None
    canon = hits.most_common(1)[0][0]
    return canon, len(trials[canon]), via[canon]

def resolve(name):
    """[{ingredient, matched_text, kind, human_status, n_trials}] for every human counterpart named in `name`."""
    key = norm(name)
    with _lock:
        if key in _cache:
            return _cache[key]
    out = [{"ingredient": i, "matched_text": t, "kind": k, "human_status": "us-human-medicine", "n_trials": None}
           for i, t, k in lookup_all(name)]
    if not out:
        a = _aact(name)
        if a:
            canon, n_trials, via = a
            again = lookup_all(canon)
            if again:
                out = [{"ingredient": i, "matched_text": canon, "kind": f"synonym-via-{via}", "human_status": "us-human-medicine",
                        "n_trials": n_trials} for i, _, _ in again]
            else:
                out = [{"ingredient": canon, "matched_text": canon, "kind": via, "human_status": "investigational", "n_trials": n_trials}]
    with _lock:
        _cache[key] = out
    return out

if __name__ == "__main__":
    for probe in ["tanezumab", "fasinumab", "PCI-32765", "masitinib", "GS-9219", "rabacfosadine", "verdinexor", "toceranib",
                  "anti-nerve growth factor monoclonal antibodies", "lokivetmab", "bedinvetmab", "mavacamten", "pimobendan"]:
        print(f"{probe:48s} -> {resolve(probe)}")
