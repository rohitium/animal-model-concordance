# Part 2 drug pairs (draft)

Built 2026-09-14 by `analysis/v04/d2_human_evidence.py` (judge anthropic/claude-sonnet-5).

- drug × indication groups: 812
- status: {'classified': 803, 'no-human-counterpart': 9}
- judgements with a citation outside the retrieved set: 0

## efficacy · same-molecule: 785 pairs — {'concordant': 188, 'indeterminate': 442, 'mixed': 108, 'discordant': 47}

| drug | vet indication | species | vet | human (level) | pair | sources |
|---|---|---|---|---|---|---|
| ACALABRUTINIB | b-cell non-hodgkin lymphoma | dog | positive | positive (us-approval) | **concordant** | pubmed+exemplar |
| ACETYLCYSTEINE | systemic illness | dog | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ACUPUNCTURE | perioperative analgesia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ALBUTEROL | hyperkalemia | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ALFENTANIL | anaesthesia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ALPRAZOLAM | perioperative anxiolysis and sedation | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| AMINOLEVULINIC | squamous cell carcinoma | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| AMLODIPINE | hypertension | cat, dog-and-cat | positive | positive (us-approval) | **concordant** | exemplar, pubmed+exemplar |
| AMOXICILLIN | pyoderma | dog | positive | positive (us-approval) | **concordant** | pubmed |
| ANTACID | gastroesophageal reflux disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ASCOPHYLLUM NODOSUM | periodontal disease | dog | positive | positive (phase-2) | **concordant** | pubmed |
| ASPARAGINASE | lymphoma | cat, dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed, pubmed+exemplar |
| ATENOLOL | hypertrophic cardiomyopathy | cat | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| AUTOLOGOUS PLATELET RICH FIBRIN | periodontal disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| BETAMETHASONE | otitis externa | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| BEXAGLIFLOZIN | diabetes mellitus | cat | positive | positive (us-approval) | **concordant** | pubmed |
| BEZAFIBRATE | hyperlipidemia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| BONE GRAFT | periodontal disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| BUDESONIDE | inflammatory bowel disease | dog | positive | positive (us-approval) | **concordant** | pubmed |
| BUMETANIDE | congestive heart failure | dog | positive | positive (us-approval) | **concordant** | pubmed |
| BUPIVACAINE | long bone fracture | dog | positive | positive (us-approval) | **concordant** | pubmed |
| BUPRENORPHINE | postoperative hyperthermia | cat | negative | negative (earlier) | **concordant** | pubmed |
| CALCIUM SULFATE | surgical site infection of bone and joint | dog-and-cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CANNABIDIOL | epilepsy | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CARBIMAZOLE | hyperthyroidism | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, pubmed |
| CARBONATE | osteoarthritis | dog | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CARBOPLATIN | urothelial carcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CEFADROXIL | pyoderma | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CELECOXIB | back pain | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CELLULOSE | acute diarrhea | dog | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CHOP | lymphoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar |
| CLARITHROMYCIN | leproid granuloma syndrome | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CLAVULANIC | pyoderma | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CLINDAMYCIN | pyoderma | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CLOMIPRAMINE | compulsive disorder | dog | positive | positive (us-approval) | **concordant** | pubmed |
| COPPER | hepatic copper accumulation | dog | positive | positive (phase-2) | **concordant** | pubmed |
| CORN | hypoglycemia | dog | positive | positive (earlier) | **concordant** | pubmed |
| CYANOCOBALAMIN | gastrointestinal disease with cobalamin deficiency | cat | positive | positive (us-approval) | **concordant** | pubmed |
| CYANOCOBALAMIN | cobalamin malabsorption syndrome | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CYANOCOBALAMIN | chronic enteropathy | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CYANOCOBALAMIN | chronic gastrointestinal disease or exocrine pancr | cat | positive | positive (us-approval) | **concordant** | pubmed |
| CYCLOPHOSPHAMIDE | lymphoma | cat, dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed, pubmed+exemplar |
| CYCLOSPORINE | hypersensitivity dermatitis | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CYCLOSPORINE | atopic dermatitis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, exemplar, pubmed+exemplar |
| CYCLOSPORINE | immune-mediated polyarthritis | dog | positive | positive (us-approval) | **concordant** | pubmed |
| CYCLOSPORINE | allergic skin disease | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| CYCLOSPORINE | chronic hepatitis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| DEXAMETHASONE | hypersensitivity dermatitis | cat | positive | positive (us-approval) | **concordant** | pubmed |
| DEXMEDETOMIDINE | radiography | dog | positive | positive (us-approval) | **concordant** | pubmed |
| DEXMEDETOMIDINE | anaesthesia | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| DEXMEDETOMIDINE | intervertebral disc disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| DEXTRAN 70 | septic shock | dog | positive | positive (phase-2) | **concordant** | pubmed |
| DEXTROSE SOLUTION | hypoglycemia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| DIAZEPAM | anaesthesia | cat | positive | positive (us-approval) | **concordant** | pubmed |
| DIGOXIN | atrial fibrillation | dog | positive | positive (us-approval) | **concordant** | pubmed |
| DILTIAZEM | atrial fibrillation | dog | positive | positive (us-approval) | **concordant** | pubmed |
| DOPAMINE | hypotension | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| DORZOLAMIDE | ocular hypertension | dog | positive | positive (us-approval) | **concordant** | pubmed |
| DOXORUBICIN | lymphoma | cat, dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed, pubmed+exemplar |
| DRUG ELUTING BEAD TRANSARTERIAL CHEMOEMBOLIZATION | hepatocellular carcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| EMLA CREAM | perioperative analgesia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| EMODEPSIDE | intestinal and lung parasitic infection | cat | positive | positive (phase-2) | **concordant** | pubmed |
| ENALAPRIL | glomerulonephritis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ENTEROCOCCUS FAECIUM | diarrhea | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| EPHEDRINE | hypotension under anesthesia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| EPINEPHRINE | cardiopulmonary arrest | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ETODOLAC | osteoarthritis | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FENOFIBRATE | hyperlipidemia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FENTANYL | postoperative pain | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| FENTANYL | perioperative analgesia | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| FENTANYL | anaesthesia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FLUCONAZOLE | coccidioidomycosis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| FLUOXETINE | compulsive disorder | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FLURBIPROFEN | postoperative ocular inflammation | dog | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| FLUTICASONE | asthma | cat | positive | positive (us-approval) | **concordant** | pubmed |
| FLUTICASONE | inflammatory airway disease | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FOSPHENYTOIN | status epilepticus | dog | positive | positive (us-approval) | **concordant** | pubmed |
| FUROSEMIDE | congestive heart failure | dog, dog-and-cat | positive | positive (us-approval) | **concordant** | pubmed |
| GABAPENTIN | osteoarthritis | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar |
| GLARGINE INSULIN | diabetes mellitus | cat, dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| GLUCOCORTICOIDS | atopic dermatitis | dog | positive | positive (earlier) | **concordant** | exemplar |
| GREEN TEA EXTRACT | osteoarthritis | dog | positive | positive (phase-2) | **concordant** | pubmed |
| HOLMIUM | urolithiasis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| HYDROCORTISONE | atopic dermatitis | dog | positive | positive (us-approval) | **concordant** | exemplar, pubmed |
| HYDROCORTISONE | otitis externa | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| HYDROMORPHONE | pain | dog | positive | positive (us-approval) | **concordant** | pubmed |
| HYDROXOCOBALAMIN | selective intestinal cobalamin malabsorption | dog | positive | positive (us-approval) | **concordant** | pubmed |
| HYDROXOCOBALAMIN | cobalamin deficiency and gastrointestinal disease | cat | positive | positive (us-approval) | **concordant** | pubmed |
| HYDROXYETHYLSTARCH | hemorrhagic shock | dog | positive | positive (earlier) | **concordant** | pubmed |
| HYMENOPTERA VENOM | anaphylaxis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| I 131 | hyperthyroidism | cat | positive | positive (us-approval) | **concordant** | pubmed |
| IBRUTINIB | b-cell non-hodgkin lymphoma | dog | positive | positive (us-approval) | **concordant** | exemplar |
| INSULIN ASPART | diabetic ketoacidosis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| INSULIN DEGLUDEC | diabetes mellitus | dog | positive | positive (us-approval) | **concordant** | pubmed |
| INSULIN DETEMIR | diabetes mellitus | dog | positive | positive (us-approval) | **concordant** | pubmed |
| INSULIN GLARGINE | diabetes mellitus | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| INTERLEUKIN 2 | melanoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| IODINE | hyperthyroidism | cat | positive | positive (us-approval) | **concordant** | pubmed |
| IVERMECTIN | demodicosis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| KETOPROFEN | perioperative analgesia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| KETOPROFEN | acute musculoskeletal pain | cat | positive | positive (us-approval) | **concordant** | pubmed |
| LEVETIRACETAM | status epilepticus | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| LEVETIRACETAM | seizures | dog | positive | positive (us-approval) | **concordant** | pubmed |
| LEVOTHYROXINE | hypothyroidism | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| LIDOCAINE | dysuria | dog | negative | negative (phase-3-or-meta-analysis) | **concordant** | pubmed |
| LIDOCAINE | intervertebral disc disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| LIPIODOL | chylothorax | dog | positive | positive (earlier) | **concordant** | pubmed |
| LOCAL ANAESTHETIC | anaesthesia | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| LOMUSTINE | lymphoma | cat, dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed, pubmed+exemplar |
| LOMUSTINE | central nervous system lymphoma | cat | positive | positive (us-approval) | **concordant** | pubmed |
| MANNITOL | intracranial hypertension | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MASITINIB | mast cell tumour | dog | positive | positive (phase-2) | **concordant** | exemplar, pubmed+exemplar |
| MEDIUM CHAIN TRIGLYCERIDES | epilepsy | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MEGLUMINE | leishmaniosis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MELOXICAM | perioperative analgesia | cat, dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, pubmed |
| MELPHALAN | multiple myeloma | dog | positive | positive (us-approval) | **concordant** | pubmed |
| METAMIZOLE | cancer pain | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| METHADONE | postoperative analgesia | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| METHADONE | perioperative analgesia | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| METHADONE | thoracolumbar disc disease | dog | positive | positive (us-approval) | **concordant** | pubmed |
| METHIMAZOLE | hyperthyroidism | cat | positive | positive (us-approval) | **concordant** | exemplar, pubmed |
| METHOTREXATE | lymphoma | cat | positive | positive (us-approval) | **concordant** | pubmed |
| METHYLENE BLUE | methemoglobinemia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| METHYLPREDNISOLONE | allergic pruritus | cat | positive | positive (us-approval) | **concordant** | pubmed |
| METRONIDAZOLE | giardiasis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MICONAZOLE | otitis externa | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MIDAZOLAM | status epilepticus | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MILRINONE | heart failure | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MIRTAZAPINE | chronic kidney disease | cat | positive | positive (earlier) | **concordant** | pubmed |
| MORPHINE | orthopedic surgery | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MORPHINE | postoperative pain | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MORPHINE | intervertebral disc extrusion | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MORPHINE | postoperative hyperthermia | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| MOXIDECTIN | filarial infections | dog | positive | positive (us-approval) | **concordant** | pubmed |
| MYCOPHENOLATE | atopic dermatitis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| NALBUPHINE | perioperative analgesia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| NERVE GROWTH FACTOR | osteoarthritis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar |
| NOREPINEPHRINE | hypotension | dog | positive | positive (us-approval) | **concordant** | pubmed |
| NPH INSULIN | diabetes mellitus | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| OZONE | bacterial colonization | dog | positive | positive (earlier) | **concordant** | pubmed |
| PHENOBARBITAL | epilepsy | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| PLATELET CONCENTRATE | osteoarthritis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| POLYUNSATURATED FATTY ACIDS | atopic dermatitis | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| POSACONAZOLE | aspergillosis | dog | positive | positive (us-approval) | **concordant** | pubmed |
| POTASSIUM BROMIDE | epilepsy | cat | positive | positive (earlier) | **concordant** | pubmed |
| PRAZIQUANTEL | intestinal parasitic infection | cat | positive | positive (us-approval) | **concordant** | pubmed |
| PREDNISOLONE | lymphoma | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| PREDNISOLONE | asthma | cat | positive | positive (us-approval) | **concordant** | pubmed |
| PREDNISOLONE | atopic dermatitis | dog | positive | positive (us-approval) | **concordant** | exemplar, pubmed+exemplar |
| PREGABALIN | epilepsy | dog | positive | positive (us-approval) | **concordant** | pubmed |
| PROPOFOL | anaesthesia | dog | positive | positive (us-approval) | **concordant** | pubmed |
| PROPOFOL | neurological diagnostic procedures | dog | positive | positive (us-approval) | **concordant** | pubmed |
| PROPOFOL | intracranial disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| PROPOFOL | perioperative complications | dog | positive | positive (us-approval) | **concordant** | pubmed |
| PROPOFOL | radiotherapy support | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| PROTAMINE | diabetes mellitus | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| PSYLLIUM | constipation | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RADIATION | oral carcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RADIATION THERAPY | urothelial carcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RADIOTHERAPY | brain tumor | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RADIOTHERAPY | lymphoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar |
| REGULAR INSULIN | diabetic ketoacidosis | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| REMDESIVIR | feline infectious peritonitis | cat | positive | positive (us-approval) | **concordant** | pubmed |
| RIFAMPICIN | leproid granuloma syndrome | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RIFAXIMIN | chronic enteropathy | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| RIVAROXABAN | thromboembolic disease | cat, dog | positive | positive (us-approval) | **concordant** | pubmed |
| ROPIVACAINE | cranial cruciate ligament rupture | dog | positive | positive (us-approval) | **concordant** | pubmed |
| ROPIVACAINE | intervertebral disc extrusion | dog | positive | positive (us-approval) | **concordant** | pubmed |
| SACUBITRIL | myxomatous mitral valve disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| SORAFENIB | hepatocellular carcinoma | dog | positive | positive (us-approval) | **concordant** | exemplar, pubmed |
| SPIRONOLACTONE | heart failure due to valvular disease | dog | positive | positive (us-approval) | **concordant** | pubmed |
| SUBLINGUAL IMMUNOTHERAPY | atopic dermatitis | cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| SULFAMETHOXAZOLE | bacterial cystitis | dog | positive | positive (us-approval) | **concordant** | pubmed |
| TACROLIMUS | dry eye disease | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| TAURINE | dilated cardiomyopathy | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| TELMISARTAN | hypertension | cat | positive | positive (us-approval) | **concordant** | pubmed |
| TELMISARTAN | proteinuria | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| TORSEMIDE | heart failure due to mitral valve disease | dog | positive | positive (us-approval) | **concordant** | pubmed |
| TRAMADOL | osteoarthritis | cat, dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| TRAMADOL | cancer pain | dog | positive | positive (us-approval) | **concordant** | pubmed |
| TRIAMCINOLONE | allergic dermatitis | cat | positive | positive (phase-2) | **concordant** | pubmed |
| TRIAMCINOLONE ACETONIDE | atopic dermatitis | dog | positive | positive (us-approval) | **concordant** | exemplar |
| TRIMETHOPRIM | pyoderma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| TURMERIC | osteoarthritis | cat, dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| VINBLASTINE | urothelial carcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| VINCRISTINE | lymphoma | cat, dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed |
| VINCRISTINE | transmissible venereal tumour | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | pubmed |
| ZONISAMIDE | epilepsy | dog | positive | positive (us-approval) | **concordant** | pubmed |
| ACETAMINOPHEN | perioperative analgesia | dog | negative | positive (us-approval) | **discordant** | pubmed |
| ANTIOXIDANTS | hyperthyroidism | cat | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| AUTOLOGOUS MICRO FRAGMENTED ADIPOSE TISSUE | osteoarthritis | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| AUTOLOGOUS SERUM | corneal epithelial defect | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| AZACITIDINE | urothelial carcinoma | dog | positive | negative (phase-2) | **discordant** | pubmed |
| BENAZEPRIL | heart disease | cat | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| BROMELAIN | perioperative analgesia | cat | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| BUPIVACAINE | cranial cruciate ligament rupture | dog | negative | positive (us-approval) | **discordant** | pubmed |
| COENZYME Q10 | mitral valve disease | dog | negative | positive (earlier) | **discordant** | pubmed |
| CRANBERRY | chronic kidney disease | cat | positive | negative (earlier) | **discordant** | pubmed |
| CRANBERRY | idiopathic cystitis | cat | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| CYCLOSPORINE | immune-mediated hemolytic anemia | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| DEHYDROEPIANDROSTERONE | obesity | dog | positive | negative (earlier) | **discordant** | pubmed |
| DEHYDROEPIANDROSTERONE DHEA | obesity | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| DEXMEDETOMIDINE | orthopaedic surgery | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| DIMENHYDRINATE | emesis and nausea | dog | negative | positive (us-approval) | **discordant** | pubmed |
| DOXORUBICIN | osteosarcoma | dog | negative | positive (us-approval) | **discordant** | exemplar, pubmed, pubmed+exemplar |
| DOXYCYCLINE | periodontal disease | cat, dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| ENALAPRIL | mitral valve disease | dog | negative | positive (phase-2) | **discordant** | pubmed |
| EPINEPHRINE | perioperative analgesia | dog | negative | positive (us-approval) | **discordant** | pubmed |
| ESSENTIAL OILS | atopic dermatitis | dog | positive | negative (earlier) | **discordant** | pubmed |
| EXENATIDE | diabetes mellitus | cat | negative | positive (us-approval) | **discordant** | pubmed |
| EXENATIDE | obesity | cat | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| FAMCICLOVIR | upper respiratory tract infection | cat | negative | positive (us-approval) | **discordant** | pubmed |
| FECAL MICROBIOTA TRANSPLANTATION | chronic enteropathy | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| FENTANYL | intervertebral disc disease | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| FISH OIL | gingivitis | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| FLUORIDE | gingivitis | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| GABAPENTIN | neuropathic pain | dog | negative | positive (us-approval) | **discordant** | pubmed |
| GRANULOCYTE MACROPHAGE COLONY STIMULATING FACTOR | melanoma | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| LAPATINIB | urothelial carcinoma | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| LEVETIRACETAM | epilepsy | dog | negative | positive (us-approval) | **discordant** | pubmed |
| LORAZEPAM | urethral obstruction | cat | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| LOSARTAN | glioma | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| METFORMIN | diabetes mellitus | cat | negative | positive (us-approval) | **discordant** | pubmed |
| METOCLOPRAMIDE | gastroesophageal reflux disease | dog | negative | positive (us-approval) | **discordant** | pubmed |
| MORPHINE | cataract surgery | dog | negative | positive (us-approval) | **discordant** | pubmed |
| NON STEROIDAL ANTI INFLAMMATORY DRUG | osteoarthritis | dog | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| OLOPATADINE | allergic conjunctivitis | dog | negative | positive (us-approval) | **discordant** | pubmed |
| ONDANSETRON | postoperative nausea | dog | negative | positive (us-approval) | **discordant** | pubmed |
| RAMIPRIL | congestive heart failure due to mitral valve disea | dog | negative | positive (us-approval) | **discordant** | pubmed |
| RHUBARB | chronic kidney disease | cat | negative | positive (phase-3-or-meta-analysis) | **discordant** | pubmed |
| SIROLIMUS | osteosarcoma | dog | negative | positive (phase-2) | **discordant** | exemplar, pubmed+exemplar |
| SPIRONOLACTONE | congestive heart failure | dog | negative | positive (us-approval) | **discordant** | pubmed |
| THALIDOMIDE | mammary carcinoma | dog | positive | negative (phase-2) | **discordant** | exemplar |
| XYLOMETAZOLINE | brachycephalic obstructive airway syndrome | dog | positive | negative (phase-3-or-meta-analysis) | **discordant** | pubmed |
| ZINC | copper storage disease | dog | negative | positive (earlier) | **discordant** | pubmed |
| 153SM DOTMP | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| 2 OCTYL CYANOACRYLATE | cranial cruciate ligament rupture | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| 4 AMINOPYRIDINE | spinal cord injury | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| 6 HYDROXYETHYL STARCH 130 0 4 | hemoperitoneum | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ACE INHIBITOR | hyperthyroidism | cat | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| ACETATE | dehydration | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ACETYLCYSTEINE | intervertebral disc disease | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| ACUPUNCTURE | thoracolumbar muscular pain | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ADRENALINE | brachycephalic obstructive airway syndrome | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ADRENOCORTICOTROPHIC HORMONE | babesiosis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ADXS31 164 | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ALCOHOL | malassezia dermatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ALLERGEN EXTRACT | atopic dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ALLOPURINOL | leishmaniosis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ALMONERTINIB PLUS MICROWAVE ABLATION | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| AMANTADINE | osteoarthritis | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| AMIKACIN | wound infection | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| AMINOCAPROIC | cardiac masses with pericardial effusion | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| AMINOCAPROIC | thrombocytopenia | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| AMINOCAPROIC | hemoperitoneum | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| AMIODARONE | atrial fibrillation | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| AMITRIPTYLINE | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| AMLODIPINE | hyperthyroidism | cat | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| AMMONIA | portosystemic shunt | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| AMOXICILLIN | acute diarrhea | dog | negative | indeterminate (earlier) | **indeterminate** | pubmed |
| AMOXICILLIN | struvite urolithiasis | dog | positive | indeterminate (us-approval) | **indeterminate** | pubmed |
| AMPICILLIN | post-surgical infection | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| ANGIOTENSIN CONVERTING ENZYME INHIBITOR | chronic kidney disease with proteinuria | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ANGIOTENSIN RECEPTOR BLOCKER | chronic kidney disease proteinuric | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ANTACID | brachycephalic obstructive airway syndrome | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ANTIBIOTIC TREATMENT | acute hemorrhagic diarrhea syndrome | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| ANTIBIOTICS | pneumonia | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ANTIHISTAMINES | mastocytosis | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| APOMORPHINE | foreign body ingestion | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ARGININE | obesity | dog-and-cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ARTESUNATE | leishmaniasis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ASCOPHYLLUM NODOSUM | oral health | dog | indeterminate | positive (earlier) | **indeterminate** | pubmed |
| ASPIRIN | immune mediated haemolytic anaemia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ATENOLOL | hyperthyroidism | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| ATIPAMEZOLE | procedural sedation and analgesia | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| ATORVASTATIN | congestive heart failure due to mitral valve disea | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| AURANOFIN | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed+exemplar |
| AUTOLOGOUS BONE MARROW ASPIRATE CONCENTRATE | cranial cruciate ligament tear | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| AUTOLOGOUS MESENCHYMAL STEM CELLS | chronic kidney disease | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| AUTOLOGOUS PLATELET RICH PLASMA | corneal epithelial defect | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| AUTOLOGOUS PLATELET RICH PLASMA PRP | osteoarthritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| AZITHROMYCIN | papillomatosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| BAICALIN | atopic dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| BENAZEPRIL | congestive heart failure | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| BENAZEPRIL | cardiac arrhythmia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BETA LACTAM | subclinical bacteriuria | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| BICARBONATE | gastroesophageal reflux disease | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| BLEOMYCIN | urothelial carcinoma | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| BLEOMYCIN | soft tissue sarcoma | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BRILLIANT BLUE G | spinal cord injury | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| BUPIVACAINE | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| BUPRENORPHINE | urethral obstruction | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| BUPRENORPHINE | cranial cruciate ligament rupture | dog | positive | indeterminate (us-approval) | **indeterminate** | pubmed |
| BUPRENORPHINE | oral disease | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| BUPRENORPHINE | squamous cell carcinoma | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BUTORPHANOL | hyperthyroidism | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BUTORPHANOL | atopic dermatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BUTORPHANOL | liver disease | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BUTORPHANOL | chronic kidney disease | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| BUTYL | chylothorax | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CABERGOLINE | anestrus | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CABERGOLINE | hypersomatotropism and diabetes mellitus | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CALCIFEDIOL | chronic kidney disease | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CALCITRIOL | diabetes mellitus | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CANNABIDIOL | mobility impairment | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CANNABIDIOL | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed+exemplar |
| CAR T CELLS | diffuse large b cell lymphoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CARBON DIOXIDE | brachycephalic obstructive airway syndrome | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CARBOPLATIN | osteosarcoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | exemplar, pubmed, pubmed+exemplar |
| CARBOPLATIN | injection-site sarcoma | cat | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CARPROFEN | osteoarthritis | dog | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| CARPROFEN | orthopedic disorders | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CARPROFEN | mammary carcinoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| CARVEDILOL | chronic valvular heart disease | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CARVEDILOL | hypertrophic cardiomyopathy | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| CEFAZOLIN | perioperative analgesia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CEFOXITIN | parvoviral enteritis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CEFPODOXIME | surgical site infection | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| CELECOXIB | intervertebral disc disease | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CHICKEN | food allergy in dogs | dog | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| CHLORAMBUCIL | urothelial carcinoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CHLORAMBUCIL | glioma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CHLORAMPHENICOL | urinary tract infection | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CHLORHEXIDINE | periodontal disease | cat | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| CHLORHEXIDINE DIGLUCONATE | pyoderma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CHONDROITIN | inflammatory bowel disease | dog | negative | indeterminate (earlier) | **indeterminate** | pubmed |
| CIMICOXIB | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CIMICOXIB | perioperative analgesia | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CISAPRIDE | brachycephalic obstructive airway syndrome | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CISPLATIN | urothelial carcinoma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| CISPLATIN | osteosarcoma | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed, pubmed+exemplar |
| CISPLATIN | soft tissue sarcoma | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CLARITHROMYCIN | leprosy | cat | indeterminate | mixed (earlier) | **indeterminate** | pubmed |
| CLAVULANATE | periodontal disease | cat | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CLAVULANIC | acute diarrhea | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| CLAVULANIC | struvite urolithiasis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CLEVIDIPINE | prostate carcinoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CLOFAZIMINE | leproid granuloma syndrome | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| CLOPIDOGREL | immune-mediated hemolytic anemia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CLOPIDOGREL | thromboembolism | cat | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| COBALAMIN | hypocobalaminemia due to chronic enteropathy or ex | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| COR388 | periodontal disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CORN | osteoarthritis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CORTICOSTEROIDS | mastocytosis cutaneous | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| CORTICOSTEROIDS | lymphoma central nervous system | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| COSYNTROPIN | hyperadrenocorticism | dog | indeterminate | indeterminate (us-approval) | **indeterminate** | pubmed |
| COSYNTROPIN | hypoadrenocorticism | dog | indeterminate | indeterminate (earlier) | **indeterminate** | pubmed |
| CRANBERRY | intervertebral disc disease | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| CRIZOTINIB | b-cell lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| CYCLOPHOSPHAMIDE | haemangiosarcoma | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| CYCLOSPORINE | chronic ulcerative stomatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| CYCLOSPORINE | chronic pancreatitis | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DAPAGLIFLOZIN | heart disease | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| DENDRITIC CELL THERAPY | hemangiosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DESLORELIN | estrus induction | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DESOXYCORTICOSTERONE PIVALATE | hypoadrenocorticism | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | dental disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | atopic dermatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | cranial cruciate ligament rupture | dog | mixed | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | gastroesophageal reflux | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | allergy testing | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | hypotension | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DEXMEDETOMIDINE | hypertrophic cardiomyopathy | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DIAZEPAM | status epilepticus | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| DICLOFENAC | diabetes mellitus | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DIPHENHYDRAMINE | mast cell tumor | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DIPHENHYDRAMINE | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed+exemplar |
| DIPHENHYDRAMINE | allergic reaction | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| DOCOSAHEXAENOIC | hypertrophic cardiomyopathy | cat | negative | indeterminate (none) | **indeterminate** | pubmed |
| DOMPERIDONE | leishmaniosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DOXORUBICIN | sarcoma | cat, dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed, pubmed+exemplar |
| DOXORUBICIN | hemangiosarcoma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| DOXORUBICIN | urinary tract tumors | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| DOXORUBICIN | hepatic carcinoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| DOXYCYCLINE | ehrlichiosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| DOXYCYCLINE | leproid granuloma syndrome | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| DOXYCYCLINE | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| DOXYCYCLINE | cranial cruciate ligament rupture | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| DOXYCYCLINE | b-cell lymphoma | dog | indeterminate | positive (earlier) | **indeterminate** | pubmed |
| DRUG PRESCRIPTION PATTERN | atopic dermatitis | dog | positive | indeterminate (none) | **indeterminate** | exemplar |
| DWP16001 | diabetes mellitus | dog | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| ELECTROCHEMOTHERAPY | cutaneous squamous cell carcinoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| EMODEPSIDE | ectoparasite infestation | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| ENALAPRIL | hypertension | dog-and-cat | indeterminate | positive (us-approval) | **indeterminate** | exemplar |
| ENOXAPARIN | cardiomyopathy-associated thromboembolism | cat | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| ENROFLOXACIN | urinary tract infection | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ENTEROCOCCUS FAECIUM | atopic dermatitis | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| EPINEPHRINE | brachycephalic obstructive airway syndrome | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ESSENTIAL OIL | pruritus with dermatological lesions | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ETHYL | head and neck cancer | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ETHYL | superficial bacterial pyoderma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ETOPOSIDE | lymphoma | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ETOPOSIDE | non-hodgkin lymphoma | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| EZN 3042 | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| FAECAL MICROBIOTA TRANSPLANTATION | atopic dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| FAMOTIDINE | postoperative nausea and vomiting | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| FECAL MICROBIAL TRANSPLANT | inflammatory bowel disease | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| FECAL MICROBIOTA TRANSPLANT | parvovirus infection | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| FECAL MICROBIOTA TRANSPLANTATION | acute hemorrhagic diarrhea syndrome | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| FENTANYL | trauma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| FENTANYL | ear surgery | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| FENTANYL | orthopaedic surgery | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| FENTANYL | postoperative nausea and vomiting | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| FENTANYL | spinal pain | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| FISH OIL | arrhythmogenic right ventricular cardiomyopathy | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| FISH OIL | perioperative analgesia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| FLUCONAZOLE | malassezia dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| FLUDROCORTISONE | hyperaldosteronism | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| FLUORINE | mast cell tumor | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| FLUORINE | mast cell tumor metastasis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| FOLATE | urothelial carcinoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| FOSMIDOMYCIN | otitis externa | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| FUROSEMIDE | hypertension and cardiomyopathy | cat | indeterminate | positive (us-approval) | **indeterminate** | exemplar |
| GABAPENTIN | epilepsy | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| GABAPENTIN | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| GABAPENTIN | chronic kidney disease | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| GADOXETATE | splenic lesions | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| GANCICLOVIR | melanoma | dog | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| GEMCITABINE | lymphoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| GEMCITABINE | osteosarcoma | dog | indeterminate | positive (phase-2) | **indeterminate** | exemplar |
| GLUTAMINE | parvovirus infection | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| GLYBURIDE | spinal cord injury | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| GLYCERYL | prostatic carcinoma | dog | indeterminate | positive (phase-2) | **indeterminate** | pubmed |
| GRANULOCYTE COLONY STIMULATING FACTOR | mitral valve disease | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| GRAPIPRANT | osteoarthritis | dog | positive | indeterminate (none) | **indeterminate** | exemplar, pubmed |
| GRAPIPRANT | postoperative pain | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| GS 441524 | feline infectious peritonitis | cat | positive | indeterminate (phase-2) | **indeterminate** | pubmed |
| GS 9219 | lymphoma | dog | positive | indeterminate (none) | **indeterminate** | exemplar, pubmed+exemplar |
| HEPARIN | peritonitis | dog | indeterminate | indeterminate (earlier) | **indeterminate** | pubmed |
| HETASTARCH | hypoalbuminemia | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| HL036 | keratoconjunctivitis sicca | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| HUPERZINE A 0 4 MG | epilepsy | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| HYALURONAN | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| HYALURONIC | portosystemic shunts | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| HYALURONIC | dry eye disease | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| HYDRALAZINE | hypertension crisis | dog-and-cat | indeterminate | positive (us-approval) | **indeterminate** | exemplar |
| HYDROCHLORIC | acidemia | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| HYDROCODONE | perioperative analgesia | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| HYDROMORPHONE | perioperative analgesia | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| HYDROMORPHONE | cranial cruciate ligament disease | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| HYDROMORPHONE | gastroesophageal reflux | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| HYDROXYCHLOROQUINE | lymphoma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| HYDROXYETHYL STARCH | shock | cat | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| HYDROXYETHYL STARCH 130 0 4 | hypoalbuminemia | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| HYDROXYETHYL STARCH 130 0 4 | gastric dilatation volvulus | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| HYPERBARIC OXYGEN THERAPY | snake envenomation wound complications | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| HYPERIMMUNE PLASMA | parvoviral enteritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| HYPERTONIC SALINE | hypertensive emergency | dog-and-cat | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| HYPOCHLORITE | pyoderma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| IDARUBICIN | lymphoma | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| IMATINIB | oral fibrosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| IMMUNE PLASMA | parvovirus infection | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| INDOCYANINE GREEN | chylothorax | dog | indeterminate | indeterminate (earlier) | **indeterminate** | pubmed |
| INDOCYANINE GREEN | mast cell tumor | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| INDOCYANINE GREEN | thyroid carcinoma | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| INSULIN | diabetes mellitus | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| INTERFERON ALPHA | keratoconjunctivitis sicca | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| INTERLEUKIN 12 | soft tissue sarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| INTERLEUKIN 12 | mast cell tumor | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| INTERLEUKIN 2 | osteosarcoma | dog | indeterminate | indeterminate (phase-2) | **indeterminate** | pubmed |
| INTERLEUKIN 2 | soft tissue sarcoma | dog | indeterminate | negative (phase-2) | **indeterminate** | pubmed |
| INTERMEDIATE ACTING INSULIN | diabetes mellitus | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| INTRAVENOUS LIPID EMULSION | permethrin toxicosis | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| IOHEXOL | spinal disease | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| IOHEXOL | thyroid carcinoma | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| ISOFLURANE | intracranial disease | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| ISOFLURANE | intervertebral disc disease | dog | indeterminate | indeterminate (earlier) | **indeterminate** | pubmed |
| ITRACONAZOLE | malassezia dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| IV IMMUNOGLOBULIN | polyradiculoneuritis | dog | negative | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| IVABRADINE | hypertrophic cardiomyopathy with lvot obstruction | cat | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| IVERMECTIN | spirocercosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| IVERMECTIN | thelaziosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| IVERMECTIN | transmissible venereal tumor | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| KETAMINE | pyometra | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| KETAMINE | cranial cruciate ligament rupture | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| KETAMINE | intervertebral disc disease | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| KETOCONAZOLE | malassezia dermatitis | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| KPT 9274 | b cell lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LACTATED RINGER S SOLUTION | circulatory abnormalities | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LACTULOSE | hepatic encephalopathy | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| LACTULOSE | portosystemic shunts | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| LIDOCAINE | cranial cruciate ligament rupture | dog | indeterminate | negative (earlier) | **indeterminate** | pubmed |
| LIDOCAINE | portosystemic shunt | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LIDOCAINE | pulmonic stenosis | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| LISPRO INSULIN | diabetic ketoacidosis | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LMP400 | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LMP744 | lymphoma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LMP776 | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LOBAPLATIN | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LOMUSTINE | mast cell tumour | dog | positive | indeterminate (none) | **indeterminate** | exemplar |
| LOMUSTINE | gastrointestinal lymphoma | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| LOMUSTINE | lymphoma of epitheliotropic t-cell type | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| LOSARTAN | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| LOTILANER | tick infestation | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LOTILANER | gastrointestinal nematode infection | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LOTILANER | heartworm disease prevention | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LOTILANER | flea and tick infestation | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| LOW FREQUENCY ACUPOINT ELECTRICAL STIMULATION | cranial cruciate ligament rupture | dog | mixed | indeterminate (none) | **indeterminate** | pubmed |
| LYSINE | hypertension | cat | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| M032 | glioma | dog | indeterminate | indeterminate (phase-2) | **indeterminate** | pubmed |
| MAGNESIUM | hypomagnesemia | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MAGNESIUM SULFATE | ventricular arrhythmias | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MALTODEXTRIN | food responsive diarrhoea | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| MASITINIB | atopic dermatitis | dog | positive | indeterminate (none) | **indeterminate** | exemplar |
| MASITINIB | epitheliotropic lymphoma | dog | positive | indeterminate (none) | **indeterminate** | exemplar |
| MASITINIB | oral fibrosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| MASITINIB | malignant melanoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| MEGESTROL | eosinophilic keratitis | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| MELATONIN | flank alopecia | dog | negative | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MELOXICAM | orthopedic disorders | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MELOXICAM | acute musculoskeletal pain | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| MELOXICAM | idiopathic cystitis | cat | negative | indeterminate (none) | **indeterminate** | pubmed |
| MELOXICAM | neuropathic pain | dog | negative | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MESENCHYMAL STEM CELLS | kidney disease | dog-and-cat | indeterminate | negative (phase-2) | **indeterminate** | pubmed |
| METHADONE | ruptured cruciate ligament | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| METHIONINE | atopic dermatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| METHIONINE | struvite urolithiasis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| METHYLENE BLUE | thyroid carcinoma | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| METHYLENE BLUE | oral neoplasia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| METHYLPREDNISOLONE | immune-mediated hemolytic anemia | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| METOCLOPRAMIDE | laryngeal paralysis | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| METRONIDAZOLE | inflammatory bowel disease | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| METRONIDAZOLE | portosystemic shunts | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| METRONIDAZOLE | chronic ulcerative stomatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| MICRONEEDLING | alopecia | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MIDAZOLAM | perioperative analgesia | dog | negative | indeterminate (earlier) | **indeterminate** | pubmed |
| MIDAZOLAM | premedication | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MIDAZOLAM | chronic kidney disease | cat | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MIGLUSTAT | niemann-pick disease type c | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MILTEFOSINE | leishmaniasis | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MINOCYCLINE | ehrlichiosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOGAMULIZUMAB | prostate cancer | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| MOMETASONE FUROATE | otitis externa | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MORPHINE | cranial cruciate ligament rupture | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MORPHINE | trauma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MORPHINE | perioperative analgesia | cat, dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| MORPHINE | corneal ulceration | dog-and-cat | negative | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | spirocercosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | intestinal nematode infections | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | tick infestation | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | thelaziosis | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | hookworm infection | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| MOXIDECTIN | flea infestation | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | heartworm disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | angiostrongylosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MOXIDECTIN | sarcoptic mange | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| MYCOPHENOLATE MOFETIL | tracheal collapse | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| MYCOPHENOLATE MOFETIL | immune-mediated hemolytic anemia | dog | negative | indeterminate (earlier) | **indeterminate** | pubmed |
| NAVITOCLAX | hematological cancer | dog | indeterminate | positive (phase-2) | **indeterminate** | pubmed |
| NETARSUDIL | corneal endothelial degeneration | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| NHS IL12 | melanoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| NICLOSAMIDE | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| NSAID | osteosarcoma | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| OCTREOTIDE | osteosarcoma | dog | negative | indeterminate (earlier) | **indeterminate** | pubmed |
| OMEPRAZOLE | chronic kidney disease | cat | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| OMEPRAZOLE | intervertebral disc extrusion | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| OZONE | otitis externa | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PAMIDRONATE | osteosarcoma | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | exemplar, pubmed |
| PANCREATIC ENZYME SUPPLEMENT | exocrine pancreatic insufficiency | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PAROMOMYCIN | leishmaniasis | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PARTS A B ADRABETADEX | niemann-pick disease type c | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| PASIREOTIDE | pituitary-dependent hyperadrenocorticism | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| PATUPILONE | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PEUMUS BOLDUS LEAF | atopic dermatitis | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| PHENYLEPHRINE | hypotension | cat | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| PICLIDENOSON | osteoarthritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PIROXICAM | urothelial carcinoma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PIROXICAM | osteosarcoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| PIROXICAM | mammary carcinoma | dog | positive | indeterminate (earlier) | **indeterminate** | exemplar |
| PLATELET RICH PLASMA | alopecia | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PLATELET RICH PLASMA | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PLERIXAFOR | immunodeficiency virus infection | cat | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| POLYETHYLENE GLYCOL | intervertebral disc disease | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| PRAZIQUANTEL | thelaziosis | cat, dog, dog-and-cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| PRAZIQUANTEL | nematode and cestode infection | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| PRAZIQUANTEL | hookworm infection | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PRAZIQUANTEL | ectoparasite infestation | cat | positive | indeterminate (us-approval) | **indeterminate** | pubmed |
| PRAZIQUANTEL | gastrointestinal nematode infection | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PRAZIQUANTEL | heartworm disease prevention | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PREDNISOLONE | mast cell tumour | dog | positive | indeterminate (none) | **indeterminate** | exemplar, exemplar |
| PREDNISOLONE | diabetes mellitus | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PREDNISOLONE | aural hematoma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PREDNISOLONE | chronic pancreatitis | cat | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| PREDNISOLONE | polydipsia and polyuria | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PREDNISONE | mast cell tumor | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PREDNISONE | immune-mediated polyarthritis | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| PREDNISONE | brain tumor | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PREGABALIN | intervertebral disc disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PREGABALIN | neuropathic pain related to syringomyelia | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PREGABALIN | syringomyelia and chiari-like malformation | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PRGF | patellar desmopathy | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| PROBIOTIC | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed+exemplar |
| PROBIOTIC | acute hemorrhagic diarrhea syndrome | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PROPARACAINE | infected corneal ulcer | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PROPOFOL | perioperative analgesia | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PROPOFOL | neurological conditions | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PROPOFOL | glaucoma | dog | indeterminate | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PROPOFOL | laryngeal paralysis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PROPOFOL | endoscopic procedures | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| PROPOFOL | status epilepticus | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| PROPRANOLOL | glioma | dog | positive | indeterminate (earlier) | **indeterminate** | pubmed |
| PROPYLTHIOURACIL | hyperthyroidism | cat | indeterminate | positive (us-approval) | **indeterminate** | exemplar |
| PYRANTEL | flea infestation | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| PYRANTEL | angiostrongylosis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PYRANTEL | sarcoptic mange | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| PYRANTEL | heartworm disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| RAAV2TYF GRK1 HRPGRCO | retinitis pigmentosa | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| RADIATION THERAPY | cardiac neoplasia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| RADIATION THERAPY | intracranial neoplasia | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| RADIATION THERAPY | cystitis | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| RADIOIODINE | hyperthyroidism | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| RADIOTHERAPY | sarcoma | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| RALTEGRAVIR | feline leukemia virus infection | cat | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| RED BLOOD CELLS | autoimmune hemolytic anemia | dog | indeterminate | positive (earlier) | **indeterminate** | pubmed |
| RESVERATROL | cardiac disease | dog | indeterminate | mixed (phase-2) | **indeterminate** | pubmed |
| RIFAMPICIN | leprosy | cat | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| RILZABRUTINIB | pemphigus | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| RIVAROXABAN | immune-mediated hemolytic anemia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| ROPINIROLE | foreign body or toxin ingestion | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| ROPINIROLE | foreign body ingestion | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SACCHAROMYCES BOULARDII | parvovirus enteritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SALICYLIC | pyoderma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SELEGILINE | pituitary-dependent hypercortisolism | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| SEVOFLURANE | intervertebral disc disease | dog | indeterminate | indeterminate (us-approval) | **indeterminate** | pubmed |
| SHORT ACTING INSULIN | diabetes mellitus | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| SILDENAFIL | myxomatous mitral valve disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SILDENAFIL | pulmonary hypertension | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| SILDENAFIL | megaesophagus | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| SIROLIMUS | hypertrophic cardiomyopathy | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| SODIUM BENZOATE | malassezia dermatitis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| SPINOSAD | cutaneous myiasis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SPIRONOLACTONE | myxomatous mitral valve disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| STANNOUS FLUORIDE | superficial pyoderma | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| STANOZOLOL | osteoarthritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SUBSTANCE P SAPORIN | bone cancer pain | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SUFENTANIL | otitis media | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| SULFADIAZINE | pyometra | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| SULFORAPHANE | lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| TACROLIMUS | atopic dermatitis | dog | indeterminate | positive (us-approval) | **indeterminate** | exemplar |
| TARAXACUM OFFICINALE | chronic kidney disease | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| TCMCB07 | cachexia | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TELMISARTAN | idiopathic epilepsy | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| TEMOZOLOMIDE | brain tumor | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| TEMOZOLOMIDE | glioma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| TERBINAFINE | malassezia dermatitis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TERBINAFINE | otitis externa | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TERBINAFINE | sino-nasal aspergillosis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| TERBINAFINE | malassezia otitis externa | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| THERAPEUTIC AUTOLOGOUS LYMPHOCYTES | non-hodgkin lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| THERAPEUTIC ULTRASOUND | periodontal disease | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| THIOPENTAL | anaesthesia | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| THYROID | hyperthyroidism | cat | negative | indeterminate (none) | **indeterminate** | pubmed |
| THYROID | thyroid carcinoma | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| TOLFENAMIC | perioperative analgesia | cat | positive | indeterminate (none) | **indeterminate** | pubmed |
| TORSEMIDE | mitral valve disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TRAZODONE | postsurgical confinement | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TRAZODONE | stress | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| TRAZODONE | perioperative analgesia | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| TRIAMCINOLONE ACETONIDE | osteoarthritis | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| TRICLOSAN | cranial cruciate ligament disease | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TRILOSTANE | hyperadrenocorticism | cat, dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| TRIMETHOPRIM | bacterial cystitis | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| TRIMETHOPRIM | pyometra | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| ULTRASOUND THERAPY COMBINED WITH CHITOSAN NANOPARTICLES GEL | osteoarthritis | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| UMBILICAL CORD DERIVED MESENCHYMAL STEM CELL | osteoarthritis | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| UROKINASE | intracranial tumors | dog | indeterminate | indeterminate (phase-2) | **indeterminate** | pubmed |
| VALSARTAN | myxomatous mitral valve disease | dog | indeterminate | positive (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| VAPOCOOLANT SPRAY | catheter pain | dog-and-cat | negative | indeterminate (none) | **indeterminate** | pubmed |
| VECURONIUM | diabetes mellitus | dog | indeterminate | indeterminate (none) | **indeterminate** | pubmed |
| VEMURAFENIB | urothelial carcinoma | dog | positive | indeterminate (none) | **indeterminate** | pubmed |
| VENETOCLAX | hematological cancer | dog | indeterminate | positive (us-approval) | **indeterminate** | pubmed |
| VERDINEXOR | cutaneous epitheliotropic t-cell lymphoma | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar, pubmed+exemplar |
| VINBLASTINE | mast cell tumour | dog | positive | indeterminate (none) | **indeterminate** | exemplar, exemplar, exemplar, pubmed+exemplar, pubmed+exemplar |
| VINCRISTINE | mast cell tumour | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar, pubmed+exemplar |
| VITAMIN C | muscle pain | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **indeterminate** | pubmed |
| VITAMIN K1 | chronic enteropathy | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| YUNNAN BAIYAO | cardiac masses with pericardial effusion | dog | negative | indeterminate (none) | **indeterminate** | pubmed |
| 6 HYDROXYETHYL STARCH 130 0 4 | acute kidney injury | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ACETYLCYSTEINE | chronic kidney disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ACUPUNCTURE | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ADEFOVIR | immunodeficiency virus infection | cat | mixed | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| AMANTADINE | neuropathic pain related to degenerative lumbosacr | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ANTIOXIDANTS | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| BENAZEPRIL | chronic kidney disease | cat, dog | mixed | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| BERAPROST | chronic kidney disease | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| BINDERS | chronic kidney disease | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| BLEOMYCIN | melanoma | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| BORIC | otitis externa | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| BOSWELLIA | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CANNABIDIOL | osteoarthritis | cat, dog | mixed | positive (phase-2) | **mixed** | pubmed |
| CANNABIDIOL | atopic dermatitis | dog | mixed | positive (phase-2) | **mixed** | pubmed |
| CANNABIDIOL | postoperative pain | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CARNITINE | aging | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CETIRIZINE | atopic dermatitis | cat | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CHITOSAN | chronic kidney disease | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CHLORHEXIDINE | urinary catheter biofilm | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CHOLECALCIFEROL | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CHONDROITIN | degenerative joint disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CLINDAMYCIN | periodontal disease | cat, dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed |
| COBALAMIN | chronic enteropathy with hypocobalaminemia | cat, dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CURCUMIN | osteoarthritis | dog-and-cat | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CURCUMIN | chronic kidney disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CYCLOPHOSPHAMIDE | soft tissue sarcoma | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| CYCLOPHOSPHAMIDE | osteosarcoma | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| DEXMEDETOMIDINE | perioperative analgesia | cat, dog | mixed | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| DEXMEDETOMIDINE | postoperative pain | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| DEXMEDETOMIDINE | sedation | cat, dog | mixed | positive (us-approval) | **mixed** | pubmed |
| DOCOSAHEXAENOIC | degenerative joint disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| DOCOSAHEXAENOIC | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| EICOSAPENTAENOIC | osteoarthritis | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ELASTIN | osteoarthritis | dog | mixed | positive (earlier) | **mixed** | pubmed |
| ENAMEL MATRIX DERIVATIVE | periodontal disease | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ENTEROCOCCUS FAECALIS | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| EPIRUBICIN | hemangiosarcoma | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| ESSENTIAL FATTY ACIDS | atopic dermatitis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| FISH OIL | osteoarthritis | dog | mixed | negative (phase-3-or-meta-analysis) | **mixed** | pubmed |
| FISH OIL | heart failure | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| GABAPENTIN | postoperative pain | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| GABAPENTIN | stress | cat | mixed | positive (earlier) | **mixed** | pubmed |
| GABAPENTIN | anxiety | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| GENTAMICIN | otitis externa | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| GLUCOCORTICOID | allergic reaction | dog | indeterminate | mixed (earlier) | **mixed** | pubmed |
| GLUCOSAMINE | degenerative joint disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HIGH FLOW NASAL CANNULA | hypoxemia | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HYALURONATE | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HYALURONIC | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HYLAN G F 20 | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HYPERTONIC SALINE | hemorrhagic shock | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| HYPERTONIC SALINE | shock | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| IMIDAPRIL | heart failure | dog | positive | mixed (phase-2) | **mixed** | pubmed |
| INSULIN GLARGINE | diabetic ketoacidosis | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| INTERLEUKIN 12 | melanoma | dog | positive | mixed (phase-2) | **mixed** | pubmed |
| L REUTERI | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| L THEANINE | stress-related emotional signs | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| LACTATE | dehydration | cat | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| LACTOBACILLUS RHAMNOSUS | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| LIDOCAINE | gastric dilatation volvulus | dog | mixed | indeterminate (none) | **mixed** | pubmed |
| LIDOCAINE | tachycardia | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MELATONIN | anaesthesia | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MELATONIN | anxiety | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MELOXICAM | osteoarthritis | cat, dog | mixed | positive (us-approval) | **mixed** | pubmed |
| MELPHALAN | melanoma | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MESENCHYMAL STROMAL CELLS | intervertebral disc degeneration | dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METAMIZOLE | perioperative analgesia | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METHIONINE | taurine deficiency | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METHYLPREDNISOLONE | intervertebral disc disease | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METRONIDAZOLE | periodontal disease | cat | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METRONIDAZOLE | chronic enteropathy | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| METRONIDAZOLE | colitis | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MIDAZOLAM | anaesthesia | cat, dog | mixed | positive (us-approval) | **mixed** | pubmed |
| MIDAZOLAM | sedation | cat, dog | mixed | positive (us-approval) | **mixed** | pubmed |
| MIRTAZAPINE | weight loss | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MITOMYCIN | urothelial carcinoma | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MITOXANTRONE | urothelial carcinoma | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| MOLNUPIRAVIR | feline infectious peritonitis | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| OMEGA 3 FATTY | osteoarthritis | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| OMEGA 3 FATTY ACIDS | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PENTOSAN POLYSULFATE | osteoarthritis | dog | positive | mixed (phase-2) | **mixed** | pubmed |
| PERMETHRIN | leishmaniosis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PERMETHRIN | tick infestation | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PHOSPHORUS | chronic kidney disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PLATELET RICH PLASMA | cranial cruciate ligament tear | dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PLATELET RICH PLASMA | bone fractures | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PREDNISOLONE | steroid responsive meningitis-arteritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PREDNISONE | lymphoma | dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | exemplar, pubmed, pubmed+exemplar |
| PREDNISONE | inflammatory bowel disease | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PREGABALIN | fear and anxiety | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| PYRANTEL | intestinal nematode infections | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| QUINAPRIL | congestive heart failure | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| SALICYLIC | pruritus | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| SPIRONOLACTONE | heart failure due to cardiomyopathy | cat, dog | mixed | positive (us-approval) | **mixed** | pubmed |
| STROMAL VASCULAR FRACTION | osteoarthritis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| TADALAFIL | pulmonary hypertension | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| TELMISARTAN | chronic kidney disease | cat | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| TORASEMIDE | congestive heart failure | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| TRAZODONE | anxiety | cat, dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| TRIAMCINOLONE HEXACETONIDE | osteoarthritis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| VASOPRESSIN | cardiopulmonary arrest | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| VINBLASTINE | lymphoma | cat, dog | mixed | positive (phase-3-or-meta-analysis) | **mixed** | pubmed, pubmed+exemplar |
| VITAMIN E | atopic dermatitis | dog | indeterminate | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| VITAMIN E | osteoarthritis | dog | negative | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| VITAMINS | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| WHEY | atopic dermatitis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | exemplar |
| ZINC | pruritus | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |
| ZOLEDRONATE | malignant osteolysis | dog | positive | mixed (phase-3-or-meta-analysis) | **mixed** | pubmed |

## efficacy · species-specific-biologic: 2 pairs — {'concordant': 2}

| drug | vet indication | species | vet | human (level) | pair | sources |
|---|---|---|---|---|---|---|
| FASINUMAB+TANEZUMAB | osteoarthritis | cat, dog, dog-and-cat | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, exemplar, exemplar, pubmed+exemplar, pubmed+exemplar |
| NEMOLIZUMAB | atopic dermatitis | dog | positive | positive (us-approval) | **concordant** | exemplar, exemplar, pubmed+exemplar |

## efficacy · class-analogue: 15 pairs — {'indeterminate': 10, 'concordant': 3, 'mixed': 1, 'discordant': 1}

| drug | vet indication | species | vet | human (level) | pair | sources |
|---|---|---|---|---|---|---|
| ABROCITINIB+BARICITINIB+TOFACITINIB+UPADACITINIB | atopic dermatitis and allergic dermatitis | cat, dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, exemplar, pubmed+exemplar |
| SUNITINIB | adenocarcinoma | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar, pubmed+exemplar |
| SUNITINIB | adrenal gland tumour | dog | positive | positive (earlier) | **concordant** | exemplar |
| SUNITINIB | mesothelioma | dog | positive | negative (phase-2) | **discordant** | exemplar |
| ABROCITINIB+BARICITINIB+TOFACITINIB+UPADACITINIB | epitheliotropic lymphoma | dog | indeterminate | indeterminate (earlier) | **indeterminate** | pubmed+exemplar |
| SELINEXOR | cutaneous epitheliotropic t-cell lymphoma | dog | positive | indeterminate (none) | **indeterminate** | exemplar, pubmed+exemplar |
| SUNITINIB | mast cell tumour | dog | positive | indeterminate (none) | **indeterminate** | exemplar, pubmed+exemplar |
| SUNITINIB | heart base tumour | dog | indeterminate | indeterminate (none) | **indeterminate** | exemplar |
| SUNITINIB | thyroid carcinoma | dog | indeterminate | positive (phase-2) | **indeterminate** | exemplar |
| SUNITINIB | chemodectoma | dog | indeterminate | positive (phase-2) | **indeterminate** | exemplar |
| SUNITINIB | insulinoma | dog | positive | indeterminate (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| SUNITINIB | nasal carcinoma | dog | positive | indeterminate (none) | **indeterminate** | exemplar |
| SUNITINIB | osteosarcoma | dog | indeterminate | positive (phase-2) | **indeterminate** | exemplar |
| SUNITINIB | hepatocellular carcinoma | dog | indeterminate | negative (phase-3-or-meta-analysis) | **indeterminate** | exemplar |
| SUNITINIB | inflammatory mammary carcinoma | dog | mixed | negative (phase-2) | **mixed** | exemplar |

## safety · species-specific-biologic: 1 pairs — {'concordant': 1}

| drug | vet indication | species | vet | human (level) | pair | sources |
|---|---|---|---|---|---|---|
| TANEZUMAB | musculoskeletal adverse events | dog | positive | positive (phase-3-or-meta-analysis) | **concordant** | exemplar |

Cost (uncached): $25.29
