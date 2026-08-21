import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pubmed
Q = [
 ("hackam2006",'Hackam DG[au] AND JAMA[ta] AND 2006[dp]'),
 ("contopoulos2008",'"Life cycle of translational research"[ti] OR (Contopoulos-Ioannidis DG[au] AND Science[ta])'),
 ("bailey_nhp",'Bailey J[au] AND (ATLA[ta] OR "Altern Lab Anim"[ta]) AND (toxicolog*[tiab] OR drug safety[tiab] OR predict*[tiab])'),
 ("redfern2003",'Redfern WS[au] AND torsade*[tiab] AND (Cardiovasc Res[ta] OR 2003[dp])'),
 ("cummings2014",'Cummings JL[au] AND "Alzheimers Res Ther"[ta] AND pipeline[tiab]'),
 ("saint1_lees2006",'Lees KR[au] AND NXY-059[tiab] AND "N Engl J Med"[ta]'),
 ("saint2_shuaib2007",'Shuaib A[au] AND NXY-059[tiab] AND "N Engl J Med"[ta]'),
 ("paoloni_khanna2008",'Paoloni M[au] AND Khanna C[au] AND "Nat Rev Cancer"[ta]'),
 ("recist_vet_nguyen",'(Nguyen SM[au] OR Vail DM[au]) AND RECIST[tiab] AND (dog*[tiab] OR canine[tiab])'),
 ("vcog_ctcae_v2",'"Veterinary Cooperative Oncology Group"[tiab] AND "Common Terminology Criteria"[tiab]'),
 ("khanna_osa",'Khanna C[au] AND osteosarcoma[tiab] AND (comparative[tiab] OR canine[tiab]) AND review[pt]'),
 ("mak2014",'Mak IW[au] AND 2014[dp] AND animal[tiab]'),
 ("ioannidis2005",'Ioannidis JP[au] AND 2005[dp] AND "Why most published research findings are false"[ti]'),
 ("garner2017",'(Garner JP[au] OR Voelkl B[au]) AND (reproducibility[tiab] OR external validity[tiab]) AND animal[tiab]'),
 ("arrive2020",'ARRIVE guidelines 2.0[tiab] AND 2020[dp]'),
 ("syrcle_rob",'Hooijmans CR[au] AND SYRCLE[tiab] AND risk of bias[tiab]'),
 ("ferret_flu",'ferret*[tiab] AND influenza[tiab] AND transmission[tiab] AND (model[tiab] AND (predict*[tiab] OR human[tiab])) AND review[pt]'),
 ("rpe65_dog",'RPE65[tiab] AND (dog*[tiab] OR canine[tiab] OR Briard[tiab]) AND gene therapy[tiab]'),
 ("tanezumab_ngf",'(tanezumab[tiab] OR "nerve growth factor"[tiab]) AND osteoarthritis[tiab] AND (canine[tiab] OR dog*[tiab] OR feline[tiab])'),
 ("bovine_rsv",'bovine respiratory syncytial virus[tiab] AND (model[tiab] AND human[tiab])'),
 ("hen_ovarian",'(hen*[tiab] OR chicken[tiab]) AND ovarian cancer[tiab] AND (spontaneous[tiab] OR model[tiab])'),
 ("canine_dm_sod1",'(degenerative myelopathy[tiab] AND SOD1[tiab] AND (dog*[tiab] OR canine[tiab]))'),
]
for key, q in Q:
    n, ids, _ = pubmed.esearch(q, retmax=4)
    s = pubmed.esummary(ids)
    print(f"\n=== {key}  hits={n}")
    for p in ids:
        c = s.get(p, {})
        print(f"  {p}  {c.get('year','')}  {c.get('journal','')}  | {', '.join(c.get('authors',[]))} | {c.get('title','')[:105]}")
