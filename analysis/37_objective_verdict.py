"""Deterministic, threshold-based verdict computed from the extracted figures.

Why this replaces the model-judged verdict as primary:

The earlier justification for having no thresholds — that a 63% concordance rate, an R² of
0.09 and a 92% failure rate cannot share a cut-off — was wrong. Direction is trivially
normalisable: a 92% failure rate is an 8% success rate. Once every figure is expressed on a
common "higher means the animal result tracked the human result" scale, a threshold is
straightforward. And the model-judged verdicts agree only moderately between raters
(kappa 0.58), which is precisely the case for a rule that anyone can recompute.

Everything here is explicit and auditable: which statistics count, how each is oriented,
what the cut-offs are, and how sensitive the result is to them.
"""
import json, os, re, collections, sys
ROOT=os.path.join(os.path.dirname(__file__),".."); J=lambda *p: os.path.join(ROOT,*p)

# --- 1. which statistics carry concordance information, and which way they point ---------
# AGREEMENT: higher value = animal result tracked the human result
AGREEMENT = [
 "concordance","agreement","accuracy","ppv","positive predictive value","npv",
 "negative predictive value","sensitivity","specificity","recall","precision","auc",
 "c-score","success rate","translation rate","overlap","same direction","correct",
 "response rate","reproducib","replicat","similarity","congruence","robustness","score",
 "predictive value","true positive","match","mimic","survival concordance",
]
# DISCORDANCE: higher value = animal result FAILED to track the human result. Inverted.
DISCORDANCE = [
 "failure rate","failure","discordan","overestimat","false positive","false negative",
 "attrition","error rate","not replicat","irreproducib","fail","mismatch","divergence",
 "distance",
]
# CORRELATION: |r| or R² already on 0-1 and oriented the right way
CORRELATION = ["correlation","pearson","spearman","r^2","r2","rho","kendall"]
# RATIO-LIKE: agreement is at 1. A ratio of animal to human effect, a fold-difference, or
# a regression slope of human on animal all mean "the same" at 1 and diverge either way.
# Mapped by 1/max(x, 1/x), so 1 -> 1.00, 2 -> 0.50, 10 -> 0.10.
RATIO_LIKE = ["fold","ratio","times","slope of","regression slope","potency ratio"]
# ASSOCIATION: odds ratios and likelihood ratios measure association, 1 = none.
# Mapped by x/(1+x), which is Yule's Q rescaled to 0-1: OR 1 -> 0.50, OR 10 -> 0.91.
ASSOCIATION = ["odds ratio","likelihood ratio","lr+","risk ratio","hazard ratio"]
# BOUNDED DIFFERENCE: a difference between two quantities that are themselves on 0-1
# (e.g. a difference of correlations). 0 = identical, so agreement is 1 - |d|.
BOUNDED_DIFF = ["difference in correlation","correlation difference","mean difference"]

# NOT convertible to a concordance magnitude, and why:
#  - p-values and FDR measure evidence against a null, not how closely two things agree.
#    A tiny p can accompany a trivial or a large divergence.
#  - unbounded distances (Mahalanobis) and slope differences in unstated units are
#    monotone in agreement but have no common scale, so they rank species within a study
#    and cannot be thresholded across studies.
UNUSABLE = [
 "p value","p-value","f-statistic","fdr","q value","significance","count","number of",
 "cost","duration","qualitative","not statistically","dose","concentration","ic50",
 "auc0","exposure","n=","mahalanobis","distance","slope difference",
]

def classify(stat, unit, what=""):
    """Classify on the statistic name AND the description of what was compared.

    Classifying on the name alone left bare labels like "rate", "proportion" and
    "probability" unscored even when the description said plainly what they measured.
    """
    t=((stat or "")+" "+(what or "")).strip().lower()
    for k in UNUSABLE:
        if k in t: return None
    for k in BOUNDED_DIFF:
        if k in t and unit in ("correlation","proportion_0_1"): return "bounded-difference"
    for k in ASSOCIATION:
        if k in t: return "association"
    for k in RATIO_LIKE:
        if k in t: return "ratio-like"
    for k in CORRELATION:
        if k in t: return "correlation"
    for k in DISCORDANCE:
        if k in t: return "discordance"
    for k in AGREEMENT:
        if k in t: return "agreement"
    return None

def to_scale(value, unit, kind):
    """Map onto 0-1 where 1 = perfect animal-to-human correspondence."""
    if value is None: return None
    v=float(value)
    if kind=="ratio-like":
        if v<=0: return 0.0
        return round(1.0/max(v, 1.0/v), 4)
    if kind=="association":
        if v<0: return None
        return round(v/(1.0+v), 4)
    if kind=="bounded-difference":
        d=abs(v)
        if d>1.0: d=d/100.0 if d<=100 else None
        return None if d is None else round(1.0-d, 4)
    if unit=="percent":
        if not (0<=v<=100): return None
        v=v/100.0
    elif unit in ("proportion_0_1","correlation"):
        if v>1.0 and v<=100.0: v=v/100.0     # some are recorded as percentages anyway
        if not (-1.0<=v<=1.0): return None
        if kind=="correlation": v=abs(v)
    else:
        return None
    return 1.0-v if kind=="discordance" else v

# --- 2. thresholds -----------------------------------------------------------------------
# Families that enter the score. Odds ratios, fold-changes and slopes CAN be put on a 0-1
# scale (Yule's Q rescaled; 1/max(x,1/x)) and those conversions are kept below — but folding
# them into one median makes the composite less meaningful, not more. A 0.5 meaning "a
# two-fold difference" is not the same claim as a 0.5 meaning "agreed half the time", and
# mixing them empirically destroys agreement with independent readers: including ratio-like
# figures moves kappa against rater 1 from +0.17 to -0.01, i.e. to chance. They are reported
# per figure on study pages instead, converted and labelled, without entering the score.
# A study's purpose-built concordance metric is the thing to score. Ancillary statistics --
# e.g. the mean gap between within-species and cross-species correlations -- are steps in
# the analysis, not measures of how well the model matched. Including bounded differences
# left kappa unchanged, so they are reported per figure and left out of the score.
SCORED_FAMILIES = {"agreement","discordance","correlation"}
SUPPORTS, PARTLY = 0.70, 0.40      # >=0.70 supports; 0.40-0.70 partly; <0.40 does not
def verdict_from(score):
    if score is None: return "insufficient-data"
    if score>=SUPPORTS: return "supports"
    if score>=PARTLY:   return "partly-supports"
    return "does-not-support"

def main():
    ANS=json.load(open(J("data","db","study_answers.json")))
    DB=json.load(open(J("data","db","studies.json")))
    PROV=json.load(open(J("data","db","figure_provenance.json")))
    OK={k:v for k,v in ANS.items() if "error" not in v and DB.get(k,{}).get("eligible")}
    out={}
    for pm,v in OK.items():
        used=[]
        prov=PROV.get(pm) or {}
        for _i,c in enumerate(v.get("comparisons") or []):
            if ((prov.get(str(_i)) or {}) if "error" not in prov else {}).get(
                    "provenance")=="cited-from-other-study":
                continue
            kind=classify(c.get("statistic"), c.get("unit"), c.get("what_compared"))
            if not kind: continue
            s=to_scale(c.get("value"), c.get("unit"), kind)
            if s is None: continue
            rec={"statistic":c["statistic"],"unit":c["unit"],"raw":c["value"],
                 "kind":kind,"scaled":round(s,4),"in_score":kind in SCORED_FAMILIES,
                 "what":c.get("what_compared"),"source":c.get("source_location")}
            used.append(rec)
        scored=[x for x in used if x["in_score"]]
        if scored:
            vals=sorted(x["scaled"] for x in scored)
            m=len(vals)//2
            median=vals[m] if len(vals)%2 else (vals[m-1]+vals[m])/2
            out[pm]={"n_usable":len(scored),"n_converted_not_scored":len(used)-len(scored),
                     "median":round(median,4),
                     "min":round(vals[0],4),"max":round(vals[-1],4),
                     "verdict":verdict_from(median),"figures":used}
        else:
            out[pm]={"n_usable":0,"n_converted_not_scored":len(used),"median":None,
                     "verdict":"insufficient-data","figures":used}
    json.dump(out, open(J("data","db","objective_verdict.json"),"w"), indent=1)

    # --- 3. how well does the rule match the two model raters? ---------------------------
    R2=json.load(open(J("data","db","second_rater.json")))
    def kappa(pairs):
        n=len(pairs)
        if not n: return 0,0
        po=sum(1 for x,y in pairs if x==y)/n
        a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
        cats={c for p in pairs for c in p}
        pe=sum((a[c]/n)*(b[c]/n) for c in cats)
        return po, (po-pe)/(1-pe) if pe<1 else 0.0
    scored={k:v for k,v in out.items() if v["verdict"]!="insufficient-data"}
    p1=[(scored[k]["verdict"], OK[k]["verdict"]) for k in scored]
    p2=[(scored[k]["verdict"], R2[k]["verdict"]) for k in scored if k in R2 and "error" not in R2[k]]
    pr=[(OK[k]["verdict"], R2[k]["verdict"]) for k in OK if k in R2 and "error" not in R2[k]]
    print(f"studies scored by rule: {len(scored)}/{len(OK)} "
          f"({len(OK)-len(scored)} had no figure on a concordance scale)")
    print(f"usable figures: {sum(v['n_usable'] for v in out.values())}")
    print("\nverdict distributions")
    print("  rule    :", dict(collections.Counter(v["verdict"] for v in out.values())))
    print("  rater 1 :", dict(collections.Counter(OK[k]['verdict'] for k in scored)))
    print("  rater 2 :", dict(collections.Counter(R2[k]['verdict'] for k in scored if k in R2 and 'error' not in R2[k])))
    for name,pp in (("rule vs rater 1",p1),("rule vs rater 2",p2),("rater 1 vs rater 2",pr)):
        a,k=kappa(pp); print(f"  {name:20s} agreement {a:.0%}  kappa {k:.2f}  (n={len(pp)})")

    print("\nsensitivity of the rule to its cut-offs")
    global SUPPORTS, PARTLY
    base=dict(collections.Counter(v["verdict"] for v in scored.values()))
    for hi,lo in ((0.75,0.45),(0.70,0.40),(0.65,0.35),(0.60,0.30)):
        SUPPORTS, PARTLY = hi, lo
        d=collections.Counter(verdict_from(v["median"]) for v in scored.values())
        print(f"  supports>={hi}, partly>={lo}:  {dict(d)}")
    SUPPORTS, PARTLY = 0.70, 0.40

if __name__=="__main__":
    main()
