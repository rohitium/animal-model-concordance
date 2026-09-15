"""Reference-data snapshots for the drug-pair table (PLAN.md v0.4 §7; user decision 2026-09-14).

Human-side evidence and the "agent exists in human medicine" filter are computed from frozen local
copies, not live API searches, so results are exhaustive and reproducible. US sources only (user
decision). Every file is recorded with source URL, retrieval date, size and SHA-256.

Files (data/raw/snapshots/, gitignored):
  drugsatfda/   Drugs@FDA data files (approvals, application history)          ~6 MB
  openfda_ndc/  openFDA NDC directory (marketed US human drugs, ingredients)   ~27 MB
  openfda_label/ openFDA drug labels, all partitions (indications text)        ~1.8 GB
  aact/         AACT daily flat-file export of ClinicalTrials.gov              ~2.35 GB
Output: data/v04/frames/snapshots_manifest.json
"""
import sys, os, json, hashlib, urllib.request, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

DEST = J("data", "raw", "snapshots")
UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/124 Safari/537.36"

def files():
    idx = json.loads(urllib.request.urlopen("https://api.fda.gov/download.json", timeout=60).read())["results"]["drug"]
    out = [("drugsatfda", "https://www.fda.gov/media/89850/download", "drugsatfda.zip"),
           ("aact", "https://aact.ctti-clinicaltrials.org/static/exported_files/daily/2026-09-14?source=web",
            "20260914_export_ctgov.zip")]
    for p in idx["ndc"]["partitions"]:
        out.append(("openfda_ndc", p["file"], os.path.basename(p["file"])))
    for p in idx["label"]["partitions"]:
        out.append(("openfda_label", p["file"], os.path.basename(p["file"])))
    return out, {"label_export": idx["label"]["export_date"], "ndc_export": idx["ndc"]["export_date"]}

def fetch(job):
    group, url, name = job
    d = os.path.join(DEST, group)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        tmp = path + ".part"
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        os.replace(tmp, path)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"group": group, "url": url, "path": os.path.relpath(path, ROOT),
            "bytes": os.path.getsize(path), "sha256": h.hexdigest()}

def main():
    jobs, meta = files()
    print(f"{len(jobs)} files")
    rows, failed = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(fetch, j): j for j in jobs}
        for f in cf.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:           # one unreachable file must not lose the others' manifest
                g, url, name = futs[f]
                failed.append({"group": g, "url": url, "error": f"{type(e).__name__}: {str(e)[:200]}"})
                print(f"  FAILED {g}: {url} ({type(e).__name__})", flush=True)
                continue
            rows.append(r)
            print(f"  {r['group']:14s} {r['bytes']/1e6:8.1f} MB  {os.path.basename(r['path'])}", flush=True)
    save({"retrieved": today(), **meta, "files": sorted(rows, key=lambda r: r["path"]), "failed": failed},
         "frames/snapshots_manifest.json")
    print(f"total {sum(r['bytes'] for r in rows)/1e9:.2f} GB")

if __name__ == "__main__":
    main()
