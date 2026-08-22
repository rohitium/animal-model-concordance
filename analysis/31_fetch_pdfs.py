"""Fetch OA PDFs for studies we hold only as XML.

Question-driven extraction reads the PDF directly, so tables and figures are visible to
the model. XML carries table markup but not figure content, so a PDF is strictly better
input where one is openly available."""
import json, os, time, urllib.request
ROOT=os.path.join(os.path.dirname(__file__),"..")
J=lambda *p: os.path.join(ROOT,*p)
FT=J("data","raw","fulltext")
UA={"User-Agent":"Mozilla/5.0 (compatible; animal-model-concordance/1.0; mailto:rsatija@stanford.edu)"}
st=json.load(open(J("data","raw","fulltext_status.json")))
db=json.load(open(J("data","db","studies.json")))
meta=json.load(open(J("data","db","metadata.json")))
need=[pm for pm,v in st.items() if v.get("xml") and not v.get("pdf") and db.get(pm,{}).get("eligible")]
print(f"{len(need)} eligible studies hold XML but no PDF")
got=0
for pm in need:
    pmcid=(meta.get(pm) or {}).get("pmcid") or (st[pm].get("pmcid") or "")
    if not pmcid: continue
    # The REST fullTextPDF path 404s for many OA records and NCBI's /pdf/ returns a
    # 1.8 KB stub; the article render endpoint returns the real file.
    urls=[f"https://europepmc.org/articles/{pmcid}?pdf=render",
          f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextPDF"]
    blob=None
    for url in urls:
        for a in range(2):
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120) as r:
                    cand=r.read()
                if cand[:4]==b"%PDF" and len(cand)>15000:
                    blob=cand; break
            except Exception:
                time.sleep(1.0*(a+1))
        if blob: break
    if blob and blob[:4]==b"%PDF" and len(blob)>15000:
        p=os.path.join(FT,f"{pm}.pdf")
        open(p,"wb").write(blob)
        st[pm]["pdf"]=os.path.relpath(p,ROOT); got+=1
    time.sleep(0.3)
json.dump(st,open(J("data","raw","fulltext_status.json"),"w"),indent=1)
elig=[p for p,v in db.items() if v.get("eligible")]
withpdf=[p for p in elig if (st.get(p) or {}).get("pdf")]
print(f"fetched {got}; eligible studies with a PDF: {len(withpdf)}/{len(elig)}")
