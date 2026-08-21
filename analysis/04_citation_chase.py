"""Citation chasing as an independent recall mechanism.

The query-based search depends on vocabulary the target literature does not use
consistently. The citation network does not. This seeds from verified anchors,
expands one generation in both directions, and reports how much of the anchor set
is recoverable from the network alone -- an overfitting-free recall check."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import pubmed

ANCHORS = {"hackam2006":"17032985","perel2007":"17175568","contopoulos2008":"18772421",
 "vanderworp2010":"20361020","pound2018":"30404629","leenaars2019":"31307492",
 "bracken2009":"19297654","wall2008":"17988725","mak2014":"24489990","howells2010":"20485296",
 "marshall2023":"36883244","sena2010":"20361022","begley2012":"22460880","prinz2011":"21892149",
 "freedman2015":"25670378","olson2000":"11029269","monticello2017":"28893587",
 "clark2018":"29730448","bailey2015":"26753942","redfern2003":"12667944","hay2014":"24406927",
 "wong2019":"29394327","cummings2014":"25024750","seok2013":"23401516","takao2015":"25092317",
 "perrin2014":"24678540","paoloni_khanna2008":"18202698","kol2015":"26446953",
 "fan_khanna2015":"29061942"}
pm = list(ANCHORS.values())

# Leave-one-out: can each anchor be reached from the OTHERS via citation links?
fwd = pubmed.elink(pm, "pubmed_pubmed_citedin")
bwd = pubmed.elink(pm, "pubmed_pubmed_refs")
print(f"forward links resolved for {len(fwd)}/{len(pm)} seeds; backward for {len(bwd)}/{len(pm)}")

reach = collections.defaultdict(set)
for src in pm:
    for tgt in fwd.get(src, []) + bwd.get(src, []):
        reach[tgt].add(src)

rec = []
for k, p in ANCHORS.items():
    others = reach.get(p, set()) - {p}
    rec.append((k, p, len(others)))
found = [r for r in rec if r[2] > 0]
print(f"\nLeave-one-out citation recall: {len(found)}/{len(rec)} = {len(found)/len(rec):.1%}")
for k, p, n in sorted(rec, key=lambda x: -x[2]):
    print(f"  {'OK ' if n else 'MISS'} {k:22s} reachable from {n} other anchor(s)")

# Candidate pool the network generates
pool = set()
for src in pm:
    pool.update(fwd.get(src, [])); pool.update(bwd.get(src, []))
pool -= set(pm)
print(f"\nOne-generation citation neighbourhood: {len(pool):,} unique records")
cnt = collections.Counter()
for src in pm:
    for t in fwd.get(src, []) + bwd.get(src, []): cnt[t] += 1
multi = [p for p, c in cnt.items() if c >= 3 and p not in pm]
print(f"Records linked to >=3 anchors (high-priority screening): {len(multi):,}")
json.dump({"leave_one_out_recall": len(found)/len(rec), "pool_size": len(pool),
           "multi_linked": sorted(multi, key=lambda x: -cnt[x])[:500]},
          open(os.path.join(os.path.dirname(__file__),"..","data","raw","citation_chase.json"),"w"), indent=1)
