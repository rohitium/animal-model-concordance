"""Resolve open-access full text for the pilot slice.

Only openly-licensed content is fetched: Europe PMC OA full-text XML, PMC, and
Unpaywall-listed OA PDFs. Paywalled articles are reported for manual supply, never
circumvented. PDFs land in data/raw/fulltext/ which is gitignored -- full texts are
copyrighted and must not be committed or published.
"""
import sys, os, json, time, urllib.request, urllib.parse
ROOT = os.path.join(os.path.dirname(__file__), "..")
FT = os.path.join(ROOT, "data", "raw", "fulltext")
os.makedirs(FT, exist_ok=True)
EMAIL = "rsatija@stanford.edu"
UA = {"User-Agent": f"animal-model-concordance/1.0 (mailto:{EMAIL})"}

def get(url, timeout=60, binary=False):
    for a in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read() if binary else r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 ** a)
    return None

db = json.load(open(os.path.join(ROOT, "data", "db", "studies.json")))
pmids = list(db)
print(f"resolving OA full text for {len(pmids)} studies\n")

STATUS_PATH = os.path.join(ROOT, "data", "raw", "fulltext_status.json")
status = json.load(open(STATUS_PATH)) if os.path.exists(STATUS_PATH) else {}
def save(): json.dump(status, open(STATUS_PATH, "w"), indent=1)

for i, pm in enumerate(pmids, 1):
    # Resume: skip anything already on disk. The first run was killed partway
    # and lost its whole state, so progress is now checkpointed every record.
    have_x = os.path.exists(os.path.join(FT, f"{pm}.xml"))
    have_p = os.path.exists(os.path.join(FT, f"{pm}.pdf"))
    if pm in status and (status[pm].get("xml") or status[pm].get("pdf")):
        continue
    if have_x or have_p:
        status[pm] = {"pmid": pm, "pmcid": None, "doi": None, "oa": True,
                      "route": "recovered_from_disk",
                      "xml": os.path.relpath(os.path.join(FT, f"{pm}.xml"), ROOT) if have_x else None,
                      "pdf": os.path.relpath(os.path.join(FT, f"{pm}.pdf"), ROOT) if have_p else None,
                      "license": None}
        continue
    rec = {"pmid": pm, "pmcid": None, "doi": None, "oa": False, "route": None,
           "xml": None, "pdf": None, "license": None}
    # Europe PMC: OA status, PMCID, DOI, full-text availability
    q = urllib.parse.quote(f"EXT_ID:{pm} AND SRC:MED")
    js = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}"
             f"&resultType=core&format=json")
    if js:
        try:
            rs = json.loads(js).get("resultList", {}).get("result", [])
            if rs:
                r0 = rs[0]
                rec["pmcid"] = r0.get("pmcid")
                rec["doi"] = r0.get("doi")
                rec["license"] = r0.get("license")
                rec["oa"] = str(r0.get("isOpenAccess", "N")).upper() == "Y"
        except Exception:
            pass
    # Route 1: Europe PMC full-text XML (OA subset)
    if rec["pmcid"]:
        xml = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{rec['pmcid']}/fullTextXML")
        if xml and "<article" in xml[:4000]:
            p = os.path.join(FT, f"{pm}.xml")
            open(p, "w", encoding="utf-8").write(xml)
            rec["xml"] = os.path.relpath(p, ROOT); rec["route"] = "europepmc_xml"
    # Route 2: OA PDF via Unpaywall
    if not rec["xml"] and rec["doi"]:
        js = get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(rec['doi'])}?email={EMAIL}")
        if js:
            try:
                d = json.loads(js)
                loc = d.get("best_oa_location") or {}
                url = loc.get("url_for_pdf")
                if d.get("is_oa") and url:
                    rec["oa"] = True
                    rec["license"] = rec["license"] or loc.get("license")
                    blob = get(url, timeout=90, binary=True)
                    if blob and blob[:4] == b"%PDF":
                        p = os.path.join(FT, f"{pm}.pdf")
                        open(p, "wb").write(blob)
                        rec["pdf"] = os.path.relpath(p, ROOT); rec["route"] = "unpaywall_pdf"
            except Exception:
                pass
    # Route 3: PMC PDF for OA-subset records without Europe PMC XML
    if not rec["xml"] and not rec["pdf"] and rec["pmcid"]:
        blob = get(f"https://www.ncbi.nlm.nih.gov/pmc/articles/{rec['pmcid']}/pdf/",
                   timeout=90, binary=True)
        if blob and blob[:4] == b"%PDF":
            p = os.path.join(FT, f"{pm}.pdf")
            open(p, "wb").write(blob)
            rec["pdf"] = os.path.relpath(p, ROOT); rec["route"] = "pmc_pdf"
    status[pm] = rec
    save()
    if i % 20 == 0:
        got = sum(1 for v in status.values() if v["xml"] or v["pdf"])
        print(f"  {i}/{len(pmids)}  retrieved={got}")
    time.sleep(0.34)

save()
got = [v for v in status.values() if v["xml"] or v["pdf"]]
xml = [v for v in got if v["xml"]]; pdf = [v for v in got if v["pdf"]]
print(f"\nretrieved {len(got)}/{len(pmids)}  (xml {len(xml)}, pdf {len(pdf)})")
print(f"not retrieved: {len(pmids)-len(got)}")
import collections
print("routes:", dict(collections.Counter(v["route"] for v in status.values())))
