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


# --- metric polarity -------------------------------------------------------
# Source studies report metrics that point in opposite directions: a high
# "concordance rate" means the model predicted well; a high "failure rate" means
# the opposite. Displaying them in one value-sorted table implies a comparison
# that does not exist, so metrics are grouped by family and never co-sorted.
METRIC_FAMILIES = [
 ("agreement",  "higher = animal and human agreed more",
  ["concordan","agreement","similar effect","reproducib","replicat","accuracy","correct",
   "translat","mimic","predictive value","ppv","npv","sensitivity","specificity","auc",
   "receiver","correlation","clinical benefit","success"]),
 ("disagreement","higher = animal and human diverged more",
  ["failure","discordan","overestimat","false positive","false negative","attrition",
   "poor predict","not replicat","irreproducib","threat"]),
]
def metric_family(metric):
    t = str(metric or "").lower()
    for fam, _, keys in METRIC_FAMILIES:
        for k in keys:
            if k in t:
                return fam
    return "unclassified"
def family_note(fam):
    for f, note, _ in METRIC_FAMILIES:
        if f == fam: return note
    return "direction not determined from the reported metric name"


# --- model organisms for the site --------------------------------------------
# One canonical name per organism. The extractor emits "monkey", "rhesus monkey",
# "cynomolgus monkey", "baboon" and "non-human primate" as five organisms, which
# fragments the table into rows backed by one study each. Group labels are kept as
# their own organisms (a paper reporting "43% of rodent studies" did not measure mice
# separately) but carry no suffix.
ORGANISM_GROUPS = {"rodent", "non-rodent", "large animal", "small animal",
                   "non-human primate", "farm animal", "companion animal"}

def organism(name):
    """Canonical organism name, or None if the label carries no organism information."""
    t = re.sub(r"\s+", " ", str(name or "").strip().lower())
    t = re.sub(r"\s*\(as grouped\)$", "", t)
    if not t or t in {"animal","animals","human","humans","species","not specified",
                      "animal model","animal models","other"}:
        return None
    if t in {"nonrodent","non rodent","non-rodents","nonrodents"}: return "non-rodent"
    if t in {"rodents","rodentia"}: return "rodent"
    if t in {"nhp","nhps"}: return "non-human primate"
    if t in {"zebra fish"}: return "zebrafish"
    if t in {"ewe","ewes","lamb","lambs"}: return "sheep"
    # not organisms: a model type, and a non-label
    if t in {"pdx models","pdx","xenograft","others","other species"}: return None
    if t in ORGANISM_GROUPS: return t
    m = _match(t, SPECIES)
    return m or t          # keep an unrecognised but specific label rather than dropping it

def organisms(names):
    out = []
    for n in names or []:
        c = organism(n)
        if c and c not in out: out.append(c)
    return out
