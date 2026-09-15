"""Sampling frame 4 (PLAN.md v0.4 §7.2): a systematic PubMed search for intervention studies in
client-owned dogs and cats with naturally occurring disease.

The query is fixed here and its exact string, date and hit count are written to the output and to
protocol/search_strings.md. Output: data/v04/frames/pubmed_companion.json
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
import pubmed  # analysis/pubmed.py, cached E-utilities

QUERY = (
    '("client-owned"[tiab] OR "client owned"[tiab] OR "privately owned"[tiab] OR "owned dogs"[tiab] '
    'OR "owned cats"[tiab] OR "pet dogs"[tiab] OR "pet cats"[tiab] OR "naturally occurring"[tiab] '
    'OR spontaneous[tiab] OR spontaneously[tiab]) '
    'AND ("Dogs"[Mesh] OR "Cats"[Mesh] OR canine[tiab] OR feline[tiab] OR dog[tiab] OR dogs[tiab] '
    'OR cat[tiab] OR cats[tiab]) '
    'AND ("Clinical Trial, Veterinary"[pt] OR "Randomized Controlled Trial, Veterinary"[pt] '
    'OR "clinical trial"[tiab] OR randomized[tiab] OR randomised[tiab] OR "phase I"[tiab] '
    'OR "phase II"[tiab] OR "single-arm"[tiab] OR "dose-escalation"[tiab] OR prospective[tiab])'
)

def main():
    count, ids, trans = pubmed.esearch(QUERY, retmax=9999, sort="pub_date")
    save({"query": QUERY, "query_translation": trans, "run_date": today(), "count": count,
          "n_ids": len(ids), "pmids": ids}, "frames/pubmed_companion.json")
    print(f"PubMed companion-animal frame: {count} records, {len(ids)} ids retrieved")
    if count > len(ids):
        print("WARNING: more records than one esearch page; frame is truncated and must be paged")

if __name__ == "__main__":
    main()
