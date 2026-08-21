"""Second pass for full texts Unpaywall/PMC did not yield, using OpenAlex and
Semantic Scholar OA locations. Open access only; paywalls are never circumvented."""
import os, json, time, urllib.request, urllib.parse
ROOT = os.path.join(os.path.dirname(__file__), "..")
FT = os.path.join(ROOT, "data", "raw", "fulltext")
EMAIL = "rsatija@stanford.edu"
UA = {"User-Agent": f"animal-model-concordance/1.0 (mailto:{EMAIL})"}

def get(url, binary=False, timeout=60):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read() if binary else r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(1.5 * (a + 1))
    return None

st = json.load(open(os.path.join(ROOT, "data", "raw", "fulltext_status.json")))
meta = json.load(open(os.path.join(ROOT, "data", "db", "metadata.json")))
missing = [pm for pm, v in st.items() if not (v.get("xml") or v.get("pdf"))]
print(f"attempting {len(missing)} without full text")

found = 0
for i, pm in enumerate(missing, 1):
    doi = (meta.get(pm) or {}).get("doi")
    urls = []
    # OpenAlex
    key = f"doi:{doi}" if doi else f"pmid:{pm}"
    js = get(f"https://api.openalex.org/works/{urllib.parse.quote(key)}?mailto={EMAIL}")
    if js:
        try:
            d = json.loads(js)
            for loc in ([d.get("best_oa_location")] + (d.get("locations") or [])):
                if loc and loc.get("pdf_url"): urls.append(loc["pdf_url"])
        except Exception: pass
    # Semantic Scholar
    js = get(f"https://api.semanticscholar.org/graph/v1/paper/PMID:{pm}?fields=openAccessPdf")
    if js:
        try:
            oa = (json.loads(js) or {}).get("openAccessPdf") or {}
            if oa.get("url"): urls.append(oa["url"])
        except Exception: pass
    for u in dict.fromkeys(urls):
        blob = get(u, binary=True, timeout=90)
        if blob and blob[:4] == b"%PDF" and len(blob) > 20000:
            p = os.path.join(FT, f"{pm}.pdf")
            open(p, "wb").write(blob)
            st[pm].update({"pdf": os.path.relpath(p, ROOT), "oa": True, "route": "openalex_s2_pdf"})
            found += 1
            break
    json.dump(st, open(os.path.join(ROOT, "data", "raw", "fulltext_status.json"), "w"), indent=1)
    time.sleep(0.4)
    if i % 15 == 0: print(f"  {i}/{len(missing)} tried, {found} new")

print(f"\nnew full texts: {found}")
got = sum(1 for v in st.values() if v.get("xml") or v.get("pdf"))
print(f"total coverage: {got}/{len(st)}")
