"""Minimal PubMed E-utilities harness. Caches every response under data/raw/cache/."""
import json, os, time, hashlib, urllib.parse, urllib.request

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "cache")
os.makedirs(CACHE, exist_ok=True)
TOOL = {"tool": "animal-model-concordance", "email": "rsatija@stanford.edu"}

def _get(endpoint, params):
    q = urllib.parse.urlencode({**params, **TOOL})
    url = f"{BASE}/{endpoint}.fcgi?{q}"
    key = hashlib.sha1(url.encode()).hexdigest()[:20]
    path = os.path.join(CACHE, f"{endpoint}_{key}.json")
    if os.path.exists(path):
        return json.load(open(path))
    time.sleep(0.4)
    # E-utilities caps GET URIs; long boolean queries must go by POST.
    if len(url) > 1800:
        req = urllib.request.Request(f"{BASE}/{endpoint}.fcgi", data=q.encode())
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode())
    json.dump(data, open(path, "w"))
    return data

def esearch(term, retmax=0):
    r = _get("esearch", {"db": "pubmed", "retmode": "json", "retmax": retmax, "term": term})["esearchresult"]
    return int(r["count"]), r.get("idlist", []), r.get("querytranslation", "")

def esummary(pmids):
    if not pmids: return {}
    out = {}
    for i in range(0, len(pmids), 150):
        chunk = pmids[i:i+150]
        r = _get("esummary", {"db": "pubmed", "retmode": "json", "id": ",".join(chunk)})["result"]
        for p in chunk:
            d = r.get(p)
            if d: out[p] = {"title": d.get("title",""), "journal": d.get("source",""),
                            "year": (d.get("pubdate","") or "")[:4],
                            "authors": [a["name"] for a in d.get("authors",[])][:3],
                            "type": d.get("pubtype",[])}
    return out
