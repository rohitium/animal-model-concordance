"""Export the landing-page table as structured JSON for the Word build.

Reuses the site's own grouping rules so the document and the page cannot drift:
a range spans only figures measuring the same thing, and nothing is averaged."""
import sys, os, json, collections, re
sys.path.insert(0, os.path.dirname(__file__))
import normalize as N
ROOT=os.path.join(os.path.dirname(__file__),".."); J=lambda *p: os.path.join(ROOT,*p)
load=lambda *p: json.load(open(J(*p)))
DB=load("data","db","studies.json"); META=load("data","db","metadata.json")
ANS=load("data","db","study_answers.json"); CLS=load("data","db","classification.json")
SYN=load("data","db","row_synthesis.json")
PROV=load("data","db","figure_provenance.json")
OK={k:v for k,v in ANS.items() if "error" not in v and DB.get(k,{}).get("eligible")}
PDX={k for k,v in DB.items() if k in OK and v.get("substrate")=="human-tissue-in-animal-host"}
CORE={k:v for k,v in OK.items() if k not in PDX}
LABEL={"efficacy":"Efficacy","toxicology":"Toxicology","safety-pharmacology":"Safety pharmacology",
       "disease-biology":"Disease biology","veterinary":"Veterinary"}
ORDER=["efficacy","toxicology","safety-pharmacology","disease-biology","veterinary"]
VLAB={"supports":"supports","partly-supports":"partly supports","does-not-support":"does not support"}

def arm(pm): return (CLS.get(pm) or {}).get("arm") or "unassigned"
def cite(pm):
    v=DB[pm]; md=META.get(pm) or {}
    a=(md.get("authors_full") or v.get("authors") or [])
    nm=(f"{a[0].split()[-1]} et al." if len(a)>1 else (a[0].split()[-1] if a else "Anon.")) if a else "Anon."
    return f"{nm} {v.get('year') or 'n.d.'}"
def orgs_of(pm):
    a=OK[pm]["animal_side"]
    return N.organisms(list(a.get("species") or [])+list(a.get("grouped_labels") or [])) or []
def comps(pm,o):
    """This study's own figures, attributable to this organism.

    Figures quoted from other work are excluded: their conditions belong to the original
    study, and counting them here would double-count. A figure with no species of its own
    is attributed only when the study examines exactly one organism."""
    v=OK[pm]; prov=PROV.get(pm) or {}
    study_orgs=N.organisms(list(v["animal_side"].get("species") or [])
                           + list(v["animal_side"].get("grouped_labels") or []))
    out=[]
    for i,c in enumerate(v.get("comparisons") or []):
        pv=(prov.get(str(i)) or {}) if "error" not in prov else {}
        if pv.get("provenance")=="cited-from-other-study": continue
        cs=N.organisms(c.get("animal_species") or [])
        if cs:
            if o in cs: out.append(c)
        elif len(study_orgs)==1 and study_orgs[0]==o:
            out.append(c)
    return out


_STOP=set("the of a an in and or to for with between from that this is are was were on by vs "
          "versus percentage percent share proportion number rate average mean".split())
def _key(t): return frozenset(w for w in re.findall(r"[a-z]+",(t or "").lower()) if w not in _STOP and len(w)>2)

rows=collections.defaultdict(set)
for pm in CORE:
    for o in orgs_of(pm):
        if comps(pm,o): rows[(arm(pm),o)].add(pm)

out=[]
for a in ORDER+[x for x in {k[0] for k in rows} if x not in ORDER]:
    for o in sorted([oo for aa,oo in rows if aa==a], key=lambda x:(-len(rows[(a,x)]), x)):
        pms=rows[(a,o)]
        buckets=[]
        for pm in sorted(pms, key=lambda p:-(DB[p].get("cited_by") or 0)):
            for c in comps(pm,o):
                if c.get("value") is None: continue
                k=_key(c.get("what_compared")); placed=False
                for b in buckets:
                    if b["stat"]!=c["statistic"].strip().lower() or b["unit"]!=c["unit"]: continue
                    if len(b["key"]&k)/(len(b["key"]|k) or 1) >= 0.6:
                        b["items"].append((pm,c)); b["key"]|=k; placed=True; break
                if not placed:
                    buckets.append({"stat":c["statistic"].strip().lower(),"unit":c["unit"],
                                    "key":set(k),"items":[(pm,c)]})
        ev=[]
        for b in sorted(buckets,key=lambda x:-len(x["items"]))[:6]:
            vals=[c["value"] for _,c in b["items"]]
            rng=f"{min(vals):g}–{max(vals):g}" if len(set(vals))>1 else f"{vals[0]:g}"
            if b["unit"]=="percent": rng+="%"
            _,c0=b["items"][0]
            nc=re.sub(r"^\s*[\d,]+\s*","",(c0.get("n_counts") or "")).strip()
            n=f", n={c0['n']:,} {nc}".rstrip() if c0.get("n") else ""
            studies=sorted({pm for pm,_ in b["items"]}, key=lambda p:-(DB[p].get("cited_by") or 0))
            ev.append({"value":rng,"statistic":b["stat"],"n":n,"what":c0["what_compared"],
                       "cites":[{"text":cite(p),"pmid":p,
                                 "url":f"https://pubmed.ncbi.nlm.nih.gov/{p}/",
                                 "site":f"https://rohitium.github.io/animal-model-concordance/study/{p}.html"}
                                for p in studies]})
        cav=[OK[pm].get("base_rate_caveat") for pm in pms if OK[pm].get("base_rate_caveat")]
        vs=collections.Counter(OK[pm]["verdict"] for pm in pms)
        sy=SYN.get(f"{a}|{o}") or {}
        if "error" in sy: sy={}
        out.append({"assessment":LABEL.get(a,a),"organism":o,"n_studies":len(pms),
                    "summary":sy.get("summary"),"direction":sy.get("direction"),
                    "why_range_is_wide":sy.get("why_range_is_wide"),
                    "negative_controls":sy.get("negative_controls_noted"),
                    "verdicts":[{"label":VLAB.get(k,k),"n":v} for k,v in vs.most_common()],
                    "evidence":ev,"caveat":cav[0] if cav else None})
json.dump(out, open(J("data","db","table_export.json"),"w"), indent=1)
print(f"{len(out)} rows, {sum(len(r['evidence']) for r in out)} evidence items")
