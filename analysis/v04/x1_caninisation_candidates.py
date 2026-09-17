"""Score human-approved molecules as candidates for a companion-animal (caninisation) program.

The question: which human molecules, already shown to work in people, are the best candidates to
license and develop for dogs or cats?

Of the classified drug pairs in the review, 477 run human approval first and the veterinary evidence
later; 22 run the other way, at a median gap of 30 years. Companion-animal medicine adopts human
drugs, and adopts them late. This selects what to adopt next.

A candidate needs both legs of human evidence - safety AND efficacy - and then either no
companion-animal program against its target, or a stop unrelated to clinical performance. An
approval carries both legs by definition. A discontinued asset carries them only if it reached a
stage where efficacy could show and was stopped for some other reason; an efficacy failure is
disqualifying, because demonstrated efficacy is the premise of the approach.

Inputs
  ~/Downloads/human_drug_programs.csv   human pipeline: company, drug, status, indication, target
  ~/Downloads/pet_drug_programs.csv     companion-animal pipeline, same shape plus species
  data/v04/part1/final_results.json     the review: dog-vs-human concordance evidence by area
  data/v04/part2/indication_areas.json  indication -> condition area (A13)
  data/v04/part2/species_safety_exclusions.json   known species toxicity (reviewer-supplied)
  data/raw/snapshots/drugsatfda/drugsatfda.zip    brand -> active ingredient -> approval year
  data/v04/frames/human_index.json      ingredient -> FDA applications and first approval

Output
  data/v04/part2/caninisation_candidates.json

What the score is, and is not. It combines four things that are evidenced: whether the target is
unclaimed in companion animals, how well that disease area's biology corresponds between dog and
human WEIGHTED BY EVIDENCE LEVEL (a level-A intervention outcome counts for more than a level-C
biology similarity), whether the molecule is old enough to be licensable cheaply, and whether its
class already has a precedent that ran dog-first. It does NOT include canine disease prevalence or
willingness to pay, because no epidemiological source is held here; that input is declared missing
rather than proxied. The score orders candidates for human review. It is not a valuation.
"""
import sys, os, re, csv, json, collections, zipfile

sys.path.insert(0, os.path.dirname(__file__))
from common import load, save, J, today  # noqa

NOW = int(today()[:4])
HUMAN_CSV = os.path.expanduser("~/Downloads/human_drug_programs.csv")
PET_CSV = os.path.expanduser("~/Downloads/pet_drug_programs.csv")

# Classes with a precedent in our own corpus that ran veterinary-first or near-simultaneously.
PRECEDENT = {
    "btk": "ibrutinib (dog 2010, human 2013), acalabrutinib (2016, 2017) and rilzabrutinib "
           "(canine pemphigus 2021, human 2025) all reached dogs at or before human approval",
    "brutinib": "same BTK class: three molecules reached dogs at or before human approval",
    "sglt2": "bexagliflozin was approved for cats and for humans within months of each other",
    "gliflozin": "same SGLT2 class: bexagliflozin was approved for cats and humans months apart",
    "anti-ngf": "bedinvetmab (Librela) and frunevetmab reached companion animals before the human "
                "anti-NGF programs cleared safety",
    "ngf": "bedinvetmab (Librela) and frunevetmab reached companion animals first",
}

# Not therapeutics: diagnostic radiotracers, contrast and imaging agents. They carry no target,
# so they score on area evidence and age alone and float to the top of any naive ranking.
# No \b after a stem: "\bthall\b" does not match "Thallium" (the same pattern-looks-right,
# matches-nothing failure as the [ae] digraph bug in the indication rules, A13).
NOT_A_THERAPEUTIC = re.compile(
    r"(thalli|thallous|gallium|technetium|iobenguane|fluorodeoxy|fludeoxy|gadolinium|"
    r"iodixanol|iohexol|barium sulfate|indium in|xenon xe|ammonia n 13|rubidium|florbetap|"
    r"flortauci|piflufolastat|copper cu|contrast agent|imaging agent|diagnostic agent)", re.I)

# Biosimilars are the same licensing opportunity as their reference molecule: strip the
# four-letter FDA suffix (BEVACIZUMAB-AWWB) and the literal word.
BIOSIMILAR = re.compile(r"-[a-z]{4}\b|\bbiosimilar\b", re.I)

# Disease areas where dogs do not get the human disease, whatever the target looks like.
NOT_A_DOG_DISEASE = re.compile(
    r"cystic fibrosis|hiv|smoking|nicotine|contracept|malaria|tuberculos|hepatitis [bc]|"
    r"sickle cell|thalass|huntington|duchenne|spinal muscular atrophy|multiple sclerosis|"
    r"alzheimer|parkinson|schizophren|bipolar|depress|migraine|opioid use|alcohol use|"
    r"covid|influenza vaccine|human papilloma|menopaus|endometrio|preterm|fertility|"
    r"psoriasis|ulcerative colitis|crohn|gout|osteoporosis|macular degeneration|"
    r"smallpox|mpox|vaccinia|hypophosphat|osteomalacia|sarcoidosis|"
    r"narcoleps|tardive|myasthenia|"
    # Human allergy to an animal is a human indication with no companion-animal counterpart: the
    # patient is a person. REGN1908-1909 (anti-Fel d 1, for people allergic to cats) reached the
    # candidate list because the area rules read "cat allergy" as immunology.
    r"cat allergy|allergy to cats|peanut allergy|allergic rhinitis", re.I)
# Not excluded, deliberately: pulmonary hypertension is a recognized and common canine condition,
# secondary to mitral valve disease and to heartworm, so the PAH agents stay in.

# Dogs and cats get a specific set of cancers, and it is not the human set. Lymphoma,
# osteosarcoma, haemangiosarcoma, mast cell tumor, oral melanoma, urothelial carcinoma, mammary
# carcinoma and soft-tissue sarcoma are common and well characterized; multiple myeloma, prostate
# adenocarcinoma, NSCLC and cervical cancer are rare, absent, or biologically different. Without
# this gate the oncology list leads with myeloma bispecifics and prostate antiandrogens, which
# would be wrong on the biology and obviously wrong to any veterinary oncologist.
CANINE_CANCER = re.compile(
    r"lymphoma|leukae?mia|osteosarcoma|h[ae]mangiosarcoma|mast cell|melanoma|urothelial|"
    r"bladder|mammary|breast|soft tissue sarcoma|sarcoma|glioma|histiocytic|"
    r"solid tumou?r|\bcancer\b|carcinoma|neoplas|oral tumou?r|nasal", re.I)
# Human tumor types that dogs do not get, or get too rarely and too differently to build a
# program on. Thyroid carcinoma and hepatocellular carcinoma are NOT here: both are real canine
# indications carried by the drug-pair corpus (5 and 3 pairs), so excluding them would drop
# evidence this review actually holds.
HUMAN_ONLY_CANCER = re.compile(
    r"multiple myeloma|\bmyeloma\b|prostat|cervical|ovarian|non-small cell|small cell lung|"
    r"nsclc|sclc|colorectal|gastric|oesophag|esophag|pancreatic|cholangio|"
    r"myelodysplas|myelofibros|mantle cell|marginal zone|"
    r"acute myeloid|chronic myeloid|hodgkin|neuroendocrine|renal cell|head and neck|"
    r"biliary|uveal|merkel|testicular|endometrial", re.I)


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def toks(s):
    s = re.sub(r"\(.*?\)", " ", (s or "").lower())
    return {t for t in re.split(r"[^a-z0-9\-]+", s) if len(t) > 2}


def brand_index(zip_path):
    """brand -> (ingredient, application numbers), from Drugs@FDA Products.txt."""
    idx = {}
    with zipfile.ZipFile(zip_path) as z:
        with z.open("Products.txt") as fh:
            for row in csv.DictReader((l.decode("utf-8", "replace") for l in fh), delimiter="\t"):
                b, ing = (row.get("DrugName") or "").strip(), (row.get("ActiveIngredient") or "").strip()
                if not b or not ing:
                    continue
                e = idx.setdefault(norm(b), {"ingredient": ing, "appl": set()})
                e["appl"].add((row.get("ApplNo") or "").strip())
    return idx


def approval_year(ingredient, human_index):
    """Earliest US approval year for an ingredient, from the human index."""
    rec = human_index.get(ingredient.upper().strip())
    if not rec:
        head = ingredient.upper().split()[0] if ingredient else ""
        rec = next((human_index[k] for k in human_index if head and k.startswith(head[:8])), None)
    if not rec:
        return None
    years = [a.get("first_approval") for a in (rec.get("applications") or {}).values()]
    years = [int(y[:4]) for y in years if y and y[:4].isdigit()]
    return min(years) if years else None


def dog_evidence(results):
    """Per condition area: how dog-vs-human comparisons came out, and at what evidence level.

    Weighted so that intervention outcomes dominate biology similarity: a level-A result counts 3,
    level B 2, level C 1. An area where the biology merely looks similar is a weaker basis for a
    development program than one where treating the disease actually worked.
    """
    AREA = {"pain-musculoskeletal": "musculoskeletal", "cross-cutting-toxicology": "toxicology"}
    W = {"A": 3, "B": 2, "C": 1}
    ev = collections.defaultdict(lambda: {"n": 0, "corr": 0, "not": 0, "mixed": 0,
                                          "A": 0, "B": 0, "C": 0, "w_corr": 0.0, "w_tot": 0.0,
                                          "studies": set()})
    for r in results:
        rep = str(r.get("species_as_reported") or "")
        if r.get("species") != "dog" and not re.search(r"dog|canine", rep, re.I):
            continue
        a = AREA.get(r.get("disease_area"), r.get("disease_area") or "other")
        lv = (r.get("level") or "?")[:1]
        e = ev[a]
        e["n"] += 1
        e["studies"].add(r["pmid"])
        if lv in W:
            e[lv] += 1
        d = r.get("direction")
        e["corr"] += d == "animal-corresponded"
        e["not"] += d == "animal-did-not-correspond"
        e["mixed"] += d == "mixed"
        if d in ("animal-corresponded", "animal-did-not-correspond"):
            w = W.get(lv, 1)
            e["w_tot"] += w
            e["w_corr"] += w if d == "animal-corresponded" else 0
    out = {}
    for a, e in ev.items():
        out[a] = {"results": e["n"], "studies": len(e["studies"]),
                  "corresponded": e["corr"], "did_not": e["not"], "mixed": e["mixed"],
                  "level_A": e["A"], "level_B": e["B"], "level_C": e["C"],
                  "weighted_concordance": round(e["w_corr"] / e["w_tot"], 3) if e["w_tot"] else None}
    return out


def main():
    results = [r for r in load("part1/final_results.json") if r["status"] == "final"]
    ev = dog_evidence(results)
    rules = (load("part2/indication_areas.json") or {}).get("rules") or []
    safety = (load("part2/species_safety_exclusions.json") or {}).get("exclusions") or []
    human_index = load(J("data", "v04", "frames", "human_index.json"))
    brands = brand_index(J("data", "raw", "snapshots", "drugsatfda", "drugsatfda.zip"))

    def area_of(s):
        s = (s or "").lower()
        for r in rules:
            if re.search(r["pattern"], s):
                return r["area"]
        return "other"

    # Every program, not only the approved ones. A human asset shelved after Phase 3 carries a
    # safety package - the expensive part - and usually failed on efficacy against a human
    # comparator or on commercial grounds, neither of which need apply in a dog.
    human = list(csv.DictReader(open(HUMAN_CSV)))
    pet = list(csv.DictReader(open(PET_CSV)))
    holder_file = load("part2/pet_target_holders.json") or {}
    holders = holder_file.get("by_target_token") or {}
    # One definition drives both sides of the join: the index was built with these same patterns.
    # Matching raw words alone failed in both directions - generic tokens like "inhibitor" matched
    # everything, while Apoquel ("JAK1 inhibitor") and Librela ("anti-NGF monoclonal antibody")
    # matched nothing, so a human JAK or NGF asset appeared to face no competition at all.
    class_patterns = holder_file.get("class_patterns") or {}

    def class_stems(*texts):
        hay = " ".join(t or "" for t in texts).lower()
        return {f"class:{k}" for k, pat in class_patterns.items() if re.search(pat, hay)}

    def stage_of(r):
        q = (r.get("phase") or "").lower()
        if "approv" in q or "market" in q:
            return "Approved"
        for n, label in (("3", "Phase 3"), ("2", "Phase 2"), ("1", "Phase 1")):
            if n in q:
                return label
        return "Preclinical" if "preclin" in q else "unstated"

    def discontinued(r):
        s = (r.get("status") or "").lower()
        return "discontinu" in s or "inactive" in s

    STAGE_RANK = {"Approved": 0, "Phase 3": 1, "Phase 2": 2, "Phase 1": 3,
                  "Preclinical": 4, "unstated": 5}

    # Why an asset was dropped, read from the source link and the phase note. Withdrawn over a
    # survival detriment (umbralisib) or halted after patient deaths (GB5121) is the opposite
    # signal from shelved on strategy, and pooling them under "shelved" would present a drug
    # pulled for harm as available inventory.
    SIGNALS = [
        ("safety or withdrawal",
         r"safety|withdraw|death|mortality|survival|toxicit|adverse|abuse|overdose|recall|"
         r"partial.?hold|clinical.?hold|black.?box"),
        ("production or supply", r"production|supply|manufactur|ceased"),
        # Signals are read mostly from URL slugs, where words are hyphen-joined: "pulls the plug"
        # never matched "pulls-the-plug", which left fasinumab - the clearest candidate here -
        # reading as "not legible". Separators are [-\s] throughout for that reason. Fifth bug of
        # this exact shape in this analysis, after [ae], \bthall\b, cardiomyopath and myopath.
        ("efficacy failure", r"fail|miss|did[-\s]not[-\s]meet|futility|endpoint|topline|halt|"
                             r"wipes?[-\s]out|cancel"),
        ("commercial or strategic", r"lay-?offs?|restructur|shelv|pipeline|strateg|"
                                    r"pulls?[-\s]the[-\s]plug|cut(s|backs)?|priorit|"
                                    r"abandon|deprioriti|ends?[-\s]|drops?[-\s]"),
    ]

    def disc_signal(r):
        hay = " ".join([r.get("source_link") or "", r.get("phase") or "",
                        r.get("indication") or ""]).lower()
        for label, pat in SIGNALS:
            if re.search(pat, hay):
                return label
        return "not legible from the source"

    # Amendment A18. The signal above reads a headline's framing, not a cause, and it was wrong on
    # the molecule that mattered most: fasinumab's slug says "pulls-the-plug", scored commercial,
    # for a program that carried an FDA partial clinical hold, an FDA-halted Phase IIb after an
    # adjudicated arthropathy, and IDMC-halted high-dose arms. Only hand-verified reasons decide
    # eligibility; the regex signal is kept for display and labeled as unverified.
    REASONS = (load("part2/discontinuation_reasons.json") or {}).get("reasons") or {}

    def verified_reason(r):
        return REASONS.get((r.get("drug_name") or "").strip())

    candidates, skipped = [], collections.Counter()
    for r in human:
        target, indication = r.get("target") or "", r.get("indication") or ""
        # A target already worked in companion animals is NOT excluded. It means the indication has
        # a validated market: atopic dermatitis carries 9 companion-animal programs and
        # osteoarthritis 25, and Elanco entered atopic dermatitis against Zoetis's Apoquel and
        # Cytopoint. Crowding is recorded so a two-player field can be told from a twenty-player
        # commodity, and the holders are named.
        keys = toks(target) | class_stems(target, r.get("drug_name"))
        claim = [h for t in keys for h in holders.get(t, [])]
        seen, competitors = set(), []
        for h in claim:
            if h["drug"] not in seen:
                seen.add(h["drug"]); competitors.append(h)
        if NOT_A_DOG_DISEASE.search(indication):
            skipped["disease dogs do not get"] += 1
            continue
        # A molecule withdrawn or halted over harm is not a licensing candidate, whatever the
        # biology says. Umbralisib was withdrawn over a survival detriment in UNITY-CLL and GB5121
        # was halted after patient deaths; both were presented as shelved assets before this gate.
        if discontinued(r) and disc_signal(r) == "safety or withdrawal":
            skipped["discontinued over safety or withdrawn"] += 1
            continue
        vr = verified_reason(r)
        if vr and vr["reason"] == "safety":
            skipped["discontinued over safety or withdrawn"] += 1
            continue
        if vr and vr["reason"] == "not-a-dog-indication":
            skipped["disease dogs do not get"] += 1
            continue
        if NOT_A_THERAPEUTIC.search(r.get("drug_name") or "") or NOT_A_THERAPEUTIC.search(target):
            skipped["diagnostic or imaging agent, not a therapeutic"] += 1
            continue
        # A human prophylactic vaccine is not a molecule to license and caninise: the companion
        # vaccine market is built on the pathogens dogs and cats actually meet (parvovirus,
        # distemper, leptospirosis, rabies), not on RSV or human papillomavirus. mRESVIA and the
        # CpG adjuvant reached the candidate list because the area rules read them as immunology.
        if re.search(r"\bvaccine\b|\bmrna vaccine\b|respiratory syncytial|\brsv\b",
                     (indication + " " + target), re.I):
            skipped["human vaccine or adjuvant, not a licensing candidate"] += 1
            continue
        # Indications the area rules place wrongly, caught by reading what landed where: travoprost
        # for glaucoma was sitting in cardiovascular (prostaglandin analogue), and chenodiol, a bile
        # acid, in musculoskeletal.
        if re.search(r"glaucoma|intraocular pressure|dry eye|keratoconjunctivitis", indication, re.I):
            area_override = "ophthalmology"
        elif re.search(r"bile acid|cholesterol ester storage|xanthomatosis", indication, re.I):
            area_override = "liver-gi"
        else:
            area_override = None
        # An oncology indication has to name a tumor type dogs actually get. A canine tumor type
        # named anywhere in the indication wins over a human-only term in the same string: killing
        # pirtobrutinib for the words "mantle cell" would drop the canine BTK opportunity, which is
        # the best-evidenced one in the whole list, over a phrase that also says "CLL and lymphoma".
        if area_of(indication) == "oncology":
            canine_named = CANINE_CANCER.search(indication)
            if not canine_named:
                skipped["oncology indication too unspecific to place in a dog"] += 1
                continue
            if HUMAN_ONLY_CANCER.search(indication) and not re.search(
                    r"lymphoma|leukae?mia|osteosarcoma|h[ae]mangiosarcoma|mast cell|melanoma|"
                    r"urothelial|bladder|mammary|breast|soft tissue sarcoma|glioma|histiocytic",
                    indication, re.I):
                skipped["human tumor type dogs do not get"] += 1
                continue
        area = area_override or area_of(indication)
        e = ev.get(area)
        if not e or e["results"] < 5 or not e["weighted_concordance"]:
            skipped["no dog evidence for this area"] += 1
            continue
        if e["weighted_concordance"] < 0.6:
            skipped["dog evidence says biology does not correspond"] += 1
            continue

        # brand -> ingredient -> first approval year
        base = re.split(r"[(/]", r.get("drug_name") or "")[0].strip()
        paren = re.findall(r"\(([^)]+)\)", r.get("drug_name") or "")
        hit = brands.get(norm(base)) or next((brands[norm(p)] for p in paren if norm(p) in brands), None)
        ingredient = hit["ingredient"] if hit else (paren[0] if paren else None)
        year = approval_year(ingredient, human_index) if ingredient else None
        age = NOW - year if year else None

        flags = []
        excluded = False
        hay = " ".join([r.get("drug_name") or "", target, ingredient or ""])
        for s in safety:
            if re.search(s["match"], hay, re.I):
                flags.append({"action": s["action"], "species": s["species"], "effect": s["effect"]})
                excluded = excluded or s["action"] == "exclude"
        if excluded:
            skipped["known species toxicity"] += 1
            continue

        precedent = next((v for k, v in PRECEDENT.items() if k in target.lower()
                          or k in (ingredient or "").lower()), None)

        # No molecule-level score. Every candidate in an area inherits identical evidence - all 9
        # cardiovascular assets carry the same 0.685 / 16 level-A / n=19 - so a blended number
        # would order molecules by the only things that vary, chiefly how old they are, while
        # looking like it ordered them by evidence. Cozaar above ivabradine would be an artifact of
        # a 1995 approval date, not a finding. Areas are ranked on the review's evidence, which is
        # real; within an area candidates are an unranked set, carrying the attributes that differ
        # so a human can order them once prevalence, market and IP are known.
        candidates.append({
            "drug": r.get("drug_name"), "ingredient": ingredient,
            "target": target, "indication": indication, "company": r.get("company_name"),
            "source": r.get("source_link"), "area": area, "first_us_approval": year,
            "years_since_approval": age, "precedent": precedent, "safety_flags": flags,
            "evidence": {k: e[k] for k in ("results", "studies", "corresponded", "did_not",
                                           "level_A", "weighted_concordance")},
            # "Cancer" or "Solid tumors" as an indication places nothing in a dog: the molecule
            # passes the tumor gate on a word, and which canine tumor it might treat is unknown.
            "indication_is_vague": bool(re.fullmatch(
                r"\s*(cancer|solid tumou?rs?|advanced cancer|oncology)\s*", indication, re.I)),
            "human_stage": stage_of(r),
            "human_status": "discontinued" if discontinued(r) else "active",
            "competitors": competitors,
            # Routes are not exclusive, and forcing one label hid the interesting case. Fasinumab
            # is a shelved Phase 3 asset AND faces four companion-animal anti-NGF antibodies; the
            # question about it is not whether the target is free but whether a shelved human asset
            # can beat Librela, which only shows if both facts are carried.
            "routes": ([("shelved asset" if discontinued(r) and STAGE_RANK[stage_of(r)] <= 2 else None),
                        ("me-too into a claimed target" if competitors else "white space")]),
            "route": ("shelved asset" if discontinued(r) and STAGE_RANK[stage_of(r)] <= 2
                      else "me-too into a claimed target" if competitors
                      else "white space"),
            "competitor_count": len(competitors),
            # "White space" means absent from the 328 branded companion-animal programs supplied,
            # NOT absent from veterinary practice. Furosemide is the standard diuretic in canine
            # heart failure and sildenafil is standard for canine pulmonary hypertension; both look
            # unclaimed here because a generic in the veterinary formulary is not a company
            # program. Molecules already in routine veterinary use are flagged so the white-space
            # route cannot be read as an open field.
            "in_veterinary_formulary": bool(re.search(
                r"furosemide|frusemide|sildenafil|tadalafil|enalapril|benazepril|amlodipine|"
                r"losartan|triamcinolone|betamethasone|prednisolone|methylprednisolone|"
                r"chlorambucil|vincristine|mitoxantrone|azathioprine|toceranib|"
                r"spironolactone|digoxin|diltiazem|atenolol|clonidine|epinephrine|prednisolone|"
                r"dexamethasone|cyclosporine|ketoconazole|metronidazole|doxycycline|gabapentin|"
                r"tramadol|buprenorphine|methimazole|levothyroxine|insulin|phenobarbital|"
                r"cytarabine|doxorubicin|vincristine|cyclophosphamide|carboplatin|lomustine",
                (ingredient or "") + " " + (r.get("drug_name") or ""), re.I)),
            # "License and caninise" assumes a molecule that can be licensed and reformulated.
            # Cell and gene therapies are a different program shape entirely.
            "not_a_licensing_shape": bool(re.search(
                r"\bCAR-?T\b|autologous|multicellular|cell therapy|gene therapy|oncolytic|"
                r"\bsiRNA\b|vaccine", (target or "") + " " + (r.get("drug_name") or ""), re.I)),
            # Why a program was dropped decides whether it is a candidate at all, and it is
            # partly recoverable from the source link rather than unknowable: a molecule withdrawn
            # over a survival detriment is not licensable inventory. Safety withdrawals are
            # excluded outright below; the rest carry their signal so a reader can weigh it.
            "discontinuation_signal": disc_signal(r) if discontinued(r) else None,
            "discontinuation_reason": (vr or {}).get("reason") if discontinued(r) else None,
            "discontinuation_note": (vr or {}).get("note") if discontinued(r) else None,
            "discontinuation_verified": bool(vr and vr.get("verified")),
            "source": r.get("source_link"),
        })

    # Row-level gates above are applied per supplied program; the gates below are applied per
    # molecule, after dedup. The funnel has to show the dedup step between them or its arithmetic
    # cannot reconcile: subtracting molecule-level counts from a row-level total does not work.
    n_rows_surviving = len(candidates)

    # One row per molecule: biosimilars and repeat listings are the same licensing opportunity
    # (Mvasi and Alymsys are both bevacizumab; Eliquis is listed twice).
    best = {}
    for c in sorted(candidates, key=lambda c: (c["years_since_approval"] or 999)):
        key = norm(BIOSIMILAR.sub("", c["ingredient"] or "")) or norm(c["drug"])
        if key in best:
            best[key].setdefault("also_marketed_as", []).append(c["drug"])
            continue
        best[key] = c

    # Routes. A candidate needs BOTH legs of human evidence - safety and efficacy - and then either
    # no companion-animal program against its target, or a stop unrelated to clinical performance.
    #
    # An approval carries both legs by definition. A discontinued asset carries them only if it
    # reached a stage where efficacy could show AND was stopped for some other reason: an efficacy
    # failure is disqualifying, because demonstrated efficacy is the premise of the whole approach.
    # Active Phase 2/3 assets have no approval behind them, so they are a watch list, not candidates.
    def route_of(c):
        if c["human_status"] == "active" and c["human_stage"] == "Approved":
            # A mechanism a companion-animal product already works is not a licensing opportunity,
            # so what used to be route2 is an exclusion rather than a presented route (A31).
            return None if c["competitor_count"] else "route1"
        if (c["human_status"] == "discontinued" and c.get("discontinuation_verified")
                and c.get("discontinuation_reason") == "non-clinical"
                and STAGE_RANK[c["human_stage"]] <= 2):
            return "route3"
        if c["human_status"] == "active" and c["human_stage"] in ("Phase 2", "Phase 3"):
            return "watch"
        return None

    for c in best.values():
        c["route"] = route_of(c)
    # Route names say what was actually established: that no branded program works the molecule's
    # MECHANISM. "No companion-animal program" read as "untried in dogs", which is a different and
    # much stronger claim - paclitaxel has 156 veterinary publications and no branded program (A19).
    ROUTE_LABEL = {
        "route1": "Approved, mechanism unclaimed in dogs or cats",
        "route3": "Shelved for a verified non-clinical reason",
        "watch": "Human pipeline, not yet approved",
    }
    for c in best.values():
        c["route_label"] = ROUTE_LABEL.get(c["route"])
    held = [c for c in best.values() if c["route"] is None]
    for c in held:
        if c["human_status"] == "active" and c["human_stage"] == "Approved":
            skipped["a companion-animal product already works this mechanism"] += 1
        else:
            skipped["discontinued on clinical performance, or reason not established"] += 1

    # Companion-animal crowding, computed here and stored, because the two program CSVs live
    # outside the repository and the site build in CI reads only committed data.
    CROWD = [("Parasites", r"flea|tick|worm|mite|parasit"),
             ("Infection", r"bacterial|infection|otitis"),
             ("Osteoarthritis and joints", r"osteoarthritis|joint|lameness|mobility"),
             ("Oncology", r"tumou?r|cancer|lymphoma|sarcoma|mast cell"),
             ("Endocrine and metabolic", r"diabet|thyroid|addison|cushing|obesity|weight"),
             ("Atopic dermatitis and pruritus", r"atopic|pruritus|allerg"),
             ("Cardiac", r"heart failure|cardi|mmvd|\bdcm\b"),
             ("Behavior and anxiety", r"anxiet|noise|behavio|stress"),
             ("Gastrointestinal", r"diarrh|vomit|nausea"),
             ("Renal", r"kidney|renal|\bckd\b")]
    crowding = sorted(
        [{"indication": lab,
          "programs": sum(1 for r in pet if re.search(pat, r.get("indication") or "", re.I))}
         for lab, pat in CROWD],
        key=lambda x: -x["programs"])

    # Areas ranked on the review's evidence; candidates grouped under the area they belong to.
    def area_rank(a):
        e = ev[a]
        depth = min(e["level_A"] + 0.5 * e["level_B"], 20) / 20
        return round(e["weighted_concordance"] * 50 + depth * 50, 1)

    grouped = collections.defaultdict(list)
    for c in best.values():
        if c["route"]:
            grouped[c["area"]].append(c)
    # Phase 1 and preclinical assets have no human efficacy yet, which is the whole premise, so they
    # are carried in the data as a watch list rather than presented as candidates.
    PRESENTED_ROUTES = {"route1", "route3"}
    is_presented = lambda c: c["route"] in PRESENTED_ROUTES
    ROUTE_ORDER = {"route1": 0, "route3": 1}

    # ---- Prioritisation (A32). Three legs, kept separate and never pre-blended, so the page can
    # say WHY a candidate ranks where it does instead of showing one opaque number.
    #
    #   concordance  this review's own evidence for the area, weighted by level (area_rank above)
    #   unmet need   inverted companion-animal crowding: fewer products for the condition scores higher
    #   market       hand-curated human franchise scale per mechanism class, each with a source
    #
    # The market leg is a PROXY, and a coarse one. It says how big the mechanism is in PEOPLE. It is
    # not a claim about the companion-animal opportunity: prevalence, market size and willingness to
    # pay are absent from this repository entirely and are probably the largest determinant of
    # programme value. Two cheaper proxies were tried and rejected - counting human programs per
    # target measured how generic the target STRING is (Dupixent scored the floor), and approval age
    # mis-sorted the route-2 molecules. market_tiers.json records both so neither is retried.
    TIERS = load("part2/market_tiers.json") or {}
    TIER_CLASSES, TIER_OVERRIDE = TIERS.get("classes") or {}, TIERS.get("molecule_overrides") or {}
    MARKET_CLASS = [
        ("anti-TNF", r"\btnf\b"), ("IL-4R / type 2 inflammation", r"il-4r"), ("IL-6R", r"il-6r"),
        # CTLA-4-Ig (Orencia, immunology) is tested before the CTLA-4 antibody (Yervoy, oncology):
        # they share a target name and are different products in different markets.
        ("CTLA-4-Ig (immunology)", r"ctla-4-ig|abatacept"),
        ("checkpoint inhibitor (oncology)", r"ipilimumab|pd-1|pd-l1|ctla-4"),
        ("BTK inhibitor", r"\bbtk\b"), ("CDK4/6 inhibitor", r"cdk4/6"), ("PARP inhibitor", r"parp"),
        ("HER2-targeted", r"her2|trastuzumab|pertuzumab"), ("VEGF / VEGFR", r"vegf"),
        ("ADC", r"\badc\b|vedotin|diftitox"), ("FGFR inhibitor", r"fgfr"),
        ("BRAF / MEK / RAF", r"braf|\bmek\b|\braf\b"),
        ("SERD / ER-targeted", r"estrogen receptor|protac er"),
        ("IL-2 / IL-15 cytokine", r"il-2|il-15"), ("oncolytic virus", r"oncolytic|laherparepvec"),
        ("cytotoxic chemotherapy", r"paclitaxel|cytarabine|gemcitabine"),
        ("PAH vasodilator", r"endothelin|prostacyclin|pde5|guanylate|ip receptor"),
        ("TTR stabilizer / silencer", r"\bttr\b"), ("cardiac myosin inhibitor", r"cardiac myosin"),
        ("Factor Xa anticoagulant", r"factor xa"),
        ("cardiovascular generic", r"angiotensin|loop diuretic|mineralocorticoid|hcn/if|vasopressin"),
        ("corticosteroid", r"corticosteroid|glucocorticoid"), ("ACTH", r"melanocortin|acth"),
    ]
    TIER_SCORE = {"blockbuster": 100, "large": 70, "mid": 40, "small": 15}

    def market_class(c):
        hay = " ".join(str(c.get(k) or "") for k in ("target", "ingredient", "drug")).lower()
        for label, pat in MARKET_CLASS:
            if re.search(pat, hay):
                return label
        return None

    crowd_by_label = {r["indication"]: r["programs"] for r in crowding}
    max_crowd = max(crowd_by_label.values()) if crowd_by_label else 0

    # The crowding vocabulary is written around companion-animal indications, so human labels miss
    # it even when the area is unambiguous: "melanoma" and "glioma" are not in the Oncology pattern,
    # and the anti-TNFs read "Autoimmune disease". Falling back to the area rescues all 12 that the
    # patterns stranded. The fallback is AREA-level and therefore coarse - every immunology
    # candidate lands on atopic dermatitis, which is right for Dupixent and the anti-TNFs and is an
    # approximation for Cortrophin Gel. It is used only to size crowding, never to claim the
    # candidate treats that condition.
    AREA_CROWD = {"oncology": "Oncology", "cardiovascular": "Cardiac",
                  "musculoskeletal": "Osteoarthritis and joints",
                  "immunology-inflammation": "Atopic dermatitis and pruritus"}

    def crowd_bucket(c):
        hay = ((c.get("indication") or "") + " " + (c.get("area") or "")).lower()
        for label, pat in CROWD:
            if re.search(pat, hay):
                return label, "indication"
        a = AREA_CROWD.get(c.get("area"))
        return (a, "area") if a else (None, None)

    for c in best.values():
        if not is_presented(c):
            continue
        klass = market_class(c)
        # A product-level figure that contradicts its class wins. Cometriq is why this exists: it
        # would inherit cabozantinib's $1.8B franchise, but Cometriq itself is $2.4M.
        ov = TIER_OVERRIDE.get(c.get("drug") or "")
        entry = ov or (TIER_CLASSES.get(klass) if klass else None) or {}
        tier = entry.get("tier", "not established")
        bucket, bucket_via = crowd_bucket(c)
        # No crowding bucket means UNKNOWN, not uncrowded. Scoring it zero would sink a candidate
        # for missing data rather than for a saturated market.
        unmet = round(100 * (1 - crowd_by_label[bucket] / max_crowd), 1) if bucket and max_crowd else None
        market_score = TIER_SCORE.get(tier)
        legs = [x for x in (area_rank(c["area"]), unmet, market_score) if x is not None]
        c["priority"] = {
            "market_tier": tier, "market_class": klass,
            "market_basis": entry.get("basis"), "market_source": entry.get("source"),
            "market_is_override": bool(ov),
            "unmet_bucket": bucket, "unmet_programs": crowd_by_label.get(bucket),
            "unmet_via": bucket_via, "unmet_score": unmet,
            "concordance_score": area_rank(c["area"]),
            # Fixed denominator of three. A mean over only the PRESENT legs rewards having fewer,
            # better ones: it put two assets with no market evidence at all (Attruby, aficamten)
            # third and fourth, above Dupixent and its sourced blockbuster tier. Filling the gap
            # was worse in both directions - the corpus median still floated them into the top ten,
            # and zero penalised a molecule for evidence nobody has looked up, which is the
            # "absence of a finding is not absence of the thing" error the register warns about.
            # Dividing by three regardless caps an incomplete candidate below a complete one by
            # construction, while the row still reads "market not established" rather than "small".
            "score": round(sum(legs) / 3, 1),
            "legs_present": len(legs),
            "score_is_partial": len(legs) < 3,
        }

    areas = [{"area": a, "evidence_rank": area_rank(a),
              "candidates": len([c for c in v if is_presented(c)]),
              "watch_list": len([c for c in v if c["route"] == "watch"]),
              "evidence": ev[a],
              "molecules": sorted([c for c in v if is_presented(c)],
                                  key=lambda c: (ROUTE_ORDER[c["route"]],
                                                 not c["precedent"],
                                                 (c["drug"] or "").lower())),
              "watch": sorted([c for c in v if c["route"] == "watch"],
                              key=lambda c: (c["drug"] or "").lower())}
             for a, v in grouped.items()]
    areas.sort(key=lambda x: -x["evidence_rank"])
    candidates = sorted([c for a in areas for c in a["molecules"]],
                        key=lambda c: (-(c.get("priority") or {}).get("score", 0),
                                       -(c.get("priority") or {}).get("legs_present", 0),
                                       (c.get("drug") or "").lower()))
    # Rank is assigned after the sort, because it is a position in this ordering rather than a
    # property of the molecule. The site reads it directly instead of re-deriving the order.
    for i, c in enumerate(candidates, 1):
        c["priority"]["rank"] = i
    watch = [c for a in areas for c in a["watch"]]
    route_counts = collections.Counter(c["route"] for c in candidates)
    out = {
        "built": today(),
        "inputs": {"human_programs": len(human), "pet_programs": len(pet),
                   "review_results": len(results)},
        "skipped": dict(skipped),
        "rows_surviving": n_rows_surviving,
        "molecules_after_dedup": len(best),
        "deduplicated": n_rows_surviving - len(best),
        "route_labels": ROUTE_LABEL,
        "route_counts": {k: route_counts.get(k, 0) for k in ("route1", "route3")},
        "watch_count": len(watch),
        "watch": watch,
        "crowding": crowding,
        "missing_inputs": [
            "Canine and feline disease prevalence: no epidemiological source is held in this "
            "repository, so no candidate is weighted by how many animals have the disease. This is "
            "probably the largest single determinant of program value and it is absent. The "
            "veterinary literature's attention (osteoarthritis 42 pairs, atopic dermatitis 31, "
            "lymphoma 25) measures what researchers study, not what dogs get, and is deliberately "
            "NOT used as a substitute.",
            "Willingness to pay and market size by indication.",
            "Patent and exclusivity status: years since first approval is a crude proxy for whether "
            "a molecule can be licensed cheaply, and says nothing about who controls it now.",
            "Target animal safety: the exclusion list is reviewer-supplied and incomplete. An absent "
            "flag means not checked, never safe.",
            "Formulation and route feasibility, palatability, and dosing interval in the target species.",
        ],
        "dog_evidence_by_area": ev,
        "areas": areas,
        "candidates": candidates,
    }
    save(out, "part2/caninisation_candidates.json")
    print(f"candidates: {len(candidates)} molecules (from {len(human)} human programs)")
    print("routes:", dict(route_counts), "| watch list:", len(watch))
    print("skipped:", dict(skipped))
    for a in areas:
        e = a["evidence"]
        print(f"\n=== {a['area']}  (area evidence rank {a['evidence_rank']}; "
              f"{e['corresponded']}/{e['corresponded'] + e['did_not']} corresponded, "
              f"{e['level_A']} of {e['results']} results are intervention outcomes, "
              f"{e['studies']} studies)")
        for c in a["molecules"][:8]:
            mark = "*" if c["precedent"] else ("!" if c["safety_flags"] else " ")
            print(f"  {mark} {(c['drug'] or '')[:32]:<34}{(c['ingredient'] or '-')[:20]:<22}"
                  f"{(c['target'] or '-')[:26]:<28}"
                  f"{('approved ' + str(c['first_us_approval'])) if c['first_us_approval'] else 'approval year unknown':<24}")
        if len(a["molecules"]) > 8:
            print(f"    ... and {len(a['molecules']) - 8} more")
    print("\n* = class has a dog-first precedent   ! = carries a species safety caution")
    print("resolved ingredient:", sum(1 for c in candidates if c["ingredient"]),
          "| approval year:", sum(1 for c in candidates if c["first_us_approval"]))


if __name__ == "__main__":
    main()
