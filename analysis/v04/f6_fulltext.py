"""Open-access full text for studies advanced by screening (amendment A6).

Routes, in order, open access only (no paywall is circumvented):
  1. a PDF already held in data/raw/fulltext/
  2. OpenAlex OA locations (best_oa_location and every location with a pdf_url)
  3. Unpaywall OA locations by DOI
  4. Europe PMC PDF render for articles with a PMCID
A download counts only if the bytes start with %PDF. Anything not found is written to
docs/fulltext_wanted_v04.md for the user to supply through institutional access.

Input:  data/v04/retrieval/screen_strict.json (include/uncertain) + candidates.json
Output: data/raw/fulltext/<pmid or openalex>.pdf (gitignored), data/v04/retrieval/fulltext_status.json
"""
import sys, os, json, time, urllib.request, urllib.parse, collections
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

FT = J("data", "raw", "fulltext")
EMAIL = "rsatija@stanford.edu"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; animal-model-concordance/1.0; mailto:{EMAIL})"}

def fetch(url, binary=True, timeout=60):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            data = r.read()
        return data if binary else json.loads(data)
    except Exception:
        return None

def key_of(c):
    return c.get("pmid") or c.get("openalex")

def try_pdf(url):
    data = fetch(url)
    return data if data and data[:4] == b"%PDF" else None

def get_one(k, c):
    name = key_of(c)
    path = os.path.join(FT, f"{name}.pdf")
    if os.path.exists(path):
        return name, {"status": "held", "path": os.path.relpath(path, ROOT)}
    urls = []
    if c.get("openalex"):
        w = fetch(f"https://api.openalex.org/works/{c['openalex']}?select=best_oa_location,locations,ids&mailto={EMAIL}", binary=False) or {}
        for loc in [w.get("best_oa_location")] + (w.get("locations") or []):
            if loc and loc.get("pdf_url"):
                urls.append(("openalex", loc["pdf_url"]))
        pmcid = ((w.get("ids") or {}).get("pmcid") or "").rsplit("/", 1)[-1]
    else:
        pmcid = ""
    if c.get("doi"):
        doi = c["doi"].replace("https://doi.org/", "")
        u = fetch(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}", binary=False) or {}
        for loc in [u.get("best_oa_location")] + (u.get("oa_locations") or []):
            if loc and loc.get("url_for_pdf"):
                urls.append(("unpaywall", loc["url_for_pdf"]))
    if pmcid:
        urls.append(("europepmc", f"https://europepmc.org/articles/{pmcid}?pdf=render"))
    seen = set()
    for route, url in urls:
        if url in seen:
            continue
        seen.add(url)
        data = try_pdf(url)
        if data:
            open(path, "wb").write(data)
            return name, {"status": "downloaded", "route": route, "url": url, "path": os.path.relpath(path, ROOT)}
        time.sleep(0.2)
    return name, {"status": "not-found", "tried": len(seen), "doi": c.get("doi"), "title": c.get("title"), "year": c.get("year")}

def main():
    strict = load("retrieval/screen_strict.json")
    cands = load("retrieval/candidates.json")
    # records that passed the strict second screening pass (include or uncertain)
    targets = {k: cands[k] for k, r in strict.items() if "error" not in r and r.get("decision") in ("include", "uncertain") and k in cands}
    status = load("retrieval/fulltext_status.json")
    todo = {k: c for k, c in targets.items() if key_of(c) not in status or status[key_of(c)]["status"] == "not-found"}
    print(f"full text: {len(targets)} advanced, {len(todo)} to resolve", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(get_one, k, c) for k, c in todo.items()]
        for i, f in enumerate(as_completed(futs), 1):
            name, st = f.result()
            status[name] = st
            if i % 50 == 0:
                save(status, "retrieval/fulltext_status.json")
                print(f"  {i}/{len(futs)} {collections.Counter(v['status'] for v in status.values())}", flush=True)
    save(status, "retrieval/fulltext_status.json")
    missing = sorted((v for v in status.values() if v["status"] == "not-found"), key=lambda v: -(v.get("year") or 0))
    with open(J("docs", "fulltext_wanted_v04.md"), "w") as f:
        f.write("# Full texts wanted (v0.4 expanded corpus)\n\nOpen-access routes found no PDF for these. "
                "Save each as `data/raw/fulltext/<PMID>.pdf` (or the OpenAlex ID shown).\n\n| key | year | title | DOI |\n|---|---|---|---|\n")
        for name, v in sorted(status.items(), key=lambda kv: -(kv[1].get("year") or 0)):
            if v["status"] == "not-found":
                f.write(f"| {name} | {v.get('year')} | {(v.get('title') or '')[:120]} | {v.get('doi') or ''} |\n")
    print(dict(collections.Counter(v["status"] for v in status.values())), f"wanted list: {len(missing)}")

if __name__ == "__main__":
    main()
