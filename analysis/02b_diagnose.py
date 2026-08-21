import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries
BLOCKS = {k: getattr(queries, k) for k in dir(queries) if k.startswith("B") and k[1].isdigit()}
MISSED = ["17032985","18772421","20361020","19297654","21097827","20361022","22460880",
          "21892149","25670378","24406927","29394327","25024750","23401516","24678540"]
summ = pubmed.esummary(MISSED)
print(f"{'pmid':10s} {'blocks NOT matched':34s} {'abs':4s} title")
for p in MISSED:
    fails = [bk for bk, bq in BLOCKS.items()
             if not pubmed.esearch(f"({bq.replace(chr(10),' ')}) AND {p}[uid]")[0]]
    n_abs = pubmed.esearch(f"{p}[uid] AND hasabstract")[0]
    print(f"{p:10s} {','.join(sorted(fails)) or '-':34s} {'y' if n_abs else 'NO':4s} {summ.get(p,{}).get('title','')[:68]}")
