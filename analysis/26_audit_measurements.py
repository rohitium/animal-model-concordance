"""Audit measurements for invented numbers.

A qualitative claim must not acquire a numeric value. The addiction review says the
incubation phenomenon "was first discovered in laboratory rats and later also
demonstrated to occur in smokers" -- a narrative observation with no statistic. It was
stored as "concordance = 100%". That is a fabricated figure: faithful in spirit,
invented in precision, and indistinguishable on the page from a measured 100%.

Rule: if a measurement carries a value, a matching number must appear in its verbatim."""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MS = json.load(open(J("data","db","measurements.json")))
DB = json.load(open(J("data","db","studies.json")))

WORDS = {"half":50,"a third":33.3,"one-third":33.3,"third":33.3,"a quarter":25,
 "one-quarter":25,"quarter":25,"two-thirds":66.7,"three-quarters":75,"dozen":12,
 "twofold":2,"two-fold":2,"threefold":3,"three-fold":3,"fourfold":4,"four-fold":4,
 "fivefold":5,"five-fold":5,"tenfold":10,"ten-fold":10,"doubled":2,"tripled":3,
 "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,
 "ten":10,"eleven":11,"twelve":12,"none":0,"all":100,"only":None}

def nums(t):
    """Numbers written as words are still stated by the source. Counting them as
    unsupported would flag 'a fivefold increase' -> 5 as fabrication."""
    out = set()
    t = t or ""
    for m in re.findall(r"\d+(?:[.,]\d+)?", t):
        try: out.add(float(m.replace(",", "")))
        except ValueError: pass
    low = t.lower()
    for w, v in WORDS.items():
        if v is not None and re.search(r"\b" + re.escape(w) + r"\b", low):
            out.add(float(v)); out.add(float(v)/100)
    return out

def supported(x):
    v = x.get("value")
    if v is None: return True
    ns = nums(x.get("verbatim",""))
    if not ns: return False
    cands = {v}
    if isinstance(v,(int,float)):
        cands |= {v*100, v/100, round(v), round(v,1), round(v,2)}
    return any(any(abs(c-n) < max(0.01, abs(c)*0.02) for n in ns) for c in cands)

bad, total = [], 0
for pm, m in MS.items():
    if "error" in m: continue
    for i, x in enumerate(m.get("measurements") or []):
        if x.get("value") is None: continue
        total += 1
        if not supported(x):
            bad.append({"pmid": pm, "index": i, "statistic": x["statistic"],
                        "value": x["value"], "unit": x["unit"],
                        "verbatim": (x.get("verbatim") or "")[:150],
                        "title": DB.get(pm,{}).get("title","")[:55]})
json.dump(bad, open(J("data","db","measurement_audit.json"),"w"), indent=1)
print(f"measurements with a value : {total}")
print(f"value NOT found in verbatim: {len(bad)}  ({len(bad)/max(1,total):.1%})")
for b in bad[:18]:
    print(f"\n  {b['pmid']} {b['statistic']} = {b['value']} {b['unit']}  | {b['title']}")
    print(f"     verbatim: {b['verbatim']}")
sys.exit(0)
