"""Map free-text extraction onto the controlled vocabularies in PLAN.md.

Raw LLM output is never overwritten: normalisation adds *_norm fields alongside,
so a mapping error can be found and corrected without re-extracting."""
import re

SPECIES = [
 ("non-human primate", ["primate","macaque","rhesus","cynomolgus","marmoset","baboon","monkey","chimpanzee","ape"]),
 ("mouse",   ["mouse","mice","murine","c57","balb"]),
 ("rat",     ["rat","rats","sprague","wistar","fischer"]),
 ("dog",     ["dog","dogs","canine","canines","beagle"]),
 ("cat",     ["cat","cats","feline"]),
 ("pig",     ["pig","pigs","swine","porcine","minipig","gottingen","yorkshire"]),
 ("rabbit",  ["rabbit","leporine","new zealand white"]),
 ("guinea pig", ["guinea pig","guinea pigs","hartley","cavia"]),
 ("hamster", ["hamster"]),
 ("sheep",   ["sheep","ovine","lamb"]),
 ("goat",    ["goat","caprine"]),
 ("cattle",  ["cattle","bovine","cow","calf","calves"]),
 ("horse",   ["horse","equine","pony"]),
 ("chicken", ["chicken","hen","avian","poultry"]),
 ("ferret",  ["ferret"]),
 ("zebrafish", ["zebrafish","danio"]),
]
# 'human' is the reference standard, not an animal model; 'rodent'/'animal' are
# too coarse to attribute to a species and become 'unspecified'.
DROP = {"human","humans","non-human","nonhuman","patient","patients"}
COARSE = {"rodent","rodents","animal","animals","mammalian","mammal","mammals","non-rodent",
          "nonrodent","larger mammals","model organisms","mammalian (nonhuman)","not-stated",
          "laboratory animals","species"}

AREAS = [
 ("oncology", ["cancer","tumor","tumour","oncolog","carcinom","sarcoma","lymphoma","leukemi",
               "melanoma","neoplas","metasta","glioma","myeloma"]),
 ("hepatic", ["liver","hepat","nash","nafld","masld","mash","steato","cirrhos"]),
 ("renal", ["kidney","renal","nephro","nephritis","uremic","alport","dialysis"]),
 ("cardiovascular", ["cardi","heart","vascular","atheroscler","hypertens","arrhythm",
                     "myocard","stroke volume","thrombo","haemorrhage","hemorrhage"]),
 ("neurology/stroke", ["stroke","ischemi","ischaemi","cerebral","neuroprotect","brain injury","epilep"]),
 ("neurodegeneration", ["alzheimer","parkinson","huntington","amyotrophic","als","dementia",
                        "neurodegener","multiple sclerosis"]),
 ("psychiatric", ["psychiatr","depress","anxiety","schizophren","autism","addiction",
                  "substance","alcohol","neuropsychiatric","bipolar"]),
 ("sepsis/inflammation", ["sepsis","septic","inflamm","endotox","burn","immune","autoimmun","arthriti"]),
 ("infectious disease", ["infect","virus","viral","bacteri","influenza","hiv","tuberculo",
                         "covid","sars","malaria","vaccine","antimicrob","parasit"]),
 ("metabolic", ["diabet","obes","metabolic","insulin","lipid","cholesterol","osteoporo"]),
 ("respiratory", ["respirat","asthma","lung","pulmon","copd","fibrosis"]),
 ("ophthalmology", ["eye","retina","ocular","ophthalm","vision","blind","uveitis"]),
 ("musculoskeletal", ["bone","muscle","tendon","cartilage","osteoarthr","dystroph","skeletal","fracture"]),
 ("pain", ["pain","analges","nocicept","migraine"]),
 ("dermatology", ["skin","dermat","atopic","wound"]),
 ("reproductive", ["reproduct","fertil","pregnan","teratog","embryo"]),
]

def _match(text, table):
    t = re.sub(r"[^a-z ]", " ", str(text).lower())
    for canon, keys in table:
        for k in keys:
            if re.search(r"\b" + re.escape(k), t):
                return canon
    return None

def species(raw):
    out = []
    for x in raw or []:
        s = str(x).strip().lower()
        if not s or s in DROP: continue
        if s in COARSE:
            out.append("unspecified"); continue
        m = _match(s, SPECIES)
        out.append(m or "other")
    seen, res = set(), []
    for x in out:
        if x not in seen: seen.add(x); res.append(x)
    return res

def areas(raw):
    out = []
    for x in raw or []:
        s = str(x).strip().lower()
        if not s or s in ("not-stated", "not stated"): continue
        m = _match(s, AREAS)
        out.append(m or "other")
    seen, res = set(), []
    for x in out:
        if x not in seen: seen.add(x); res.append(x)
    return res
