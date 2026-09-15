"""Index of active ingredients present in US human medicine (amendment A5).

Built only from the frozen snapshots, never from a model:
  - Drugs@FDA Products.txt ActiveIngredient, joined to Applications (NDA/BLA/ANDA) and the original
    approval date from Submissions (SubmissionType ORIG, status AP);
  - openFDA drug labels with a HUMAN product type (openfda.substance_name), which adds marketed
    human products that Drugs@FDA lists differently, and supplies indications text.

Names are normalised by upper-casing, removing punctuation and stripping salt/ester words, so
"BENAZEPRIL HYDROCHLORIDE" and "benazepril" resolve to the same base. Both the raw name and the base
are kept, and a lookup reports which one matched, so a salt-stripped match can be audited.

Output: data/v04/frames/human_index.json   (lookup(name) is imported by the pilot)
"""
import sys, os, re, io, csv, json, zipfile, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

SNAP = J("data", "raw", "snapshots")
SALTS = {"HYDROCHLORIDE", "HCL", "DIHYDROCHLORIDE", "HYDROBROMIDE", "SODIUM", "DISODIUM", "POTASSIUM",
         "CALCIUM", "MAGNESIUM", "MALEATE", "MESYLATE", "MESILATE", "BESYLATE", "SULFATE", "SULPHATE",
         "BISULFATE", "ACETATE", "TARTRATE", "BITARTRATE", "CITRATE", "FUMARATE", "SUCCINATE", "PHOSPHATE",
         "DIPROPIONATE", "PROPIONATE", "VALERATE", "BENZOATE", "LACTATE", "GLUCONATE", "TROMETHAMINE",
         "MONOHYDRATE", "DIHYDRATE", "TRIHYDRATE", "HYDRATE", "ANHYDROUS", "PAMOATE", "OXIME", "HYCLATE",
         "NITRATE", "CHLORIDE", "BROMIDE", "IODIDE", "MEGLUMINE", "ARGININE", "LYSINE", "ESTOLATE",
         "STEARATE", "PALMITATE", "DECANOATE", "ENANTHATE", "CYPIONATE", "FREE", "BASE", "ACID"}

def norm(name):
    s = re.sub(r"[^A-Z0-9 ]+", " ", (name or "").upper())
    return re.sub(r"\s+", " ", s).strip()

def base(name):
    toks = [t for t in norm(name).split() if t not in SALTS]
    return " ".join(toks) if toks else norm(name)

def split_ingredients(s):
    return [p.strip() for p in re.split(r";|,(?![^()]*\))| AND ", s or "") if p.strip()]

def build():
    z = zipfile.ZipFile(os.path.join(SNAP, "drugsatfda", "drugsatfda.zip"))
    read = lambda n: csv.DictReader(io.TextIOWrapper(z.open(n), encoding="latin-1"), delimiter="\t")
    apps = {r["ApplNo"]: r["ApplType"] for r in read("Applications.txt")}
    orig = {}
    for r in read("Submissions.txt"):
        if r["SubmissionType"] == "ORIG" and r["SubmissionStatus"] == "AP":
            d = r["SubmissionStatusDate"][:10]
            if r["ApplNo"] not in orig or d < orig[r["ApplNo"]]:
                orig[r["ApplNo"]] = d
    idx = collections.defaultdict(lambda: {"names": set(), "applications": {}, "labels": {}})
    for r in read("Products.txt"):
        for ing in split_ingredients(r["ActiveIngredient"]):
            e = idx[base(ing)]
            e["names"].add(norm(ing))
            e["applications"][r["ApplNo"]] = {"type": apps.get(r["ApplNo"]), "first_approval": orig.get(r["ApplNo"]),
                                              "drug_name": r["DrugName"]}
    n_labels = 0
    for part in sorted(glob.glob(os.path.join(SNAP, "openfda_label", "*.json.zip"))):
        zz = zipfile.ZipFile(part)
        for rec in json.loads(zz.read(zz.namelist()[0]))["results"]:
            of = rec.get("openfda", {})
            ptype = (of.get("product_type") or [""])[0]
            if not ptype.startswith("HUMAN"):
                continue
            n_labels += 1
            for sub in of.get("substance_name", []):
                e = idx[base(sub)]
                e["names"].add(norm(sub))
                sid = rec.get("set_id")
                prev = e["labels"].get(sid)
                if prev and prev["effective_time"] >= rec.get("effective_time", ""):
                    continue
                e["labels"][sid] = {"effective_time": rec.get("effective_time", ""), "product_type": ptype,
                                    "application_number": (of.get("application_number") or [None])[0],
                                    "brand": (of.get("brand_name") or [None])[0],
                                    "n_substances": len(of.get("substance_name", [])),
                                    "indications": " ".join(rec.get("indications_and_usage", []))[:3000]}
    out = {}
    for k, e in idx.items():
        out[k] = {"names": sorted(e["names"]), "applications": e["applications"], "labels": e["labels"]}
    return out, n_labels

_INDEX = None
def lookup(name):
    """Resolve an agent name against the human index. Returns (base_key, match_kind) or (None, None).
    match_kind is 'exact' (normalised name equals a recorded name) or 'salt-stripped'."""
    global _INDEX
    if _INDEX is None:
        _INDEX = load("frames/human_index.json")
    n, b = norm(name), base(name)
    if b in _INDEX:
        return b, ("exact" if n in _INDEX[b]["names"] else "salt-stripped")
    return None, None

# Ingredient names that are also ordinary words or vehicles; never taken as a test agent's ingredient
# when found inside a longer name (L73).
GENERIC = {"WATER", "OXYGEN", "IRON", "GOLD", "SALINE", "ALCOHOL", "GLYCERIN", "GLUCOSE", "DEXTROSE", "SUCROSE",
           "LACTOSE", "CALCIUM", "SODIUM", "POTASSIUM", "MAGNESIUM", "ZINC", "SILVER", "SULFUR", "CARBON", "NITROGEN",
           "AIR", "PLACEBO", "VEHICLE", "OIL", "PETROLATUM", "TALC", "STARCH", "CELLULOSE", "GELATIN", "HONEY"}

def lookup_all(name):
    """Every indexed ingredient named inside `name` ("Paclitaxel with encequidar", "vincristine plus
    ivermectin", "Credelio Quattro (lotilaner, moxidectin, ...)"). Longest n-gram wins, so
    "INSULIN LISPRO" is not also reported as "INSULIN". Returns [(ingredient, matched_text, kind)]."""
    global _INDEX
    if _INDEX is None:
        _INDEX = load("frames/human_index.json")
    whole, kind = lookup(name)
    if whole:
        return [(whole, norm(name), kind)]
    toks = norm(name).split()
    taken, found = set(), []
    for n in range(min(4, len(toks)), 0, -1):
        for i in range(len(toks) - n + 1):
            span = set(range(i, i + n))
            if span & taken:
                continue
            g = " ".join(toks[i:i + n])
            b = base(g)
            if i > 0 and toks[i - 1] in ("ANTI", "NON"):   # "anti-nerve growth factor" is not nerve growth factor
                continue
            if b in _INDEX and b not in GENERIC and len(b) > 3:
                taken |= span
                found.append((b, g, "exact" if g in _INDEX[b]["names"] else "salt-stripped"))
    return found

def main():
    out, n_labels = build()
    save(out, "frames/human_index.json")
    with_app = sum(1 for e in out.values() if e["applications"])
    print(f"human index: {len(out)} ingredient bases ({with_app} with an FDA application), "
          f"from {n_labels} human labels")
    for probe in ("pimobendan", "benazepril hydrochloride", "lotilaner", "fluralaner", "telmisartan",
                  "cyclosporine", "paclitaxel", "nesiritide", "moxidectin", "cannabidiol", "lokivetmab", "nemolizumab"):
        k, kind = lookup(probe)
        e = out.get(k, {})
        print(f"  {probe:26s} -> {k} ({kind}) apps={len(e.get('applications', {}))} labels={len(e.get('labels', {}))}")

if __name__ == "__main__":
    main()
