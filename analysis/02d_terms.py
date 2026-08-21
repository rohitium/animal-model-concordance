"""Which terms drive the volume? Count each candidate term alone, and in the
animal+human context, to find the leaks before redesigning."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries
ANIM = "(" + queries.B1_ANIMAL.replace("\n"," ") + ")"
TERMS = ['translat*[tiab]','"translational"[tiab]','predict*[tiab]','correlat*[tiab]',
         'replicat*[tiab]','reproducib*[tiab]','concordan*[tiab]','"predictive value"[tiab]',
         '"predictive validity"[tiab]','extrapolat*[tiab]','"species differences"[tiab]',
         '"Drug Evaluation, Preclinical"[Mesh]','"Translational Research, Biomedical"[Mesh]',
         '"Treatment Failure"[Mesh]','"Disease Models, Animal"[Mesh]','"Predictive Value of Tests"[Mesh]']
print(f"{'term':44s} {'alone':>11s} {'AND animal':>12s}")
for t in TERMS:
    a = pubmed.esearch(t)[0]
    b = pubmed.esearch(f"{t} AND {ANIM}")[0]
    print(f"{t:44s} {a:>11,} {b:>12,}")
