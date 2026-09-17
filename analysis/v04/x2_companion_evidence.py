"""Establish, per candidate molecule, what is actually known about companion-animal presence.

Amendment A19. The caninisation page previously answered "is this target claimed in dogs or cats?"
from one supplied spreadsheet of 328 branded programs, and printed "No program in the supplied
list targets this in dogs or cats" when the join found nothing. That sentence was doing two
dishonest jobs at once: it reported the limits of one file as though it were a fact about the world,
and the join underneath it was broken, so it also fired when the answer was in the file.

How badly: dupilumab (target "IL-4Ralpha") matched nothing, so a human atopic-dermatitis antibody
was shown as facing no companion-animal competition while canine atopic dermatitis carries Apoquel,
Cytopoint, Zenrelia, Befrena and five cyclosporine products. Ipilimumab ("CTLA-4") matched nothing
although VGS-001 is an anti-canine CTLA-4 antibody. ZILRETTA ("corticosteroid") matched nothing
although its own active, triamcinolone acetonide, is in GENESIS Topical Spray - already in the
indexed list. Widening the join to ingredient and brand tokens made it worse, not better:
vutrisiran matched a saline infusion on "sodium", ivabradine and gemcitabine matched a
dexmedetomidine injection on "hydrochloride", Cortrophin Gel matched ear gel on "gel". Inventing a
competitor is worse than reporting none, so token joining is abandoned here.

Absence is now asserted only after four named checks, and the page prints what each one found:

  1. Target mechanism   curated map (part2/companion_presence_map.json). An empty holder list is a
                        positive finding - the mechanism is named, looked for, and unoccupied.
  2. Companion condition curated map. The crowding a developer actually faces, which is a different
                        question from who holds the target: a mechanism can be wide open inside an
                        indication with fifteen incumbents.
  3. Veterinary literature  deterministic PubMed search, cached, no model involved. Names are
                        normalized first: querying the salt form returned zero for ivabradine,
                        cabozantinib, lenvatinib and trastuzumab, all of which have canine
                        literature under their base name.
  4. This review's own pair corpus  drug-and-indication pairs with companion-animal evidence.

NOT CHECKED, and declared rather than implied: no approved-animal-drug registry. The FDA Green Book
publishes no machine-readable export, openFDA's animal endpoint carries adverse events rather than
approved products, and the EMA veterinary dataset has moved behind a portal with no download. So a
molecule can be approved for dogs somewhere and show nothing here. "Not found" never means "absent".

Output: data/v04/part2/companion_evidence.json
"""
import sys, os, re, json

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "analysis"))
from common import load, save, today  # noqa
import pubmed  # noqa

# Salt, ester and hydrate forms, and the four-letter FDA biologic suffix. Searching PubMed for the
# salt form is the same pattern-looks-right, matches-nothing failure this project keeps hitting:
# "vutrisiran sodium" returns 0 and "vutrisiran" is the molecule anyone writes about.
SALT = (r"(sodium|potassium|calcium|magnesium|disodium|hydrochloride|hydrobromide|besylate|"
        r"mesylate|tosylate|citrate|sulfate|sulphate|phosphate|acetate|tartrate|maleate|fumarate|"
        r"succinate|s-malate|malate|pivalate|acetonide|dipropionate|furoate|xinafoate|pamoate|"
        r"embonate|mofetil|hemihydrate|monohydrate|dihydrate|anhydrous)")
BIO_SUFFIX = r"-(?:[a-z]{4})\b"
JUNK = {"generic", "undisclosed", "none", "various", "vaccine", "biologic"}


def search_name(ingredient, drug):
    """The name to search PubMed under, or None when no single molecule name can be resolved."""
    for raw in (ingredient, drug):
        if not raw:
            continue
        s = re.split(r"[;/]| \+ |,| and ", str(raw))[0].strip()
        s = re.sub(BIO_SUFFIX, "", s, flags=re.I)
        s = re.sub(r"\b" + SALT + r"\b", "", s, flags=re.I).strip()
        s = re.sub(r"\(.*?\)", "", s).strip(" -")
        if s.lower() in JUNK or len(s) < 4 or len(s.split()) > 2:
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 \-']{3,40}", s):
            continue
        return s
    return None


def vet_literature(name):
    """Veterinary literature for a molecule: total, and the treatment-flavoured subset."""
    base = f'"{name}"[tiab] AND (dogs[mh] OR cats[mh] OR canine[tiab] OR feline[tiab])'
    hits, ids, _ = pubmed.esearch(base, retmax=3)
    clin, _, _ = pubmed.esearch(
        base + " AND (therapy[sh] OR treatment[tiab] OR trial[tiab] OR clinical[tiab])", retmax=0)
    return {"query": base, "hits": hits, "clinical": clin, "pmids": ids}


def main():
    cand = load("part2/caninisation_candidates.json") or {}
    cmap = load("part2/companion_presence_map.json") or {}
    classes = cmap.get("target_classes") or []
    indications = cmap.get("indication_map") or []
    pairs = load("part2/pairs.json") or {}

    norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
    corpus = {}
    for k, v in pairs.items():
        corpus.setdefault(norm(k.split("|")[0]), []).append(v.get("veterinary_indication"))

    out, counts = {}, {}
    molecules = (cand.get("candidates") or []) + (cand.get("watch") or [])
    for i, c in enumerate(molecules):
        hay = " ".join([c.get("target") or "", c.get("ingredient") or "", c.get("drug") or ""]).lower()
        klass = next((t for t in classes if re.search(t["match"], hay, re.I)), None)
        ind = next((x for x in indications
                    if re.search(x["match"], c.get("indication") or "", re.I)), None)

        nm = search_name(c.get("ingredient"), c.get("drug"))
        lit = None
        if nm:
            try:
                lit = vet_literature(nm)
            except Exception as e:
                lit = {"error": str(e)[:80]}

        key = norm(c.get("ingredient")) or norm(c.get("drug"))
        in_corpus = corpus.get(key) or corpus.get(norm(c.get("drug"))) or []

        # Patents and halted programs are separate evidence from marketed products, and they
        # change the answer. Elanco wrote off a pet-health IL-4R asset in 2024 and at least four
        # companies have filed on anti-canine IL-4Ralpha, yet no IL-4R product is marketed for dogs,
        # so a marketed-products-only view called that mechanism unoccupied.
        patents = (klass or {}).get("patents") or []
        halted = (klass or {}).get("halted") or []

        # The verdict is a summary of the checks, never a claim beyond them.
        if klass and klass["holders"]:
            status = "a companion-animal program works this mechanism"
        elif patents or halted:
            status = "no marketed product, but the mechanism is claimed or was attempted"
        elif ind and ind["holders"]:
            status = "mechanism unoccupied, but the condition is contested"
        elif (lit and lit.get("clinical")) or in_corpus:
            status = "no program found, but used or studied in dogs or cats"
        elif klass or ind:
            status = "no program, and no veterinary literature found"
        else:
            status = "not classified"
        counts[status] = counts.get(status, 0) + 1

        out[c["drug"]] = {
            "ingredient": c.get("ingredient"),
            "searched_as": nm,
            "target_class": klass["class"] if klass else None,
            "target_holders": klass["holders"] if klass else None,
            "target_patents": patents,
            "target_halted": halted,
            "target_note": (klass or {}).get("note"),
            "companion_condition": ind["companion_condition"] if ind else None,
            "condition_holders": ind["holders"] if ind else None,
            "condition_note": (ind or {}).get("note"),
            "vet_literature": lit,
            "pair_corpus": sorted({str(x) for x in in_corpus if x})[:6],
            "status": status,
        }
        if i % 40 == 0:
            print(f"  ...{i}/{len(molecules)}", flush=True)

    save({
        "built": today(),
        "sources_checked": [
            "Curated target-mechanism map over the supplied companion-animal program list",
            "Curated human-indication to companion-condition map over the same list",
            "PubMed veterinary literature search, deterministic and cached",
            "This review's own classified drug-pair corpus",
            "Curated patent filings and halted or written-off companion-animal programs, for the "
            "mechanisms where these were searched by hand, each carrying its source",
        ],
        "sources_not_checked": [
            "No approved-animal-drug registry. The FDA Green Book publishes no machine-readable "
            "export, openFDA's animal endpoint carries adverse events rather than approved products, "
            "and the EMA veterinary dataset has no download. A molecule approved for dogs or cats "
            "outside the supplied list would not be detected here.",
            "No systematic patent search. Google Patents has no documented public API and rate-limits "
            "automated querying, so patent evidence is hand-curated per mechanism rather than swept "
            "across every candidate. A mechanism with no patent entry has not been searched, and "
            "must not be read as free of intellectual property.",
            "No systematic sweep of discontinued or written-off companion-animal programs. These "
            "surface in company results and press releases rather than in any register, and are "
            "recorded per mechanism as they are found.",
        ],
        "status_counts": counts,
        "molecules": out,
    }, "part2/companion_evidence.json")
    print(f"companion evidence for {len(out)} molecules")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
