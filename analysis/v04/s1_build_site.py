"""Build the v0.4 site from editable content files plus the frozen v0.4 outputs.

All prose lives in content/*.md and is edited there, never here. This module supplies the data,
draws the things that cannot be written by hand (the heatmap, the tables, the browsers), and
renders the markdown around them. content/README.md documents every token for the writer.

Structure
  index.html        the report, from content/report.md, with a section rail built from its headings
  results.html      all final results, searchable and sortable
  pairs.html        all classified dog and cat drug pairs
  spotcheck.html    the seeded sample anyone can check the review against
  study/<id>.html   one page per study, wrapped by content/study.md
  assets/           one stylesheet and one script, shared by every page
  api/*.json        the same content as data

Two rules hold throughout. Statistics are never recomputed here: the strata, Q4 and recall numbers
are the ones computed by d3/d4/d5/r3 and are embedded from their reports verbatim, with build
provenance stripped. Quotes are reproduced byte-exact, so an asterisk inside a quotation is the
paper's own significance marker and stays.

Species and disease-area labels are normalized for display only (the records keep what the
extractor recorded): stray species spellings fold onto the frozen vocabulary, off-vocabulary
disease areas fold into one "other" row, and results whose species could not be resolved to one
animal are shown in their own labeled column rather than dropped.
"""
import sys, os, re, json, html, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import load, species_column, today, J, V04

OUT = J("site", "v04_build")
CONTENT = J("content")
e = lambda s: html.escape(str(s if s is not None else ""))
# Paper-derived text (statements) is not markdown; strip stray emphasis characters so they do not
# surface as asterisks. Quotes are never passed through this: they are reproduced exactly.
t = lambda s: e(re.sub(r"\*+", "", str(s if s is not None else "")))

LEVELS = [("A-outcome-concordance", "A", "intervention outcomes"),
          ("B-toxicity-safety-concordance", "B", "toxicity and safety"),
          ("C-biological-similarity", "C", "disease biology")]
DIR_LABEL = {"animal-corresponded": "corresponded", "animal-did-not-correspond": "did not correspond",
             "mixed": "mixed", "not-applicable": "not applicable"}
DIR_CLASS = {"animal-corresponded": "ok", "animal-did-not-correspond": "no", "mixed": "mid"}

SPECIES_FIX = {"guinea pig": "guinea pig", "cynomolgus monkey": "non-human primate",
               "Macaca fascicularis": "non-human primate", "sheep": "sheep/goat",
               "pig-minipig": "pig", "sheep-goat": "sheep/goat",
               "non-human-primate": "non-human primate", "other-rodent": "guinea pig"}
# "other-species" is not a category, it is whatever the extractor could not place. Where the
# reported label names an animal the vocabulary does have, use it; what is left keeps the honest
# catch-all name rather than being quietly assigned somewhere.
OTHER_FIX = {r"guinea ?pig": "guinea pig", r"hamster": "hamster", r"gerbil": "gerbil",
             r"ferret": "other-species", r"chicken|chick\b|avian": "other-species"}
UNRESOLVED = {"grouped-label", "human"}

# Recovering species from species_as_reported (amendment A7).
#
# Every result in this review compares an animal with a human, so a reported label such as
# "canine and human" names one animal and the comparator — not two animals. The extractor
# collapsed those to "grouped-label", which put 879 results into a column meaning "species
# unknown" and emptied cells that do hold evidence. Where the reported label names exactly one
# animal from the frozen vocabulary, that is the species; where it names several ("both species",
# "rodents", "animals") or none, it stays unresolved. The rule never invents a species, and the
# stored records are unchanged: this is a display mapping, like the spelling fixes above.
ANIMAL_WORDS = {
    "dog": r"\b(dogs?|canine|canis)\b", "cat": r"\b(cats?|feline)\b",
    "mouse": r"\b(mice|mouse|murine|mus musculus)\b", "rat": r"\b(rats?|rattus)\b",
    "non-human-primate": r"\b(monkeys?|macaques?|primates?|rhesus|cynomolgus|marmoset|baboon)\b",
    "pig-minipig": r"\b(pigs?|swine|porcine|minipigs?)\b",
    "rabbit": r"\b(rabbits?|leporine|oryctolagus)\b",
    "sheep-goat": r"\b(sheep|ovine|goats?|caprine)\b", "zebrafish": r"\b(zebrafish|danio)\b",
    "drosophila": r"\b(drosophila|fruit fly|fruit flies)\b",
    "c-elegans": r"\b(c\.? ?elegans|nematode)\b", "horse": r"\b(horses?|equine)\b",
    "guinea pig": r"\b(guinea[ -]?pigs?|cavia porcellus)\b",
    "hamster": r"\b(hamsters?|mesocricetus|cricetulus)\b",
    "gerbil": r"\b(gerbils?|meriones)\b",
}
ANIMAL_WORDS["mouse"] += r"|\bGEMMs?\b"


# "guinea pig" contains "pig", so the pig-minipig pattern fires on it and a guinea-pig result is
# read as a pig result too. Mask the compound term before any animal matching.
GUINEA = re.compile(r"guinea[ -]?pigs?", re.I)


def animals_named(text):
    """Every animal from the frozen vocabulary named in this text."""
    t = GUINEA.sub("GUINEAPIG", text or "")
    found = {k for k, pat in ANIMAL_WORDS.items() if re.search(pat, t, re.I)}
    if GUINEA.search(text or ""):
        found.add("guinea pig")
    return found


def _one_animal(text):
    found = animals_named(text)
    return found.pop() if len(found) == 1 else None


def recovered_species(r):
    """The species this result is about, or None if it cannot be pinned down.

    Sources in order of authority (amendments A7, A8): the extractor's own species_as_reported
    label first; then, only if that is non-specific, the study title or the result's own statement
    and quote. Where both of those fire they agreed in 74 of 74 checked cases. Any source naming
    more than one animal resolves nothing, so the rule cannot invent a species.
    """
    s = _one_animal(str(r.get("species_as_reported") or ""))
    if s:
        return s
    from_title = _one_animal(r.get("title") or "")
    from_text = _one_animal((r.get("statement") or "") + " " + (r.get("quote") or ""))
    if from_title and from_text:
        return from_title if from_title == from_text else None
    return from_title or from_text
SPECIES_ORDER = ["mouse", "rat", "guinea pig", "rabbit", "pig", "sheep/goat",
                 "non-human primate", "laboratory dog", "companion dog", "laboratory cat",
                 "companion cat", "horse", "zebrafish"]
# Columns that name no species. Most of what lands here are meta-analyses whose finding is about
# animal models as a class, so there is no species in the paper to use; the rest are records whose
# species field holds the human side of the comparison. They are counted and reported, not shown as
# a column pretending to be a species (A25).
NON_SPECIES = {"not resolved", "other-species"}
# Invertebrate models are not shown on the evidence map. They must be removed from the grid itself,
# not merely from SPECIES_ORDER: row and column totals count every study in the grid, so dropping a
# column alone leaves visible cells that do not sum to the total printed beside them.
OFF_MAP_SPECIES = {"drosophila", "c-elegans", "hamster"}
AREA_ORDER = ["oncology", "neurology", "immunology/inflammation", "cross-cutting toxicology",
              "cardiovascular", "liver/GI", "infectious disease", "pain/musculoskeletal",
              "psychiatry/addiction", "metabolic/endocrine", "ophthalmology", "respiratory",
              "reproductive/developmental", "hematology", "renal", "dermatology", "other"]


def species_of(r):
    """Every species column this result belongs in (A25).

    A result whose own species_as_reported label names several animals belongs in each of them: a
    record reading "dogs, rats, mice, rabbits and monkeys" is evidence about five species, and
    resolving it to none put it nowhere. Only the label is used - species mentioned in a title or a
    statement are passing prose, not the result's subject. Returns an empty set when no species is
    named, which keeps the result off the map entirely.
    """
    pre = r.get("_species")
    if pre is not None:
        return set(pre)
    one = sp_display(r)
    if one not in NON_SPECIES:
        return set() if one in OFF_MAP_SPECIES else {one}
    named = animals_named(str(r.get("species_as_reported") or ""))
    if len(named) < 2:
        return set()
    cols = {_col(species_column(SPECIES_FIX.get(a, a), r.get("model_type"))) for a in named}
    return cols - OFF_MAP_SPECIES


def sp_label(r):
    """What a single row calls itself: one species, or the several it names."""
    cols = sorted(species_of(r))
    return ", ".join(cols) if cols else A("species", "none", "no species named")


DOGCAT = {"laboratory-dog": "laboratory dog", "companion-dog": "companion dog",
          "laboratory-cat": "laboratory cat", "companion-cat": "companion cat",
          "pig-minipig": "pig", "sheep-goat": "sheep/goat",
          "non-human-primate": "non-human primate", "other-rodent": "guinea pig"}


def _col(name):
    return DOGCAT.get(name, name)


def sp_display(r):
    """Species column for display: frozen vocabulary, with unresolved labels kept visible."""
    s = r.get("species")
    if s in UNRESOLVED:
        s = recovered_species(r)
        if not s:
            return "not resolved"
    if s == "other-species":
        rep = str(r.get("species_as_reported") or "")
        for pat, to in OTHER_FIX.items():
            if re.search(pat, rep, re.I):
                s = to
                break
    return _col(species_column(SPECIES_FIX.get(s, s), r.get("model_type")))


# The records store a British spelling for one area. Normalize it BEFORE the vocabulary test:
# mapping afterwards produced a value that was no longer in AREA_ORDER, so the heatmap dropped the
# row and its 10 studies without a word. A display map has to run before whatever matches on it.
# Display names for condition areas, covering both vocabularies: the results records and the
# indication rules used by the pair and candidate pages. A hyphen joining one compound idea becomes
# a space ("infectious disease"); a hyphen joining two different things becomes a slash
# ("immunology/inflammation"). Applied BEFORE the AREA_ORDER test, never after - mapping afterwards
# produced a value no longer in the vocabulary and silently dropped a row from the map.
AREA_FIX = {
    "haematology": "hematology",
    "immunology-inflammation": "immunology/inflammation",
    "psychiatry-addiction": "psychiatry/addiction",
    "pain-musculoskeletal": "pain/musculoskeletal",
    "metabolic-endocrine": "metabolic/endocrine",
    "reproductive-developmental": "reproductive/developmental",
    "liver-gi": "liver/GI",
    "infectious-disease": "infectious disease",
    "cross-cutting-toxicology": "cross-cutting toxicology",
    # vocabularies used by the pair and candidate pages only
    "infectious-parasitic": "infectious/parasitic",
    "anaesthesia-analgesia": "anesthesia/analgesia",
    "dental-oral": "dental/oral",
    "nutrition-supportive": "nutrition/supportive",
    "behaviour": "behavior",
}


def area_name(a):
    """Display name for a condition area, from either vocabulary."""
    return AREA_FIX.get(a, a)


# 21 of the 419 studies are keyed by an OpenAlex work id rather than a PubMed id, because that is
# where retrieval found them. Building "pubmed.ncbi.nlm.nih.gov/<id>/" from those produced 21 study
# pages linking to a record that does not exist. Route each id to the registry it belongs to.
OPENALEX = {}


def record_link(pid):
    """The registry a study id actually belongs to.

    21 studies are keyed by an OpenAlex work id, and building a PubMed URL from those linked to a
    record that does not exist. Resolved through the OpenAlex API (part1/openalex_ids.json): none
    carry a PubMed id, 20 of 21 carry a DOI, so those link to doi.org. openalex.org itself is not
    used as a destination - it serves a bot-protection challenge to automated clients.
    """
    pid = str(pid)
    if pid.isdigit():
        return f"https://pubmed.ncbi.nlm.nih.gov/{pid}/", A("study", "pubmed", "PubMed")
    rec = OPENALEX.get(pid) or {}
    if rec.get("pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{rec['pmid']}/", A("study", "pubmed", "PubMed")
    if rec.get("doi"):
        return f"https://doi.org/{rec['doi']}", A("study", "doi", "DOI")
    return f"https://api.openalex.org/works/{pid}", A("study", "openalex", "OpenAlex record")


def area_display(r):
    a = r.get("disease_area") or "other"
    a = AREA_FIX.get(a, a)
    return a if a in AREA_ORDER else "other"


CSS = """
:root{
  --ink:#15181c; --dim:#5c636c; --faint:#878e97; --line:#e3e6ea; --bg:#fbfaf8; --card:#fff;
  --accent:#1d4e79; --accent-soft:#eef3f8; --ok:#2c6a4e; --no:#8f3a2c; --mid:#866416;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 var(--serif);
  -webkit-font-smoothing:antialiased}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
header.top .in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;flex-wrap:wrap;
  gap:8px 22px;align-items:baseline}
header.top .brand{font-weight:600;color:var(--ink);text-decoration:none;font-size:16px;letter-spacing:-.01em}
header.top nav{font-family:var(--sans);font-size:14px;display:flex;gap:18px;flex-wrap:wrap}
header.top nav a{color:var(--dim);text-decoration:none}
header.top nav a:hover,header.top nav a.on{color:var(--accent)}
header.top nav a.on{font-weight:600}
main{max-width:1180px;margin:0 auto;padding:0 22px 80px}
.wrap{display:grid;grid-template-columns:200px minmax(0,1fr);gap:46px;align-items:start}
.rail{position:sticky;top:64px;font-family:var(--sans);font-size:13.5px;padding-top:34px}
.rail a{display:block;color:var(--dim);text-decoration:none;padding:4px 0 4px 10px;
  border-left:2px solid var(--line);line-height:1.35}
.rail a:hover{color:var(--accent)}
.rail a.on{color:var(--accent);border-left-color:var(--accent);font-weight:600}
.doc{padding-top:34px;min-width:0}
h1{font-size:34px;line-height:1.18;margin:.1em 0 .3em;letter-spacing:-.015em;font-weight:600;
  text-wrap:balance;max-width:34ch}
.page h1{max-width:44ch}
h2{font-size:23px;margin:2.4em 0 .5em;font-weight:600;letter-spacing:-.01em;scroll-margin-top:72px}
h3{font-size:18px;margin:1.8em 0 .4em;font-weight:600}
h4{font-size:15px;margin:1.4em 0 .3em;font-weight:600;font-family:var(--sans)}
p,li{max-width:68ch}
p{margin:.75em 0}
ol,ul{max-width:68ch}
li{margin:.3em 0}
.lede{font-size:20px;line-height:1.5;color:#3b424a;max-width:60ch;margin:.6em 0 1em}
.lede p{margin:.35em 0;max-width:none}
.lede p:first-child{margin-top:0}
.dek{font-family:var(--sans);font-size:13px;color:var(--faint);text-transform:uppercase;
  letter-spacing:.08em;margin:0 0 6px}
.dek p{margin:0}
a{color:var(--accent)}
.small{font-size:14.5px;color:var(--dim);font-family:var(--sans);line-height:1.5}
.small p{margin:.4em 0;max-width:72ch}
.small p:first-child{margin-top:0}
code{font-family:var(--mono);font-size:13px;background:#f1f3f5;padding:1px 5px;border-radius:3px}
hr{border:0;border-top:1px solid var(--line);margin:2.6em 0}

.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin:22px 0}
.figs div{background:var(--card);padding:14px 16px}
.figs .n{font-size:27px;font-weight:600;font-family:var(--sans);font-variant-numeric:tabular-nums;
  letter-spacing:-.02em}
.figs .l{font-family:var(--sans);font-size:13px;color:var(--dim);line-height:1.35;margin-top:2px}

table{border-collapse:collapse;width:100%;margin:16px 0;background:var(--card);
  font-family:var(--sans);font-size:14px}
.scroll{overflow-x:auto;margin:16px 0;border:1px solid var(--line);background:var(--card)}
.scroll table{margin:0;border:0}
th,td{border-bottom:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
thead th{background:#f7f8f9;font-weight:600;color:#3b424a;white-space:nowrap;
  border-bottom:1px solid var(--line)}
tbody tr:hover{background:#fafbfc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
caption{caption-side:top;text-align:left;font-family:var(--sans);font-size:13px;color:var(--dim);
  padding:0 0 8px}

.tag{display:inline-block;padding:1px 8px;border-radius:2px;font-size:12.5px;font-family:var(--sans);
  border:1px solid var(--line);white-space:nowrap;color:var(--dim)}
.tag.ok{color:var(--ok);border-color:#c3dbcd;background:#f4f9f6}
.tag.no{color:var(--no);border-color:#e3c4bd;background:#fdf6f4}
.tag.mid{color:var(--mid);border-color:#e4d7a9;background:#fcf9ef}
.tag.ev{color:var(--accent);border-color:#c5d6e4;background:var(--accent-soft);font-weight:500}

.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  padding:14px 18px;margin:22px 0;max-width:72ch}
.note p{margin:.4em 0}
.note p:first-of-type{margin-top:0}
.note .h{font-family:var(--sans);font-size:13px;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;color:var(--accent);margin-bottom:4px}
blockquote{margin:.6em 0;padding:.3em 0 .3em 14px;border-left:2px solid var(--line);color:#3b424a;
  font-size:16px}

.hmwrap{overflow-x:auto;margin:18px 0;border:1px solid var(--line);background:var(--card)}
table.hm{font-size:13px;margin:0;border:0}
table.hm th{font-weight:500;font-size:12.5px;color:var(--dim);background:var(--card);
  border-bottom:1px solid var(--line)}
table.hm thead th{white-space:nowrap;text-align:center;padding:9px 6px;vertical-align:bottom}
table.hm th.rowh{text-align:left;white-space:nowrap;position:sticky;left:0;background:var(--card);
  border-right:1px solid var(--line);color:var(--ink);font-weight:500;z-index:1}
table.hm td{padding:0;border:0;border-bottom:1px solid #f0f2f4;text-align:center}
table.hm td a{display:block;padding:7px 4px;text-decoration:none;font-variant-numeric:tabular-nums;
  font-family:var(--sans);min-width:38px}
table.hm td a sup{font-size:9px;opacity:.75;margin-left:1px}
table.hm td.empty{background:repeating-linear-gradient(45deg,#fcfcfc,#fcfcfc 4px,#f6f7f8 4px,#f6f7f8 8px)}
table.hm td.tot a,table.hm td.tot{background:#f7f8f9;color:var(--dim);font-weight:600}
.legend{display:flex;align-items:center;gap:8px;font-family:var(--sans);font-size:12.5px;
  color:var(--dim);margin:10px 0 0;flex-wrap:wrap}
.legend .ramp{display:flex}
.legend .ramp i{width:22px;height:11px;display:block}

.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 10px;
  font-family:var(--sans);font-size:14px}
.controls input[type=search]{flex:1 1 260px;min-width:200px;padding:8px 11px;border:1px solid var(--line);
  border-radius:3px;font:inherit;background:var(--card);color:var(--ink)}
.controls select{padding:7px 9px;border:1px solid var(--line);border-radius:3px;font:inherit;
  background:var(--card);color:var(--ink)}
.controls input[type=search]:focus,.controls select:focus{outline:2px solid var(--accent);outline-offset:1px}
.count{font-family:var(--sans);font-size:13.5px;color:var(--dim);margin-left:auto}
.psz{font-family:var(--sans);font-size:13.5px;color:var(--dim);display:flex;align-items:center;gap:6px}
.psz select{padding:6px 8px;border:1px solid var(--line);border-radius:3px;font:inherit;
  background:var(--card);color:var(--ink)}
.pager{display:flex;align-items:center;gap:10px;justify-content:flex-end;margin:10px 0 0;
  font-family:var(--sans);font-size:13.5px;color:var(--dim)}
.pager button{border:1px solid var(--line);background:var(--card);color:var(--accent);
  border-radius:3px;cursor:pointer;font-size:16px;line-height:1;padding:4px 12px}
.pager button:disabled{color:#c2c8cf;cursor:default}
.reset{font-family:var(--sans);font-size:13.5px;background:none;border:0;color:var(--accent);
  cursor:pointer;padding:6px 2px}
th.s{cursor:pointer;user-select:none}
th.s:hover{color:var(--accent)}
th.s::after{content:"";display:inline-block;width:0;height:0;margin-left:5px;vertical-align:middle;
  border-left:4px solid transparent;border-right:4px solid transparent;border-top:4px solid #c2c8cf}
th.s.asc::after{border-top:0;border-bottom:4px solid var(--accent)}
th.s.desc::after{border-top:4px solid var(--accent)}
td .stmt{font-family:var(--serif);font-size:15px;line-height:1.45;display:block;max-width:60ch}
td .src{color:var(--dim);font-size:12.5px}
.empty-state{padding:26px;text-align:center;color:var(--dim);font-family:var(--sans);font-size:14px}
tr.row{cursor:pointer}
tr.row.open{background:var(--accent-soft)}
tr.det>td{background:#fafbfc;padding:0}
.pd{padding:14px 18px;max-width:82ch}
.pd h4{margin:.9em 0 .2em;font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--accent);font-family:var(--sans)}
.pd h4:first-child{margin-top:0}
.pd p{margin:.25em 0;font-family:var(--serif);font-size:15px;line-height:1.5;max-width:76ch}
.pd p.src{font-family:var(--sans);font-size:13px;color:var(--dim)}
.hint{font-family:var(--sans);font-size:13.5px;color:var(--dim);margin:0 0 4px}

footer{border-top:1px solid var(--line);margin-top:60px;padding:22px;color:var(--faint);
  font-family:var(--sans);font-size:13px}
footer .in{max-width:1180px;margin:0 auto}
/* charts: horizontal bars, area cards, funnel. One hue, same tokens as everything else. */
figure.chart{margin:20px 0;padding:0}
figure.chart figcaption{font-family:var(--sans);font-size:13px;color:var(--dim);margin:0 0 10px}
.bars{display:flex;flex-direction:column;gap:3px}
.brow{display:grid;grid-template-columns:minmax(90px,190px) minmax(0,1fr) 52px;gap:10px;
  align-items:center;font-family:var(--sans);font-size:13.5px}
.brow .bl{color:var(--ink);line-height:1.3}
.brow .bt{background:#f0f2f4;height:17px;display:block;border-radius:1px;overflow:hidden}
.brow .bt i{display:block;height:100%;background:var(--accent)}
.brow .bt i.alt{background:#8aa8c0}
.brow .bn{text-align:right;font-variant-numeric:tabular-nums;color:var(--dim)}
.cnote{font-family:var(--sans);font-size:12.5px;color:var(--dim);margin:10px 0 0;max-width:72ch}
.sankeywrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);padding:10px 12px}
.sankeywrap svg{display:block;min-width:620px;width:100%;height:auto}
text.sl{font-family:var(--sans);font-size:11px;fill:var(--dim);paint-order:stroke;
  stroke:var(--card);stroke-width:3px;stroke-linejoin:round}
.pres{display:grid;gap:8px;margin:18px 0}
.pres .p{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  padding:11px 14px;font-family:var(--sans);font-size:13.5px}
.pres .p b{font-size:19px;font-variant-numeric:tabular-nums;margin-right:8px;color:var(--accent)}
.pres .p.none{border-left-color:var(--mid)}
.strata{margin:18px 0}
.srow{display:grid;grid-template-columns:minmax(150px,2fr) minmax(120px,3fr) 130px 68px;gap:14px;
  align-items:center;padding:9px 0;border-bottom:1px solid var(--line);font-family:var(--sans);
  font-size:13.5px}
.srow.sub .sname{padding-left:16px;color:var(--dim)}
.sbar{display:flex;height:16px;background:#f0f2f4;overflow:hidden;border-radius:2px}
.sbar i{display:block;height:100%}
.sbar i.ok{background:var(--accent)}
.sbar i.no{background:var(--no)}
.sbar i.mid{background:var(--mid)}
.sbar i.ind{background:#dde2e7}
.sval{text-align:right;font-variant-numeric:tabular-nums}
.sval .ci{color:var(--dim);font-size:12.5px}
.snum{text-align:right;font-variant-numeric:tabular-nums;color:var(--dim)}
.legend .key{width:11px;height:11px;display:inline-block;margin-right:5px;vertical-align:-1px}
.legend .key.ok{background:var(--accent)}
.legend .key.no{background:var(--no)}
.legend .key.mid{background:var(--mid)}
.legend .key.ind{background:#dde2e7}
.q4{margin:18px 0}
.q4 .figs{margin:14px 0}
table.q4m th{font-weight:500;color:var(--dim);background:var(--card)}
table.q4m td.num{font-variant-numeric:tabular-nums;font-size:15px}
table.q4m td.hi{font-weight:600;color:var(--accent);background:var(--accent-soft)}
tr.hi td{background:#fcf9ef}
.q4s{font-family:var(--sans);font-size:14.5px;color:var(--ink);border-left:3px solid var(--accent);
  padding:8px 0 8px 14px;margin:16px 0;max-width:72ch}

.areas{display:grid;gap:14px;margin:20px 0}
.acard{background:var(--card);border:1px solid var(--line);padding:16px 18px}
.atop{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:baseline;justify-content:space-between}
.atop h3{margin:0;font-size:17px}
.rank{font-family:var(--sans);font-size:12.5px;font-weight:600;color:var(--accent);
  background:var(--accent-soft);padding:3px 9px;border-radius:2px;white-space:nowrap}
.acard .bar{display:flex;height:9px;margin:13px 0 7px;background:var(--line);overflow:hidden}
.acard .bar i{display:block;height:100%}
.acard .bar i.ok{background:var(--accent)}
.acard .bar i.no{background:var(--no)}
.alegend{font-family:var(--sans);font-size:12.5px;color:var(--dim);display:flex;flex-wrap:wrap;
  gap:4px 18px}

.routes{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin:22px 0}
.rcard{background:var(--card);padding:16px 18px}
.rcard h3{margin:0 0 3px;font-size:15px;font-family:var(--sans)}
.rcard p{margin:0;font-family:var(--sans);font-size:13.5px;color:var(--dim);line-height:1.5;
  max-width:72ch}

.funnel{font-family:var(--sans);font-size:13.5px;margin:18px 0;border-left:2px solid var(--line)}
.funnel div{display:flex;justify-content:space-between;gap:18px;padding:7px 0 7px 16px;
  border-bottom:1px solid var(--line)}
.funnel div:last-child{border-bottom:0;font-weight:600;color:var(--accent)}
.funnel span:last-child{font-variant-numeric:tabular-nums;color:var(--dim);white-space:nowrap}
.funnel div:last-child span:last-child{color:var(--accent)}
.chip{display:inline-block;font-family:var(--sans);font-size:11.5px;font-weight:600;padding:1px 7px;
  border-radius:2px;white-space:nowrap;background:var(--accent-soft);color:var(--accent)}
.chip.warn{background:#fcf9ef;color:var(--mid)}

@media (max-width:900px){
  .brow{grid-template-columns:minmax(80px,130px) minmax(0,1fr) 44px;font-size:12.5px}
  .wrap{grid-template-columns:1fr;gap:0}
  .rail{position:static;padding:22px 0 0;display:flex;flex-wrap:wrap;gap:4px 14px;
    border-bottom:1px solid var(--line);padding-bottom:12px}
  .rail a{border-left:0;padding:2px 0}
  .rail a.on{border-left:0}
  body{font-size:16px}
  h1{font-size:28px}
  .lede{font-size:18px}
  /* Six filters stack one per row on a phone and push the data off screen; pair them up. */
  .controls input[type=search]{flex:1 1 100%}
  .controls select{flex:1 1 44%;min-width:0;max-width:100%}
  .count{margin-left:0;flex:1 1 100%}
}
"""

JS = r"""
// Section rail: highlight the section currently in view.
(function () {
  var links = [].slice.call(document.querySelectorAll('.rail a[href^="#"]'));
  if (!links.length) return;
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function mark() {
    var best = 0, top = 90;
    targets.forEach(function (el, i) {
      if (el && el.getBoundingClientRect().top <= top) best = i;
    });
    links.forEach(function (a, i) { a.classList.toggle('on', i === best); });
  }
  window.addEventListener('scroll', mark, { passive: true });
  mark();
})();

// Rows are built as HTML strings, so every value taken from a paper is escaped here. The JSON
// keeps the original text: a finding reading "p < 0.05" must still be findable by searching for it.
window.esc = function (s) {
  return String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
};

// Data browser: search, sort, filter over a table's rows. Rows are embedded in the page as JSON
// so the page works offline and from a local file, with no request and no library.
window.initTable = function (cfg) {
  var data = JSON.parse(document.getElementById(cfg.dataId).textContent);
  var root = document.getElementById(cfg.id);
  var search = root.querySelector('input[type=search]');
  // Only selects carrying a data-key are filters. The page-size control is a select too, and
  // picking up every select swept it into matches(), where r[undefined] !== '10' rejected
  // every row and rendered an empty table.
  var selects = [].slice.call(root.querySelectorAll('select[data-key]'));
  var tbody = root.querySelector('tbody');
  var count = root.querySelector('.count');
  var reset = root.querySelector('.reset');
  var heads = [].slice.call(root.querySelectorAll('th.s'));
  var psize = root.querySelector('.psize');
  var pager = root.querySelector('.pager');
  var pinfo = root.querySelector('.pinfo');
  var prevB = root.querySelector('.prev');
  var nextB = root.querySelector('.next');
  var sort = { key: null, dir: 1 };
  var page = 1;

  selects.forEach(function (sel) {
    var key = sel.dataset.key;
    var vals = {};
    // A result can belong to several species, so a filter value may be an array. Count each
    // membership separately, or the dropdown lists "mouse, zebrafish" as its own option and the
    // "mouse" option silently misses those rows.
    data.forEach(function (r) {
      var v = r[key];
      if (Array.isArray(v)) { v.forEach(function (x) { vals[x] = (vals[x] || 0) + 1; }); }
      else if (v) { vals[v] = (vals[v] || 0) + 1; }
    });
    Object.keys(vals).sort().forEach(function (v) {
      var o = document.createElement('option');
      o.value = v; o.textContent = v + ' (' + vals[v] + ')';
      sel.appendChild(o);
    });
  });

  var params = new URLSearchParams(location.search);
  if (params.get('q')) search.value = params.get('q');
  selects.forEach(function (sel) {
    var v = params.get(sel.dataset.key);
    if (v) sel.value = v;
  });

  function matches(r) {
    for (var i = 0; i < selects.length; i++) {
      var sel = selects[i];
      var rv = r[sel.dataset.key];
      if (sel.value) {
        if (Array.isArray(rv)) { if (rv.indexOf(sel.value) < 0) return false; }
        else if (rv !== sel.value) return false;
      }
    }
    var q = search.value.trim().toLowerCase();
    if (!q) return true;
    var terms = q.split(/\s+/);
    for (var j = 0; j < terms.length; j++) {
      var term = terms[j], hit = false;
      for (var k = 0; k < cfg.searchKeys.length; k++) {
        var v = r[cfg.searchKeys[k]];
        if (v && String(v).toLowerCase().indexOf(term) >= 0) { hit = true; break; }
      }
      if (!hit) return false;
    }
    return true;
  }

  function render() {
    var rows = data.filter(matches);
    if (sort.key) {
      rows = rows.slice().sort(function (a, b) {
        var x = a[sort.key], y = b[sort.key];
        if (x === null || x === undefined || x === '') return 1;
        if (y === null || y === undefined || y === '') return -1;
        if (typeof x === 'number' && typeof y === 'number') return (x - y) * sort.dir;
        return String(x).localeCompare(String(y)) * sort.dir;
      });
    }
    // Slice the DATA, never the DOM: rows carrying an evidence panel emit two <tr> each, so
    // slicing rendered rows would separate a row from its own detail panel.
    var total = rows.length;
    var size = (psize && psize.value === 'all') ? (total || 1) : parseInt((psize && psize.value) || '10', 10);
    var pages = Math.max(1, Math.ceil(total / size));
    if (page > pages) page = pages;
    var from = (page - 1) * size;
    var shown = rows.slice(from, from + size);
    tbody.innerHTML = total
      ? shown.map(cfg.row).join('')
      : '<tr><td class="empty-state" colspan="' + cfg.cols + '">'
        + (root.dataset.empty || 'Nothing matches those filters.') + '</td></tr>';
    count.textContent = total
      ? (from + 1).toLocaleString() + '\u2013' + Math.min(from + size, total).toLocaleString()
        + ' of ' + total.toLocaleString() + ' ' + cfg.noun
        + (total === data.length ? '' : ' (filtered from ' + data.length.toLocaleString() + ')')
      : '0 ' + cfg.noun;
    if (pager) {
      pager.hidden = pages < 2;
      pinfo.textContent = 'Page ' + page + ' of ' + pages.toLocaleString();
      prevB.disabled = page <= 1;
      nextB.disabled = page >= pages;
    }
    var p = new URLSearchParams();
    if (search.value.trim()) p.set('q', search.value.trim());
    selects.forEach(function (sel) { if (sel.value) p.set(sel.dataset.key, sel.value); });
    history.replaceState(null, '', p.toString() ? '?' + p : location.pathname);
  }

  // Rows that carry an evidence panel open on click. The panel is a sibling row emitted by the
  // row renderer, so filtering and sorting move it with its row.
  tbody.addEventListener('click', function (ev) {
    if (ev.target.closest('a')) return;
    var tr = ev.target.closest('tr.row');
    if (!tr) return;
    var det = tr.nextElementSibling;
    if (det && det.classList.contains('det')) {
      det.hidden = !det.hidden;
      tr.classList.toggle('open', !det.hidden);
    }
  });

  var timer;
  search.addEventListener('input', function () {
    clearTimeout(timer); timer = setTimeout(function () { page = 1; render(); }, 120);
  });
  selects.forEach(function (sel) {
    sel.addEventListener('change', function () { page = 1; render(); });
  });
  if (psize) psize.addEventListener('change', function () { page = 1; render(); });
  if (prevB) prevB.addEventListener('click', function () { if (page > 1) { page--; render(); } });
  if (nextB) nextB.addEventListener('click', function () { page++; render(); });
  reset.addEventListener('click', function () {
    search.value = ''; selects.forEach(function (s) { s.value = ''; });
    sort = { key: null, dir: 1 };
    page = 1;
    if (psize) psize.value = '10';
    heads.forEach(function (h) { h.classList.remove('asc', 'desc'); });
    render();
  });
  heads.forEach(function (th) {
    th.addEventListener('click', function () {
      var key = th.dataset.sort;
      sort = { key: key, dir: sort.key === key ? -sort.dir : 1 };
      page = 1;
      heads.forEach(function (h) { h.classList.remove('asc', 'desc'); });
      th.classList.add(sort.dir === 1 ? 'asc' : 'desc');
      render();
    });
  });
  render();
};
"""

NAV = [("index.html", "Report"), ("results.html", "Detailed evidence"), ("pairs.html", "Drug pairs"),
       ("caninisation.html", "Program selection"), ("spotcheck.html", "Verify")]


def asset_url(up, name):
    """Asset URL carrying a hash of its own contents.

    GitHub Pages serves assets/site.css with a short max-age and no version in the path, so a
    browser holding the previous build's stylesheet keeps using it after a deploy: a CSS fix then
    appears to have done nothing until the cache expires, and the page renders with old rules
    against new markup. Hashing the contents into the query string means a changed file is a
    changed URL, and an unchanged one stays cached.
    """
    import hashlib
    src = CSS if name.endswith(".css") else JS
    return f"{up}assets/{name}?v={hashlib.sha1(src.encode()).hexdigest()[:8]}"


def page(fname, title, body, depth=0, rail=None, cls="page"):
    up = "../" * depth
    here = fname if depth == 0 else ""
    nav = "".join(f'<a href="{up}{h}"{" class=\"on\"" if h == here else ""}>{lab}</a>' for h, lab in NAV)
    if rail:
        railhtml = '<div class="rail">' + "".join(
            f'<a href="#{i}">{e(lab)}</a>' for i, lab in rail) + "</div>"
        body = f'<div class="wrap">{railhtml}<div class="doc">{body}</div></div>'
    else:
        body = f'<div class="doc {cls}">{body}</div>'
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<link rel="stylesheet" href="{asset_url(up, 'site.css')}">
</head><body>
<header class="top"><div class="in"><a class="brand" href="{up}index.html">Animal-model concordance</a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="in">A systematic review of studies comparing findings in live non-human animals
with the corresponding findings in humans. Protocol frozen before data collection; every figure
reproducible from the public data and code. Built {today()}.</div></footer>
<script src="{asset_url(up, 'site.js')}" defer></script></body></html>"""
    p = os.path.join(OUT, fname)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(doc)


PATH_RE = re.compile(r"\s*\(?`[^`]*(?:/|\.(?:py|json|md))[^`]*`\)?|\s*\b[\w-]+\.(?:py|json|md)\b|\s*\b(?:analysis|data|site|docs)/[\w./-]+")
PROVENANCE_RE = re.compile(r"^\s*(?:Built|Generated|Computed|Cost)\b", re.I)


def strip_working_notes(src):
    """Remove build provenance and file paths from a pipeline report, and unwrap its hard wrapping.

    The reports are working records: they name the script that wrote them and the files they read.
    That provenance belongs in the repository, not on the page.
    """
    def clean(s):
        s = PATH_RE.sub("", s)
        s = s.replace("**F1 statement:**", "**In plain terms:**").replace(" (draft)", "")
        s = re.sub(r"[;,]\s*\)", ")", s)
        s = re.sub(r"\(\s*[;,]?\s*\)", "", s)
        return re.sub(r" {2,}", " ", s).replace(" .", ".").rstrip()
    out, para = [], []
    def flush():
        if para:
            out.append(" ".join(para)); para.clear()
    for ln in src.splitlines():
        if (PROVENANCE_RE.match(ln) or "{'" in ln or ln.startswith("**Not yet produced")
                or ln.startswith("# ") or ln.startswith("Confusion (")):
            continue
        s = clean(ln.rstrip())
        if not s.strip() or s.lstrip().startswith(("#", "|", "- ", "* ")):
            flush(); out.append(s)
        else:
            para.append(s.strip())
    flush()
    return "\n".join(out)


def report_md(path):
    """A pipeline report, cleaned and rendered."""
    return render(strip_working_notes(open(path).read() if os.path.exists(path) else ""))[0]


SLUG = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
HEAD_META = re.compile(r"\s*\{#([^}|]+)(?:\|([^}]+))?\}\s*$")


def inline(x):
    """Markdown inline: escaping first, then bold, italic, code, links."""
    x = e(x)
    x = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", x)
    x = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", x)
    x = re.sub(r"`(.+?)`", r"<code>\1</code>", x)
    x = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', x)
    return x


def render(src):
    """Render the markdown subset used by the content files and the pipeline reports.

    Returns (html, sections) where sections are the (id, rail label) pairs of the h2 headings, so
    the report's rail follows whatever the writer puts in the file.
    """
    out, sections, rows = [], [], []
    listtag, box = None, None

    def flush_table():
        nonlocal rows
        if not rows:
            return
        head, body = rows[0], [r for r in rows[1:] if not set(r) <= set("-| :")]
        cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
        out.append('<div class="scroll"><table><thead><tr>'
                   + "".join(f"<th>{inline(c)}</th>" for c in cells(head)) + "</tr></thead><tbody>")
        for r in body:
            out.append("<tr>" + "".join(
                f'<td{" class=\"num\"" if i and re.match(r"^[\d.,%–\-() ]+$", c) else ""}>{inline(c)}</td>'
                for i, c in enumerate(cells(r))) + "</tr>")
        out.append("</tbody></table></div>")
        rows = []

    def close_list():
        nonlocal listtag
        if listtag:
            out.append(f"</{listtag}>"); listtag = None

    # Each line is passed through inline() separately, so a markdown link wrapped across a line
    # break never matched: the first line leaves "[" unclosed and the second carries an orphan
    # "](url)". Join lines while a link bracket is still open, before anything else looks at them.
    joined, raw_lines, i = [], src.splitlines(), 0
    while i < len(raw_lines):
        ln = raw_lines[i]
        while (ln.count("[") > ln.count("]") or ln.rstrip().endswith("](")) and i + 1 < len(raw_lines):
            i += 1
            ln = ln.rstrip() + " " + raw_lines[i].lstrip()
        joined.append(ln)
        i += 1

    for line in joined:
        if line.startswith("|"):
            rows.append(line); continue
        flush_table()
        s = line.strip()

        if s.startswith(":::"):
            close_list()
            rest = s[3:].strip()
            if box and not rest:
                out.append("</div>"); box = None
            elif rest:
                kind, _, title = rest.partition(" ")
                box = kind
                if kind == "note":
                    out.append('<div class="note">'
                               + (f'<div class="h">{inline(title)}</div>' if title.strip() else ""))
                else:
                    out.append(f'<div class="{e(kind)}">')
            continue

        if not s:
            close_list(); continue

        if s.startswith("#"):
            close_list()
            n = len(s) - len(s.lstrip("#"))
            text = s.lstrip("# ")
            hid, label = "", ""
            m = HEAD_META.search(text)
            if m:
                hid, label = m.group(1), (m.group(2) or "")
                text = HEAD_META.sub("", text)
            if n == 2:
                hid = hid or SLUG(text)
                sections.append((hid, label or text))
                out.append(f'<h2 id="{e(hid)}">{inline(text)}</h2>')
            else:
                idattr = f' id="{e(hid)}"' if hid else ""
                out.append(f"<h{min(n,4)}{idattr}>{inline(text)}</h{min(n,4)}>")
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            if listtag != "ol":
                close_list(); out.append("<ol>"); listtag = "ol"
            out.append(f"<li>{inline(m.group(2))}</li>"); continue
        if s.startswith(("- ", "* ")):
            if listtag != "ul":
                close_list(); out.append("<ul>"); listtag = "ul"
            out.append(f"<li>{inline(s[2:])}</li>"); continue

        if listtag:
            # a wrapped continuation line inside a list item
            out[-1] = out[-1][:-5] + " " + inline(s) + "</li>"
            continue
        if out and out[-1].startswith("<p>") and out[-1].endswith("</p>"):
            out[-1] = out[-1][:-4] + " " + inline(s) + "</p>"
        else:
            out.append(f"<p>{inline(s)}</p>")

    flush_table(); close_list()
    if box:
        out.append("</div>")
    return "\n".join(out), sections


def indication_area(rules, indication):
    """Condition area for a veterinary indication (amendment A13). First matching rule wins."""
    s = (indication or "").lower()
    for r in rules:
        if re.search(r["pattern"], s):
            return r["area"]
    return "other"


def load_artifacts():
    """The wording inside the generated artifacts, from content/artifacts.md.

    Sections are "## name"; within a section each line is "key :: text". Missing keys fall back to
    the caller's default, so an edit that removes a line degrades to the built-in wording rather
    than to a blank.
    """
    art, section = {}, None
    path = os.path.join(CONTENT, "artifacts.md")
    if not os.path.exists(path):
        return art
    for line in open(path):
        s = line.strip()
        if s.startswith("## "):
            section = s[3:].strip(); art[section] = {}
        elif section and "::" in s and not s.startswith("#"):
            k, _, v = s.partition("::")
            art[section][k.strip()] = v.strip()
    return art


ART = {}
def A(section, key, default=""):
    return ART.get(section, {}).get(key, default)


def compose(name, scalars, blocks):
    """Read a content file, fill in its tokens, and render it."""
    src = open(os.path.join(CONTENT, name)).read()
    src = re.sub(r"\{\{(\w+)\}\}", lambda m: str(scalars.get(m.group(1), m.group(0))), src)
    parts, buf = [], []
    for line in src.splitlines():
        key = line.strip()[2:-2] if line.strip().startswith("{{") and line.strip().endswith("}}") else None
        if key and key in blocks:
            parts.append(("md", "\n".join(buf))); buf = []
            parts.append(("html", blocks[key]))
        else:
            buf.append(line)
    parts.append(("md", "\n".join(buf)))
    html_out, sections, title = [], [], ""
    for kind, chunk in parts:
        if kind == "html":
            html_out.append(chunk)
        else:
            h, secs = render(chunk)
            html_out.append(h); sections += secs
            m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
            if m and not title:
                title = re.sub(r"<[^>]+>", "", m.group(1))
    return "\n".join(html_out), sections, title


def dir_label(d):
    return A("directions", d, DIR_LABEL.get(d, d or "—"))


def dirtag(d):
    return f'<span class="tag {DIR_CLASS.get(d, "")}">{e(dir_label(d))}</span>'


def figures_block(pairs):
    return '<div class="figs">' + "".join(
        f'<div><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in pairs) + "</div>"


def ramp(ratio):
    """Single-hue navy ramp, square-root scaled: the median cell holds 2 studies and the largest
    holds 67, so a linear ramp would render one dark square and a hundred white ones."""
    a, b = (238, 243, 248), (29, 78, 121)
    c = [round(a[i] + (b[i] - a[i]) * ratio) for i in range(3)]
    return f"rgb({c[0]},{c[1]},{c[2]})", ("#fff" if ratio > 0.55 else "#15181c")


LEVEL_RANK = {"A-outcome-concordance": 0, "B-toxicity-safety-concordance": 1,
              "C-biological-similarity": 2}


def collapse_quotes(fin):
    """One finding per sentence (A29).

    The extractor emits one row per reported value, so a sentence reading "identity rates ranged
    from 83.8% to 94.3%" becomes two rows and a paper reporting one analysis gene by gene becomes
    one row per gene. Those rows are not separate observations, and counting them as results
    overstates how much the review rests on. The unit here is the quoted sentence.

    Collapsing must not silently pick a winner where members disagree: direction becomes "mixed"
    rather than the first row's verdict, species are unioned, and the strongest level is kept. A
    row carrying no quote is never merged - without a sentence to group on, every quote-less row
    in a study would otherwise fuse into one.

    This deliberately stops at the sentence. Grouping instead by study, species and area would
    merge findings that are genuinely distinct - separate gene-overlap counts for MEF2C and MEF2A,
    or a sensitivity and a specificity from the same screen - and lose real evidence to tidy a
    presentation problem.
    """
    groups = collections.OrderedDict()
    for i, r in enumerate(fin):
        q = (r.get("quote") or "").strip()
        groups.setdefault((r["pmid"], q) if q else ("", i), []).append(r)
    out = []
    for rs in groups.values():
        rep = dict(rs[0])
        if len(rs) > 1:
            dirs = {r.get("direction") for r in rs}
            rep["direction"] = next(iter(dirs)) if len(dirs) == 1 else "mixed"
            rep["level"] = min((r["level"] for r in rs),
                               key=lambda l: LEVEL_RANK.get(l, 9))
            rep["disease_area"] = collections.Counter(
                r.get("disease_area") for r in rs).most_common(1)[0][0]
            sp = set()
            for r in rs:
                sp |= species_of(r)
            rep["_species"] = sorted(sp)
            vals = [r["value"] for r in rs if isinstance(r.get("value"), (int, float))]
            if vals:
                unit = "" if rep.get("unit") in (None, "none") else f" {rep['unit']}"
                lo, hi = min(vals), max(vals)
                rep["_value_display"] = f"{lo:g}{unit}" if lo == hi else f"{lo:g}\u2013{hi:g}{unit}"
                rep["value"] = lo
        rep["_n_rows"] = len(rs)
        out.append(rep)
    return out


def heatmap(fin):
    grid = collections.defaultdict(lambda: {"s": set(), "lv": set()})
    for r in fin:
        for col in species_of(r):
            g = grid[(area_display(r), col)]
            g["s"].add(r["pmid"]); g["lv"].add((r["level"] or "?")[:1])
    areas = [a for a in AREA_ORDER if any(k[0] == a for k in grid)]
    cols = [c for c in SPECIES_ORDER if any(k[1] == c for k in grid)]
    mx = max(len(g["s"]) for g in grid.values())
    rowtot = {a: len({p for (aa, _), g in grid.items() if aa == a for p in g["s"]}) for a in areas}
    coltot = {c: len({p for (_, cc), g in grid.items() if cc == c for p in g["s"]}) for c in cols}

    h = ['<div class="hmwrap"><table class="hm"><thead><tr><th class="rowh">'
         f'{e(A("heatmap", "row_header", "disease area"))}</th>']
    h += [f"<th>{e(c)}</th>" for c in cols]
    h.append(f'<th class="tot">{e(A("heatmap", "total", "all"))}</th></tr></thead><tbody>')
    for a in areas:
        h.append(f'<tr><th class="rowh">{e(a)}</th>')
        for c in cols:
            g = grid.get((a, c))
            if not g:
                h.append('<td class="empty"></td>'); continue
            n = len(g["s"])
            bg, fg = ramp((n / mx) ** 0.5)
            lv = min(g["lv"])
            ttl = (A("heatmap", "cell_title", "{{area}} · {{species}}: {{n}} studies, highest "
                                              "evidence level {{level}}")
                   .replace("{{area}}", a).replace("{{species}}", c)
                   .replace("{{n}}", str(n)).replace("{{level}}", lv))
            h.append(f'<td><a href="results.html?ar={e(a)}&amp;spf={e(c)}" '
                     f'style="background:{bg};color:{fg}" title="{e(ttl)}">{n}<sup>{lv}</sup></a></td>')
        h.append(f'<td class="tot"><a href="results.html?ar={e(a)}">{rowtot[a]}</a></td></tr>')
    h.append('<tr><th class="rowh">all</th>'
             + "".join(f'<td class="tot"><a href="results.html?spf={e(c)}">{coltot[c]}</a></td>' for c in cols)
             + f'<td class="tot">{len({r["pmid"] for r in fin})}</td></tr>')
    h.append("</tbody></table></div>")
    steps = "".join(f'<i style="background:{ramp(i / 5)[0]}"></i>' for i in range(6))
    high = A("heatmap", "legend_high", "more ({{max}} at most)").replace("{{max}}", str(mx))
    h.append(f'<div class="legend"><span>{e(A("heatmap", "legend_low", "fewer studies"))}</span>'
             f'<span class="ramp">{steps}</span><span>{e(high)}</span>'
             f'<span>· {e(A("heatmap", "legend_note", "superscript = highest evidence level in the "
                            "cell · click a cell to see those results"))}</span></div>')
    return "\n".join(h)


def sankey(stages, links, caption="", note="", height=330):
    """Flow diagram. stages: [[(label, value), ...], ...]; links: [[(from_i, to_i, value), ...], ...]
    between consecutive stages. Drawn only over stages where every item is accounted for, so the
    ribbon widths mean what they look like they mean."""
    W, NODE, GAP, RIGHT = 780, 13, 9, 196
    mx = max(sum(v for _, v in s) for s in stages) or 1
    ngap = max(len(s) for s in stages) - 1
    scale = (height - ngap * GAP) / mx
    span = W - NODE - RIGHT
    xs = [round(i * span / max(len(stages) - 1, 1)) for i in range(len(stages))]
    pos = []
    for s in stages:
        y = (height - (sum(v for _, v in s) * scale + (len(s) - 1) * GAP)) / 2
        row = []
        for lab, v in s:
            h = max(v * scale, 1.5)
            row.append({"lab": lab, "v": v, "y": y, "h": h})
            y += h + GAP
        pos.append(row)
    out = ['<figure class="chart">']
    if caption:
        out.append(f"<figcaption>{e(caption)}</figcaption>")
    out.append(f'<div class="sankeywrap"><svg viewBox="0 0 {W} {height}" '
               f'preserveAspectRatio="xMidYMid meet" role="img">')
    so = [[0.0] * len(s) for s in stages]
    do = [[0.0] * len(s) for s in stages]
    for li, lk in enumerate(links):
        for a, b, v in lk:
            h = v * scale
            y1 = pos[li][a]["y"] + so[li][a]; so[li][a] += h
            y2 = pos[li + 1][b]["y"] + do[li + 1][b]; do[li + 1][b] += h
            x1, x2 = xs[li] + NODE, xs[li + 1]
            m = (x1 + x2) / 2
            out.append(f'<path d="M{x1},{y1:.1f} C{m},{y1:.1f} {m},{y2:.1f} {x2},{y2:.1f} '
                       f'L{x2},{y2 + h:.1f} C{m},{y2 + h:.1f} {m},{y1 + h:.1f} {x1},{y1 + h:.1f} Z" '
                       f'fill="var(--accent)" opacity=".16"/>')
    for si, row in enumerate(pos):
        for n in row:
            out.append(f'<rect x="{xs[si]}" y="{n["y"]:.1f}" width="{NODE}" '
                       f'height="{n["h"]:.1f}" fill="var(--accent)" rx="1"/>')
            out.append(f'<text class="sl" x="{xs[si] + NODE + 6}" '
                       f'y="{n["y"] + n["h"] / 2 + 4:.1f}">{e(n["lab"])} · {n["v"]:,}</text>')
    out.append("</svg></div>")
    if note:
        out.append(f'<p class="cnote">{e(note)}</p>')
    out.append("</figure>")
    return "\n".join(out)


PRESENCE_ORDER = [
    ("a companion-animal program works this mechanism", False),
    ("no marketed product, but the mechanism is claimed or was attempted", False),
    ("mechanism unoccupied, but the condition is contested", False),
    ("no program found, but used or studied in dogs or cats", False),
    ("no program, and no veterinary literature found", True),
    ("not classified", True),
]


def cand_presence(counts):
    """What the four presence checks found, as counts. The last two rows are the honest tail."""
    h = ['<div class="pres">']
    for status, muted in PRESENCE_ORDER:
        n = counts.get(status, 0)
        if not n:
            continue
        h.append(f'<div class="p{" none" if muted else ""}"><b>{n}</b>{e(status)}</div>')
    h.append("</div>")
    return "\n".join(h)


def pairs_flow(classified, attrs):
    """799 pairs, by which species got there first and how the evidence came out.

    Drawn because every pair lands in exactly one timing and one verdict, so the ribbon widths are
    complete. The equivalent flow over all 1,949 human programs is NOT drawn: three quarters of
    them fall outside the curated mechanism map, so the chart would render the map's coverage as
    though it were a finding (L96)."""
    TL = {"human-approval-before-veterinary-evidence": "Human approval first",
          "no-us-approval": "No US human approval",
          "human-approval-after-veterinary-evidence": "Veterinary evidence first"}
    VL = ["concordant", "discordant", "mixed", "indeterminate"]
    pairs_t, cross = collections.Counter(), collections.Counter()
    for k, v in classified.items():
        t = TL.get((attrs.get(k) or {}).get("timing"), "Timing unknown")
        verdict = (v.get("judgement") or {}).get("pair")
        if verdict not in VL:
            continue
        pairs_t[t] += 1
        cross[(t, verdict)] += 1
    timings = [t for t in TL.values() if pairs_t.get(t)] + (
        ["Timing unknown"] if pairs_t.get("Timing unknown") else [])
    verdicts = [v for v in VL if any(cross.get((t, v)) for t in timings)]
    total = sum(pairs_t[t] for t in timings)
    stages = [[(A("caninisation", "flow_root", "Classified pairs"), total)],
              [(t, pairs_t[t]) for t in timings],
              [(v, sum(cross.get((t, v), 0) for t in timings)) for v in verdicts]]
    l0 = [(0, i, pairs_t[t]) for i, t in enumerate(timings)]
    l1 = [(i, j, cross[(t, v)]) for i, t in enumerate(timings)
          for j, v in enumerate(verdicts) if cross.get((t, v))]
    return sankey(stages, [l0, l1],
                  A("caninisation", "pairsflow_caption", ""),
                  A("caninisation", "pairsflow_note", ""))


def q4_block(d):
    """Companion animals vs laboratory models, drawn from the numbers d5 computed.

    Previously this piped d5's working draft through the markdown renderer. That draft's "##"
    headings became page-level <h2>s sitting beside Methods and Limitations, its intermediate counts
    arrived as bare bullet lists, and the sensitivity analysis was given the same weight as the
    primary rule while stating the opposite conclusion. Nothing is recomputed here: every figure
    comes from part2/q4_summary.json, written by the same function that writes the report (A22).
    """
    if not d:
        return ""
    rules = {r["rule"]: r for r in d.get("rules", [])}
    p = rules.get("lab_side")
    if not p:
        return ""
    A_ = lambda k, dflt="": A("q4", k, dflt)
    h = ['<div class="q4">']

    # The 2x2, as a labelled matrix rather than a bare contingency table.
    h.append('<figure class="chart"><figcaption>'
             + e(A_("matrix_caption", "Where companion animals and laboratory models agreed with the "
                                      "human outcome, for the {n} pairs where all three sides are "
                                      "positive or negative").replace("{n}", f'{p["n"]}'))
             + "</figcaption>")
    h.append('<div class="scroll"><table class="q4m"><thead><tr>'
             f'<th></th><th>{e(A_("lab_yes", "laboratory matched"))}</th>'
             f'<th>{e(A_("lab_no", "laboratory did not"))}</th></tr></thead><tbody>'
             f'<tr><th>{e(A_("comp_yes", "companion matched"))}</th>'
             f'<td class="num hi">{p["both_matched"]}</td><td class="num">{p["companion_only"]}</td></tr>'
             f'<tr><th>{e(A_("comp_no", "companion did not"))}</th>'
             f'<td class="num">{p["laboratory_only"]}</td><td class="num">{p["neither"]}</td></tr>'
             "</tbody></table></div></figure>")

    # The two rates, then the only comparison that carries information: the discordant corner.
    h.append('<div class="figs">'
             f'<div><div class="n">{p["companion_rate"]:.0%}</div><div class="l">'
             f'{e(A_("rate_comp", "companion animals matched humans"))}</div></div>'
             f'<div><div class="n">{p["laboratory_rate"]:.0%}</div><div class="l">'
             f'{e(A_("rate_lab", "laboratory models matched humans"))}</div></div>'
             f'<div><div class="n">{p["discordant"]}</div><div class="l">'
             f'{e(A_("rate_disc", "pairs where only one agreed"))}</div></div></div>')
    if p.get("companion_share_of_discordant") is not None:
        h.append('<p class="cnote">'
                 + e(A_("disc_note", "Of those, companion animals were right in {b} ({pct}, 95% CI "
                                     "{lo}–{hi}).")
                     .replace("{b}", str(p["companion_only"]))
                     .replace("{pct}", f'{p["companion_share_of_discordant"]:.0%}')
                     .replace("{lo}", f'{p["ci_lo"]:.0%}').replace("{hi}", f'{p["ci_hi"]:.0%}'))
                 + "</p>")
    if p.get("statement"):
        h.append(f'<p class="q4s">{e(p["statement"])}</p>')

    # Breakdown: the human-negative row is the only one that tests prediction, and says so.
    rows = d.get("breakdown") or []
    if rows:
        h.append('<figure class="chart"><figcaption>'
                 + e(A_("breakdown_caption", "Where the comparison is informative")) + "</figcaption>"
                 '<div class="scroll"><table><thead><tr>'
                 f'<th>{e(A_("col_subset", "Subset"))}</th>'
                 f'<th class="num">{e(A_("col_pairs", "Pairs"))}</th>'
                 f'<th class="num">{e(A_("col_comp", "Companion matched"))}</th>'
                 f'<th class="num">{e(A_("col_lab", "Laboratory matched"))}</th></tr></thead><tbody>')
        for r in rows:
            n = r["pairs"]
            pc = f'{r["companion_matched"]}/{n} ({r["companion_matched"] / n:.0%})' if n else "—"
            pl = f'{r["laboratory_matched"]}/{n} ({r["laboratory_matched"] / n:.0%})' if n else "—"
            mark = ' <span class="chip">' + e(A_("tests", "tests prediction")) + "</span>" if r.get("tests_prediction") else ""
            cls = ' class="hi"' if r.get("tests_prediction") else ""
            h.append(f"<tr{cls}><td>{e(r['subset'])}{mark}</td><td class='num'>{n}</td>"
                     f"<td class='num'>{pc}</td><td class='num'>{pl}</td></tr>")
        h.append("</tbody></table></div></figure>")

    s = rules.get("lab_side_unanimous")
    if s and s.get("n"):
        h.append('<p class="cnote">'
                 + e(A_("sensitivity", "Sensitivity, counting a laboratory side only when every study "
                                       "agrees: {n} pairs, companion {c}, laboratory {l}. {st}")
                     .replace("{n}", str(s["n"])).replace("{c}", f'{s["companion_rate"]:.0%}')
                     .replace("{l}", f'{s["laboratory_rate"]:.0%}').replace("{st}", s.get("statement") or ""))
                 + "</p>")
    if d.get("reader"):
        h.append(f'<p class="cnote">{e(A_("reader", "Laboratory side read from abstracts by"))} '
                 f'{e(d["reader"])}.</p>')
    h.append("</div>")
    return "\n".join(h)


def strata_block(d):
    """Drug-pair strata, drawn from the numbers d4 computed.

    The old table put "pairs" and "concordance" in the same row with different denominators: a
    stratum reading 586 pairs and 82% was 152/185, with the 339 indeterminate and 62 mixed excluded
    from the percentage while dominating the row. Each row now shows what the pairs are made of and
    states the denominator the percentage is actually taken over.
    """
    if not d or not d.get("strata"):
        return ""
    A_ = lambda k, dflt="": A("strata", k, dflt)
    SEG = [("concordant", "ok"), ("discordant", "no"), ("mixed", "mid"), ("indeterminate", "ind")]
    h = ['<div class="strata">']
    h.append(f'<p class="cnote">{e(A_("definition", d.get("definition", "")))}</p>')
    for row in d["strata"]:
        name = row["stratum"]
        sub = name.startswith("Primary:") or name.startswith("Primary,")
        n = row["n"] or 1
        bar = "".join(
            f'<i class="{cls}" style="width:{row.get(k, 0) / n * 100:.2f}%" '
            f'title="{row.get(k, 0)} {k}"></i>' for k, cls in SEG)
        call = (f'{row["concordance"]:.0%}' if row.get("concordance") is not None else "—")
        ci = (f' <span class="ci">({row["ci95"][0]:.0%}–{row["ci95"][1]:.0%})</span>'
              if row.get("ci95") and row["ci95"][0] is not None else "")
        of = A_("of", "of {c} that could be called").replace("{c}", str(row.get("classifiable", 0)))
        h.append(
            f'<div class="srow{" sub" if sub else ""}">'
            f'<div class="sname">{e(name)}</div>'
            f'<div class="sbar">{bar}</div>'
            f'<div class="sval"><strong>{call}</strong>{ci}<br><span class="src">{e(of)}</span></div>'
            f'<div class="snum">{row["n"]:,}<br><span class="src">{e(A_("pairs", "pairs"))}</span></div>'
            "</div>")
    h.append('<div class="legend">'
             + "".join(f'<span><i class="key {cls}"></i>{e(A_(k, k))}</span>' for k, cls in SEG)
             + "</div>")
    rel = d.get("reliability")
    if rel:
        h.append('<p class="cnote">'
                 + e(A_("reliability", "Blind re-judgement of {p} random primary pairs by a second "
                                       "model: {a} agreement, Cohen's kappa {k}.")
                     .replace("{p}", str(rel["pairs"])).replace("{a}", f'{rel["agreement"]:.0%}')
                     .replace("{k}", str(rel["kappa"]))) + "</p>")
    h.append("</div>")
    return "\n".join(h)


def hbars(rows, caption="", note="", alt_before=None):
    """Horizontal bar chart. rows are (label, n); alt_before shades the first n bars differently."""
    mx = max([n for _, n in rows] or [1])
    h = ['<figure class="chart">']
    if caption:
        h.append(f"<figcaption>{e(caption)}</figcaption>")
    h.append('<div class="bars">')
    for i, (label, n) in enumerate(rows):
        cls = " alt" if alt_before is not None and i < alt_before else ""
        # A zero-width bar reads as a missing row rather than an empty one, so keep a hairline.
        w = max(n / mx * 100, 0.7) if mx else 0.7
        h.append(f'<div class="brow"><span class="bl">{e(label)}</span>'
                 f'<span class="bt"><i class="{cls.strip()}" style="width:{w:.1f}%"></i></span>'
                 f'<span class="bn">{n:,}</span></div>')
    h.append("</div>")
    if note:
        h.append(f'<p class="cnote">{e(note)}</p>')
    h.append("</figure>")
    return "\n".join(h)


def cand_lag(attrs):
    """How long companion-animal medicine took to adopt each human drug."""
    lags = [v["vet_year"] - v["approval_year"] for v in attrs.values()
            if v.get("vet_year") and v.get("approval_year")]
    buckets = [("Veterinary evidence first", -10**6, -1), ("0–4 years", 0, 4), ("5–9", 5, 9),
               ("10–19", 10, 19), ("20–29", 20, 29), ("30–39", 30, 39), ("40–49", 40, 49),
               ("50 or more", 50, 10**6)]
    rows = [(lab, sum(1 for l in lags if lo <= l <= hi)) for lab, lo, hi in buckets]
    return hbars(rows, A("caninisation", "lag_caption",
                         f"Years between human approval and the veterinary evidence, "
                         f"for the {len(lags)} pairs where both dates are known"),
                 A("caninisation", "lag_note", ""), alt_before=1)


def cand_routes(d):
    """The routes, stated as bases for selection. The per-route counts are deliberately not
    shown here: this section is about what each route *is*, and the counts are in the browser
    below and on the funnel, where a reader can act on them."""
    labels = d.get("route_labels") or {}
    h = ['<div class="routes">']
    for k in ("route1", "route2", "route3"):
        h.append(f'<div class="rcard"><div>'
                 f'<h3>{e(A("caninisation", f"{k}_name", labels.get(k, k)))}</h3>'
                 f'<p>{e(A("caninisation", f"{k}_desc", ""))}</p></div></div>')
    h.append(f'<div class="rcard held"><div>'
             f'<h3>{e(A("caninisation", "watch_name", "Held back"))}</h3>'
             f'<p>{e(A("caninisation", "watch_desc", ""))}</p></div></div>')
    h.append("</div>")
    return "\n".join(h)


def cand_areas(d):
    h = ['<div class="areas">']
    for a in d.get("areas", []):
        ev = a["evidence"]
        det = ev["corresponded"] + ev["did_not"]
        h.append(
            f'<div class="acard"><div class="atop"><h3>{e(area_name(a["area"]))}</h3>'
            f'<span class="rank">{a["candidates"]} '
            f'{e(A("caninisation", "areas_cands", "candidates"))}</span></div>'
            f'<div class="bar"><i class="ok" style="flex:{ev["corresponded"]}"></i>'
            f'<i class="no" style="flex:{ev["did_not"]}"></i></div>'
            f'<div class="alegend">'
            f'<span>{ev["corresponded"]} of {det} '
            f'{e(A("caninisation", "areas_conc", "of dog results corresponded"))}</span>'
            f'<span><strong>{ev["level_A"]} of {ev["results"]}</strong> '
            f'{e(A("caninisation", "areas_levela", "are intervention outcomes"))}</span>'
            f'<span>{ev["studies"]} {e(A("caninisation", "areas_studies", "studies"))}</span>'
            f"</div></div>")
    h.append("</div>")
    return "\n".join(h)


def cand_crowding(d):
    rows = [(c["indication"], c["programs"]) for c in d.get("crowding", [])]
    return hbars(rows, A("caninisation", "crowding_caption", ""),
                 A("caninisation", "crowding_note", ""))


def cand_funnel(d):
    sk, inp = d.get("skipped") or {}, d.get("inputs") or {}
    order = [
        ("no dog evidence for this area", "No dog evidence in the review for that condition area"),
        ("disease dogs do not get", "A disease dogs do not get, or a human-only indication"),
        ("human tumor type dogs do not get", "A human tumor type dogs do not get"),
        ("oncology indication too unspecific to place in a dog",
         "Oncology indication too unspecific to place in a dog"),
        ("dog evidence says biology does not correspond",
         "Dog evidence says the biology does not correspond"),
        ("discontinued over safety or withdrawn", "Discontinued over safety, or withdrawn"),
        ("known species toxicity", "Known toxicity in the target species"),
        ("diagnostic or imaging agent, not a therapeutic", "Diagnostic or imaging agent"),
    ]
    # The gates above are per supplied program; the gates below are per molecule. The dedup step
    # sits between them, and without it the column does not add up.
    h = ['<div class="funnel">',
         f'<div><span>Human programs supplied</span>'
         f'<span>{inp.get("human_programs", 0):,}</span></div>']
    for key, label in order:
        if sk.get(key):
            h.append(f"<div><span>{e(label)}</span><span>−{sk[key]:,}</span></div>")
    if d.get("deduplicated"):
        h.append(f'<div><span>The same molecule listed more than once (biosimilars, repeat '
                 f'listings)</span><span>−{d["deduplicated"]:,}</span></div>')
    held = sk.get("discontinued on clinical performance, or reason not established")
    if held:
        h.append(f'<div><span>Stopped on clinical performance, or the reason could not be '
                 f'established</span><span>−{held:,}</span></div>')
    h.append(f'<div><span>Held as a watch list — no human approval yet</span>'
             f'<span>−{d.get("watch_count", 0):,}</span></div>')
    h.append(f'<div><span>Candidates</span><span>{len(d.get("candidates", [])):,}</span></div></div>')
    return "\n".join(h)


def browser(tid, data_id, rows_json, columns, filters, noun, search_keys, row_js,
            placeholder="", empty="", reset="Reset"):
    """A searchable, sortable table. Rows render client-side from JSON embedded in the page."""
    ph = placeholder or f"Search {noun}…"
    ctl = [f'<div id="{tid}" data-empty="{e(empty or "Nothing matches those filters.")}">'
           '<div class="controls">',
           f'<input type="search" placeholder="{e(ph)}" aria-label="{e(ph)}">']
    for key, label in filters:
        ctl.append(f'<select data-key="{key}" aria-label="{e(label)}"><option value="">{e(label)}: all</option></select>')
    ctl.append(f'<button class="reset" type="button">{e(reset)}</button>'
               f'<label class="psz">{e(A("tables", "rows", "Rows"))} '
               '<select class="psize">'
               '<option>10</option><option>25</option><option>50</option><option>100</option>'
               f'<option value="all">{e(A("tables", "all", "All"))}</option></select></label>'
               '<span class="count"></span></div>')
    ctl.append('<div class="pager"><button class="prev" type="button">&#8249;</button>'
               '<span class="pinfo"></span>'
               '<button class="next" type="button">&#8250;</button></div>')
    ctl.append('<div class="scroll"><table><thead><tr>')
    for c in columns:
        cls = "s" + (" num" if c.get("num") else "")
        ctl.append(f'<th class="{cls}" data-sort="{c["key"]}">{e(c["label"])}</th>')
    ctl.append("</tr></thead><tbody></tbody></table></div></div>")
    ctl.append(f'<script type="application/json" id="{data_id}">{rows_json}</script>')
    # site.js is deferred, so it has not run while this inline script is parsed. DOMContentLoaded
    # fires after every deferred script has executed.
    ctl.append(f"""<script>document.addEventListener("DOMContentLoaded",function(){{
initTable({{id:"{tid}",dataId:"{data_id}",cols:{len(columns)},
noun:"{noun}",searchKeys:{json.dumps(search_keys)},row:{row_js}}});}});</script>""")
    return "\n".join(ctl)


def main():
    global ART, OPENALEX
    ART = load_artifacts()
    OPENALEX = (load("part1/openalex_ids.json") or {}).get("works") or {}
    fin = [r for r in load("part1/final_results.json") if r["status"] == "final"]
    # Amendment A10: model_type decides the companion/laboratory column, and the extractor left it
    # unfilled on dog and cat results across 20 studies, defaulting them all to laboratory. Each
    # study was read and resolved from its own full text; the evidence is in the overrides file.
    mt_over = {k: v for k, v in load("part1/model_type_overrides.json").items() if not k.startswith("_")}
    for r in fin:
        ov = mt_over.get(r["pmid"])
        if ov and r.get("model_type") == "mixed-or-not-stated":
            r["model_type"] = ov["model_type"]
    # Amendment A29: the unit of analysis is the quoted sentence, not the extracted value. This
    # runs after the model_type overrides above, because the companion/laboratory column feeds the
    # species union, and before every count below, so nothing downstream counts split rows.
    fin = collapse_quotes(fin)
    studies = collections.defaultdict(list)
    for r in fin:
        studies[r["pmid"]].append(r)
    n_stud = len(studies)
    by_level = collections.Counter(r["level"] for r in fin)
    by_dir = collections.Counter(r["direction"] for r in fin)
    lvl_dir = collections.defaultdict(collections.Counter)
    for r in fin:
        lvl_dir[r["level"]][r["direction"]] += 1
    unresolved = sum(1 for r in fin if sp_display(r) == "not resolved")

    heads = load("part1/headlines.json")
    adj = load("part1/adjudicated.json")
    manual = {k.rsplit("|", 1)[0] for k in adj if k.endswith("|manual")}
    n_single = sum(1 for r in fin if r["pmid"] in manual)
    n_extracted = sum(len(h.get("items") or []) for h in heads.values())
    # Studies whose full text was read, and the subset judged eligible at that stage. These are two
    # different numbers and the page must not conflate them.
    n_extraction_studies = len(heads)
    n_eligible = sum(1 for h in heads.values() if h.get("eligible"))
    # L84 appears twice in the register (superseded, plus the invalid first run), so count distinct
    # limitation numbers rather than heading lines.
    n_limits = len(set(re.findall(r"^\*\*(L\d+)", open(J("docs", "limitations.md")).read(), re.M)))

    pairs = load("part2/pairs.json")
    attrs = load("part2/pair_attributes.json")
    classified = {k: v for k, v in pairs.items()
                  if (v.get("judgement") or {}).get("pair") in ("concordant", "discordant", "mixed", "indeterminate")}
    # Amendment A9: name and type corrections, each justified in the overrides file from the
    # pair's own veterinary_basis; four pairs are dropped as not drug-and-indication comparisons.
    overrides = {k: v for k, v in load("part2/pair_overrides.json").items() if not k.startswith("_")}
    for key, ov in overrides.items():
        if key not in classified:
            continue
        if ov.get("drop"):
            del classified[key]
        else:
            if ov.get("name"):
                classified[key] = {**classified[key], "ingredient": ov["name"]}
            if ov.get("type"):
                attrs[key] = {**attrs.get(key, {}), "type": ov["type"]}

    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets", "site.css"), "w").write(CSS)
    open(os.path.join(OUT, "assets", "site.js"), "w").write(JS)

    scalars = {"n_results": f"{len(fin):,}", "n_studies": f"{n_stud:,}",
               "n_level_a": f"{by_level['A-outcome-concordance']:,}",
               "n_level_b": f"{by_level['B-toxicity-safety-concordance']:,}",
               "n_level_c": f"{by_level['C-biological-similarity']:,}",
               "n_corresponded": f"{by_dir['animal-corresponded']:,}",
               "n_not_corresponded": f"{by_dir['animal-did-not-correspond']:,}",
               "n_mixed": f"{by_dir['mixed']:,}", "n_unresolved": f"{unresolved:,}",
               "n_no_species": f"{sum(1 for r in fin if not species_of(r)):,}",
               "n_species_results": f"{sum(1 for r in fin if species_of(r)):,}",
               "n_pairs": f"{len(classified):,}", "n_single_reviewer": f"{n_single:,}",
               "n_extracted": f"{n_extracted:,}", "n_extraction_studies": f"{n_extraction_studies:,}",
               "n_eligible": f"{n_eligible:,}",
               "n_limitations": f"{n_limits:,}", "built_date": today(),
               }

    # Program-selection scalars. The timing counts and the median lag come from the pair
    # attributes computed by d4, never recomputed here.
    _timing = collections.Counter(v.get("timing") for v in attrs.values())
    _lags = sorted(v["vet_year"] - v["approval_year"] for v in attrs.values()
                   if v.get("vet_year") and v.get("approval_year"))
    _cand = load("part2/caninisation_candidates.json") or {}
    _rc = _cand.get("route_counts") or {}
    scalars.update({
        "n_human_first": f"{_timing['human-approval-before-veterinary-evidence']:,}",
        "n_vet_first": f"{_timing['human-approval-after-veterinary-evidence']:,}",
        "median_lag": f"{_lags[len(_lags) // 2]:,}" if _lags else "—",
        "n_lag_pairs": f"{len(_lags):,}",
        "n_human_programs": f"{(_cand.get('inputs') or {}).get('human_programs', 0):,}",
        "n_pet_programs": f"{(_cand.get('inputs') or {}).get('pet_programs', 0):,}",
        "n_candidates": f"{len(_cand.get('candidates') or []):,}",
        "n_route1": f"{_rc.get('route1', 0):,}", "n_route2": f"{_rc.get('route2', 0):,}",
        "n_route3": f"{_rc.get('route3', 0):,}",
        "n_watch": f"{_cand.get('watch_count', 0):,}",
        "n_formulary": f"{sum(1 for c in (_cand.get('candidates') or []) if c.get('route') == 'route1' and c.get('in_veterinary_formulary')):,}",
    })
    # Companion-animal presence, candidate-only (A19). The counts in the evidence file span the
    # watch list too, and the page's prose is about candidates.
    _cevf = load("part2/companion_evidence.json") or {}
    _cnames = {c["drug"] for c in (_cand.get("candidates") or [])}
    _pcounts = collections.Counter(v.get("status") for k, v in (_cevf.get("molecules") or {}).items()
                                   if k in _cnames)
    scalars.update({
        "n_occupied": f"{_pcounts.get('a companion-animal program works this mechanism', 0):,}",
        "n_mech_open": f"{_pcounts.get('mechanism unoccupied, but the condition is contested', 0):,}",
        "n_used_no_programme": f"{_pcounts.get('no program found, but used or studied in dogs or cats', 0):,}",
        "n_nothing_found": f"{_pcounts.get('no program, and no veterinary literature found', 0):,}",
        "n_unclassified": f"{_pcounts.get('not classified', 0):,}",
    })

    # ---------------- blocks the writer cannot type by hand ----------------
    lt = [f'<div class="scroll"><table><caption>'
          f'{e(A("level_table", "caption", "Results by evidence level, and how they came out."))}'
          f'</caption><thead><tr><th>{e(A("level_table", "level", "Evidence level"))}</th>'
          f'<th class="num">{e(A("level_table", "studies", "studies"))}</th>'
          f'<th class="num">{e(A("level_table", "results", "results"))}</th>'
          f'<th class="num">{e(A("level_table", "corresponded", "corresponded"))}</th>'
          f'<th class="num">{e(A("level_table", "did_not", "did not"))}</th>'
          f'<th class="num">{e(A("level_table", "mixed", "mixed"))}</th></tr></thead><tbody>']
    for key, letter, label in LEVELS:
        rs = [r for r in fin if r["level"] == key]
        c = lvl_dir[key]
        label = A("level_table", f"label_{letter.lower()}", label)
        lt.append(f"<tr><td><strong>{letter}</strong> — {e(label)}</td>"
                  f"<td class='num'>{len({r['pmid'] for r in rs})}</td><td class='num'>{len(rs):,}</td>"
                  f"<td class='num'>{c['animal-corresponded']:,}</td>"
                  f"<td class='num'>{c['animal-did-not-correspond']}</td>"
                  f"<td class='num'>{c['mixed']}</td></tr>")
    lt.append("</tbody></table></div>")

    blocks = {
        "figures": figures_block([
            (f"{len(fin):,}", A("figures", "n_results", "results kept after checking")),
            (f"{n_stud}", A("figures", "n_studies", "studies")),
            (f"{by_level['A-outcome-concordance']}", A("figures", "n_level_a", "level A · intervention outcomes")),
            (f"{by_level['B-toxicity-safety-concordance']}", A("figures", "n_level_b", "level B · toxicity and safety")),
            (f"{by_level['C-biological-similarity']}", A("figures", "n_level_c", "level C · disease biology"))]),
        "level_table": "\n".join(lt),
        "heatmap": heatmap(fin),
        "pairs_strata": strata_block(load("part2/strata.json")),
        "q4_tables": q4_block(load("part2/q4_summary.json")),
        "recall": report_md(os.path.join(V04, "retrieval", "recall.md")),
    }
    body, sections, title = compose("report.md", scalars, blocks)
    page("index.html", "Animal-model concordance: what the literature reports", body, rail=sections)

    # ---------------- results browser ----------------
    rows = []
    for r in fin:
        val = r.get("_value_display") or ""
        if not val and r.get("value") is not None:
            unit = "" if r.get("unit") in (None, "none") else f" {r['unit']}"
            val = f"{r['value']:g}{unit}" if isinstance(r["value"], (int, float)) else f"{r['value']}{unit}"
        rows.append({"st": (r["statement"] or "").replace("*", ""), "ti": (r.get("title") or "")[:140],
                     "pm": r["pmid"], "y": r.get("year") or 0, "lv": (r["level"] or "?")[:1],
                     "sp": sp_label(r), "spf": sorted(species_of(r)), "ar": area_display(r),
                     "dr": dir_label(r.get("direction")),
                     "dc": DIR_CLASS.get(r.get("direction"), ""), "v": val,
                     "ru": record_link(r["pmid"])[0], "rl": record_link(r["pmid"])[1],
                     "vn": r["value"] if isinstance(r.get("value"), (int, float)) else None})
    row_js = ("""function(r){return '<tr><td><span class="stmt">'+esc(r.st)+'</span></td>'
+'<td>'+r.lv+'</td><td>'+esc(r.sp)+'</td><td>'+esc(r.ar)+'</td>'
+'<td><span class="tag '+r.dc+'">'+r.dr+'</span></td>'
+'<td class="num">'+esc(r.v||'')+'</td>'
+'<td><a href="study/'+encodeURIComponent(r.pm)+'.html">'+esc(r.ti)+'</a><br><span class="src">'
+(r.y||'')+' · <a href="'+esc(r.ru)+'">'+esc(r.rl)+'</a>'
+'</span></td></tr>';}""")
    cols = [{"key": "st", "label": A("results_table", "col_st", "Finding")},
            {"key": "lv", "label": A("results_table", "col_lv", "Level")},
            {"key": "sp", "label": A("results_table", "col_sp", "Species")},
            {"key": "ar", "label": A("results_table", "col_ar", "Disease area")},
            {"key": "dr", "label": A("results_table", "col_dr", "Direction")},
            {"key": "vn", "label": A("results_table", "col_vn", "Value"), "num": True},
            {"key": "ti", "label": A("results_table", "col_ti", "Study")}]
    body, _, title = compose("results.md", scalars, {
        "results_table": browser("results", "resultdata", json.dumps(rows, separators=(",", ":")), cols,
                                 [("lv", A("results_table", "filter_lv", "Level")),
                                  ("spf", A("results_table", "filter_sp", "Species")),
                                  ("ar", A("results_table", "filter_ar", "Disease area")),
                                  ("dr", A("results_table", "filter_dr", "Direction"))],
                                 A("results_table", "noun", "results"), ["st", "ti", "sp", "ar"], row_js,
                                 placeholder=A("results_table", "placeholder", ""),
                                 empty=A("results_table", "empty", ""),
                                 reset=A("results_table", "reset", "Reset"))})
    page("results.html", title or "Results", body)

    # ---------------- pairs browser ----------------
    prow = []
    area_rules = (load("part2/indication_areas.json") or {}).get("rules") or []
    vclass = {"concordant": "ok", "discordant": "no", "mixed": "mid"}
    for k, v in classified.items():
        j, a = v["judgement"], attrs.get(k, {})
        sp = v.get("species")
        # Provenance for the verdict: the veterinary studies read, and the human studies and US
        # labels cited. PMIDs link to PubMed; label keys resolve through this pair's own label set
        # to DailyMed. A few citations arrive as "PMID 12345678", so digits are taken where present.
        labels = v.get("labels") or {}
        cites = []
        for c in (j.get("human_citations") or []):
            c = str(c).strip()
            digits = re.sub(r"\D", "", c)
            if re.fullmatch(r"L\d+", c) and c in labels:
                lab = labels[c]
                cites.append({"k": "label", "t": f"{lab.get('brand') or c} ({lab.get('application') or 'US label'})",
                              "u": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={lab.get('set_id')}"})
            elif len(digits) >= 6:
                cites.append({"k": "pmid", "t": digits, "u": f"https://pubmed.ncbi.nlm.nih.gov/{digits}/"})
        vrecs = [{"t": rec.split(":", 1)[1], "u": f"https://pubmed.ncbi.nlm.nih.gov/{rec.split(':', 1)[1]}/"}
                 for rec in (v.get("records") or []) if rec.startswith("PMID:")]
        prow.append({"ag": v.get("ingredient") or "", "sp": ", ".join(sp) if isinstance(sp, list) else str(sp or ""),
                     "ind": v.get("veterinary_indication") or "",
                     "ar": area_name(indication_area(area_rules, v.get("veterinary_indication"))),
                     "ev": A("pairs_table", f"ev_{j.get('human_top_level') or 'none'}",
                             j.get("human_top_level") or "none"),
                     "vd": j["pair"],
                     "vc": vclass.get(j["pair"], ""), "vet": j.get("veterinary") or "",
                     "hu": j.get("human") or "", "ty": a.get("type") or "", "ti": a.get("timing") or "",
                     "vb": j.get("veterinary_basis") or "", "hb": j.get("human_basis") or "",
                     "cv": j.get("caveats") or "", "tl": j.get("human_top_level") or "",
                     "vr": vrecs, "hc": cites})
    prow.sort(key=lambda r: (r["ag"].lower(), r["ind"].lower()))
    L = {k: A("pairs_table", k, d) for k, d in (
        ("detail_vet", "What the veterinary evidence showed"),
        ("detail_human", "What the human evidence showed"),
        ("detail_caveats", "Caveats"),
        ("detail_vet_records", "Veterinary studies behind this verdict"),
        ("detail_human_records", "Human evidence cited"),
        ("detail_toplevel", "Strongest human evidence found"),
        ("ev_note", ""),
        ("detail_none", "No human evidence was retrieved for this drug and indication."))}
    prow_js = ("""function(r){
var link=function(x){return '<a href="'+x.u+'">'+esc(x.t)+'</a>';};
var L=""" + json.dumps(L) + """;
var det='<div class="pd"><h4>'+L.detail_vet+'</h4><p>'+esc(r.vb)+'</p>'
+(r.vr.length?'<p class="src">'+L.detail_vet_records+': '+r.vr.map(link).join(', ')+'</p>':'')
+'<h4>'+L.detail_human+'</h4><p>'+esc(r.hb)+'</p>'
+(r.hc.length?'<p class="src">'+L.detail_human_records+': '+r.hc.map(link).join(', ')+'</p>'
  :'<p class="src">'+L.detail_none+'</p>')
+(r.ev?'<p class="src">'+L.detail_toplevel+': <span class="tag ev">'+esc(r.ev)+'</span>'
  +(r.tl==='us-approval'&&L.ev_note?' '+esc(L.ev_note):'')+'</p>':'')
+(r.cv?'<h4>'+L.detail_caveats+'</h4><p>'+esc(r.cv)+'</p>':'')+'</div>';
return '<tr class="row"><td><strong>'+esc(r.ag)+'</strong></td><td>'+esc(r.sp)+'</td>'
+'<td>'+esc(r.ind)+'</td><td><span class="tag '+r.vc+'">'+r.vd+'</span></td>'
+'<td>'+esc(r.vet)+'</td><td>'+esc(r.hu)+'</td><td>'+esc(r.ty)+'</td><td>'+esc(r.ti)+'</td></tr>'
+'<tr class="det" hidden><td colspan="8">'+det+'</td></tr>';}""")
    pcols = [{"key": "ag", "label": A("pairs_table", "col_ag", "Drug")},
             {"key": "sp", "label": A("pairs_table", "col_sp", "Species")},
             {"key": "ind", "label": A("pairs_table", "col_ind", "Veterinary indication")},
             {"key": "vd", "label": A("pairs_table", "col_vd", "Verdict")},
             {"key": "vet", "label": A("pairs_table", "col_vet", "Veterinary")},
             {"key": "hu", "label": A("pairs_table", "col_hu", "Human")},
             {"key": "ty", "label": A("pairs_table", "col_ty", "Type")},
             {"key": "ti", "label": A("pairs_table", "col_ti", "Timing")}]
    hint = A("pairs_table", "hint", "")
    body, _, title = compose("pairs.md", scalars, {
        "pairs_flow": pairs_flow(classified, attrs),
        "pairs_table": (f'<p class="hint">{e(hint)}</p>' if hint else "") +
                       browser("pairs", "pairdata", json.dumps(prow, separators=(",", ":")), pcols,
                               [("vd", A("pairs_table", "filter_vd", "Verdict")),
                                ("ar", A("pairs_table", "filter_ar", "Condition area")),
                                ("ev", A("pairs_table", "filter_ev", "Human evidence")),
                                ("sp", A("pairs_table", "filter_sp", "Species")),
                                ("ty", A("pairs_table", "filter_ty", "Type")),
                                ("ti", A("pairs_table", "filter_ti", "Timing"))],
                               A("pairs_table", "noun", "pairs"), ["ag", "ind", "vet", "hu", "vb", "hb"],
                               prow_js, placeholder=A("pairs_table", "placeholder", ""),
                               empty=A("pairs_table", "empty", ""), reset=A("pairs_table", "reset", "Reset"))})
    page("pairs.html", title or "Dog and cat drug pairs", body)

    # ---------------- program selection ----------------
    crow = []
    # Companion-animal presence, established from four named sources rather than from one supplied
    # spreadsheet joined on shared word tokens (A19). Each row carries what every check found, so
    # the page can report absence as "not found by these checks" instead of asserting it.
    _cev = (load("part2/companion_evidence.json") or {}).get("molecules") or {}
    # The watch list is browsable alongside the candidates rather than being a number the page
    # quotes and then hides. It also makes the stage filter mean something: every candidate is
    # approved, so on the candidates alone that control offered a single option.
    for c in (_cand.get("candidates") or []) + (_cand.get("watch") or []):
        ev = c.get("evidence") or {}
        det = ev.get("corresponded", 0) + ev.get("did_not", 0)
        crow.append({
            "dr": c.get("drug") or "", "ing": c.get("ingredient") or "",
            "tg": c.get("target") or "", "ar": area_name(c.get("area") or ""),
            "rt": c.get("route_label") or "", "st": c.get("human_stage") or "",
            "cn": c.get("competitor_count") or 0, "co": c.get("company") or "",
            "ind": c.get("indication") or "", "yr": c.get("first_us_approval"),
            "ev": (f'{ev.get("corresponded", 0)} of {det} dog results corresponded · '
                   f'{ev.get("level_A", 0)} of {ev.get("results", 0)} are intervention outcomes · '
                   f'{ev.get("studies", 0)} studies'),
            "cp": [h.get("drug") for h in (c.get("competitors") or [])][:14],
            "sf": [f'{f.get("effect")}' for f in (c.get("safety_flags") or [])],
            "pr": c.get("precedent") or "", "dn": c.get("discontinuation_note") or "",
            "fm": bool(c.get("in_veterinary_formulary")),
            "vg": bool(c.get("indication_is_vague")),
            "src": c.get("source") or "",
            **(lambda p: {
                "mc": p.get("target_class") or "",
                "mh": p.get("target_holders") if p.get("target_holders") is not None else None,
                "mp": [{"a": x.get("assignee"), "w": x.get("what"), "u": x.get("source"),
                        "p": x.get("publication")} for x in (p.get("target_patents") or [])],
                "mx": [{"a": x.get("company"), "w": x.get("what"), "u": x.get("source"),
                        "p": x.get("program")} for x in (p.get("target_halted") or [])],
                "mn": p.get("target_note") or "",
                "cc": p.get("companion_condition") or "",
                "ch": p.get("condition_holders") or [],
                "cnn": p.get("condition_note") or "",
                "vl": (p.get("vet_literature") or {}).get("hits"),
                "vc": (p.get("vet_literature") or {}).get("clinical"),
                "vp": (p.get("vet_literature") or {}).get("pmids") or [],
                "pc": p.get("pair_corpus") or [],
                "ps": p.get("status") or "",
            })(_cev.get(c.get("drug")) or {})})
    crow.sort(key=lambda r: r["dr"].lower())
    CL = {k: A("caninisation", k, d) for k, d in (
        ("detail_ind", "Human indication"),
        ("detail_ev", "Dog evidence for this condition area"),
        ("detail_comp", "Companion-animal programs on this target"),
        ("detail_comp_none", "No program in the supplied list targets this in dogs or cats."),
        ("detail_safety", "Species safety caution"),
        ("detail_precedent", "Class precedent in companion animals"),
        ("detail_disc", "Why the human program stopped"),
        ("detail_formulary", "Already in routine veterinary use as a generic."),
        ("detail_vague", "The human indication is too general to place a tumor type."),
        ("detail_presence", "What is known about companion-animal presence"),
        ("detail_mechanism", "Mechanism in companion animals"),
        ("detail_mechanism_none", "No companion-animal program works this mechanism."),
        ("detail_patents", "Patent filings on this mechanism in companion animals"),
        ("detail_halted", "Halted or written-off companion-animal programs on this mechanism"),
        ("detail_condition", "Corresponding condition in dogs or cats"),
        ("detail_condition_none", "No corresponding companion-animal condition was mapped."),
        ("detail_vetlit", "Veterinary literature (PubMed)"),
        ("detail_vetlit_none", "No veterinary publications found under this molecule's name."),
        ("detail_corpus", "This review's own drug-pair records"),
        ("detail_notchecked", "Not checked: no approved-animal-drug registry is machine-readable."),
        ("detail_source", "Program source"))}
    crow_js = ("""function(r){
var L=""" + json.dumps(CL) + """;
var d='<div class="pd">';
d+='<h4>'+L.detail_ind+'</h4><p>'+esc(r.ind)+(r.co?' · '+esc(r.co):'')+'</p>';
if(r.vg){d+='<p class="src">'+L.detail_vague+'</p>';}
d+='<h4>'+L.detail_ev+'</h4><p class="src">'+esc(r.ev)+'</p>';
d+='<h4>'+L.detail_presence+'</h4>';
d+='<p class="src"><strong>'+esc(r.ps)+'</strong></p>';
d+='<p class="src">'+L.detail_mechanism+': '
 +(r.mc?'<em>'+esc(r.mc)+'</em> — ':'')
 +(r.mh&&r.mh.length?r.mh.map(esc).join('; ')
   :(r.mh?L.detail_mechanism_none:'not classified'))+'</p>';
if(r.mx&&r.mx.length){d+='<p class="src">'+L.detail_halted+': '+r.mx.map(function(x){
  return '<strong>'+esc(x.a)+'</strong>'+(x.p?' — '+esc(x.p):'')+(x.w?'. '+esc(x.w):'')
   +(x.u?' <a href="'+esc(x.u)+'">source</a>':'');}).join(' ')+'</p>';}
if(r.mp&&r.mp.length){d+='<p class="src">'+L.detail_patents+': '+r.mp.map(function(x){
  return '<strong>'+esc(x.a)+'</strong>'+(x.p?' ('+esc(x.p)+')':'')+(x.w?' — '+esc(x.w):'')
   +(x.u?' <a href="'+esc(x.u)+'">source</a>':'');}).join(' ')+'</p>';}
if(r.mn){d+='<p class="src">'+esc(r.mn)+'</p>';}
d+='<p class="src">'+L.detail_condition+': '
 +(r.cc?'<em>'+esc(r.cc)+'</em> — ':'')
 +(r.ch.length?r.ch.map(esc).join('; '):L.detail_condition_none)+'</p>';
if(r.cnn){d+='<p class="src">'+esc(r.cnn)+'</p>';}
d+='<p class="src">'+L.detail_vetlit+': '
 +(r.vl===null||r.vl===undefined?'name could not be resolved for search'
   :(r.vl?r.vl+' publications, '+r.vc+' clinical'
     +(r.vp.length?' — '+r.vp.map(function(p){return '<a href="https://pubmed.ncbi.nlm.nih.gov/'+p+'/">'+p+'</a>';}).join(', '):'')
     :L.detail_vetlit_none))+'</p>';
if(r.pc.length){d+='<p class="src">'+L.detail_corpus+': '+r.pc.map(esc).join('; ')+'</p>';}
d+='<p class="src">'+L.detail_notchecked+'</p>';
if(r.fm){d+='<p class="src"><span class="chip warn">in veterinary use</span> '+L.detail_formulary+'</p>';}
if(r.pr){d+='<h4>'+L.detail_precedent+'</h4><p class="src">'+esc(r.pr)+'</p>';}
if(r.sf.length){d+='<h4>'+L.detail_safety+'</h4><p class="src">'+r.sf.map(esc).join(' ')+'</p>';}
if(r.dn){d+='<h4>'+L.detail_disc+'</h4><p class="src">'+esc(r.dn)+'</p>';}
if(r.src){d+='<p class="src">'+L.detail_source+': <a href="'+esc(r.src)+'">'+esc(r.src.slice(0,74))+'</a></p>';}
d+='</div>';
return '<tr class="row"><td><strong>'+esc(r.dr)+'</strong>'
+(r.ing&&r.ing.toLowerCase()!==r.dr.toLowerCase()?'<br><span class="src">'+esc(r.ing)+'</span>':'')
+(r.fm?' <span class="chip warn">in veterinary use</span>':'')+'</td>'
+'<td>'+esc(r.tg)+'</td><td>'+esc(r.ind)+'</td><td>'+esc(r.ar)+'</td><td>'+esc(r.rt)+'</td>'
+'<td>'+esc(r.st)+(r.yr?' <span class="src">'+r.yr+'</span>':'')+'</td>'
+'<td class="num">'+((r.mh&&r.mh.length)||r.ch.length?((r.mh?r.mh.length:0)+r.ch.length):'—')+'</td></tr>'
+'<tr class="det" hidden><td colspan="7">'+d+'</td></tr>';}""")
    ccols = [{"key": "dr", "label": A("caninisation", "col_drug", "Molecule")},
             {"key": "tg", "label": A("caninisation", "col_target", "Target")},
             {"key": "ind", "label": A("caninisation", "col_ind", "Human indication")},
             {"key": "ar", "label": A("caninisation", "col_area", "Condition area")},
             {"key": "rt", "label": A("caninisation", "col_route", "Route")},
             {"key": "st", "label": A("caninisation", "col_stage", "Human stage")},
             {"key": "cn", "label": A("caninisation", "col_comp", "Companion-animal programs"),
              "num": True}]
    body, sections, title = compose("caninisation.md", scalars, {
        "cand_figures": figures_block([
            (scalars["n_candidates"], A("caninisation", "fig_candidates", "candidates")),
            (scalars["n_route1"], A("caninisation", "fig_route1", "approved, no companion program")),
            (scalars["n_route2"], A("caninisation", "fig_route2", "approved, target claimed")),
            (scalars["n_route3"], A("caninisation", "fig_route3", "shelved, non-clinical")),
            (scalars["n_watch"], A("caninisation", "fig_watch", "pipeline watch list"))]),
        "cand_routes": cand_routes(_cand),
        "cand_presence": cand_presence(_pcounts),
        "pairs_flow": pairs_flow(classified, attrs),
        "cand_lag": cand_lag(attrs),
        "cand_areas": cand_areas(_cand),
        "cand_crowding": cand_crowding(_cand),
        "cand_funnel": cand_funnel(_cand),
        "cand_table": browser("cands", "canddata", json.dumps(crow, separators=(",", ":")), ccols,
                              [("ar", A("caninisation", "filter_area", "Condition area")),
                               ("rt", A("caninisation", "filter_route", "Route")),
                               ("st", A("caninisation", "filter_stage", "Human stage"))],
                              A("caninisation", "noun", "candidates"),
                              ["dr", "ing", "tg", "ind", "co"], crow_js,
                              placeholder=A("caninisation", "placeholder", ""),
                              empty=A("caninisation", "empty", ""),
                              reset=A("caninisation", "reset", "Reset"))})
    page("caninisation.html", title or "Licensing human molecules for dogs and cats", body,
         rail=sections)

    # ---------------- study pages ----------------
    for pm, rs in studies.items():
        r0 = rs[0]
        header = (f'<p class="dek">Study</p><h1>{e(r0.get("title") or pm)}</h1>'
                  f'<p class="small">{e(r0.get("year"))} · {e(r0.get("design"))} · peer reviewed: '
                  f'{e(r0.get("peer_reviewed"))} · record {e(pm)} · '
                  f'<a href="{e(record_link(pm)[0])}">{e(record_link(pm)[1])}</a></p>')
        rblocks = []
        for r in rs:
            meta = [dirtag(r["direction"]), f'level {e((r["level"] or "?")[:1])}',
                    e(sp_label(r)), e(area_display(r))]
            if r.get("_value_display"):
                meta.append(f"<strong>{e(r['_value_display'])}</strong>")
            elif r.get("value") is not None:
                unit = "" if r.get("unit") in (None, "none") else f" {e(r['unit'])}"
                meta.append(f"<strong>{e(r.get('value'))}{unit}</strong>")
            if r.get("denominator"):
                meta.append(f"n {e(r.get('numerator'))}/{e(r.get('denominator'))}")
            rblocks.append(f"<h3>{t(r['statement'])}</h3>"
                           f'<p class="small">' + " · ".join(meta) + "</p>"
                           f"<blockquote>“{e(r.get('quote'))}”<br><span class='small'>page "
                           f"{e(r.get('pdf_page'))}</span></blockquote>")
        body, _, _ = compose("study.md", {**scalars, "n_results": str(len(rs)),
                                          "result_word": "finding" if len(rs) == 1 else "findings"},
                             {"study_header": header, "study_results": "\n".join(rblocks)})
        page(f"study/{pm}.html", (r0.get("title") or pm)[:80], body, depth=1)

    # ---------------- spot-check ----------------
    items = load("part1/spotcheck.json", [])
    sb = []
    for s, label in (("A", "Sample A — random across all kept results"),
                     ("B", "Sample B — single-reviewer studies")):
        rows_s = [x for x in items if x["sample"] == s]
        sb.append(f'<h2 id="sample{s}">{e(label)} ({len(rows_s)})</h2>')
        for it in rows_s:
            ln = " · ".join(f'<a href="{e(u)}">{e(lbl)}</a>' for lbl, u in it["links"])
            val = ""
            if it["value"] is not None:
                unit = "" if it.get("unit") in (None, "none") else f" {e(it['unit'])}"
                val = f" · <strong>{e(it['value'])}{unit}</strong>"
                if it["denominator"]:
                    val += f" (n {e(it['numerator'])}/{e(it['denominator'])})"
            sb.append(f"<h3>{e(s)}{it['n']}. {e((it['title'] or it['pmid'])[:110])}</h3>"
                      f'<p class="small">{e(it["year"])} · {e(it["journal"] or "—")} · {ln} · '
                      f'<a href="study/{e(it["pmid"])}.html">study page</a> · <strong>page '
                      f'{e(it["pdf_page"])}</strong> · adjudication: '
                      f'{"single reviewer" if it["adjudicator"] == "hand" else "model"}</p>'
                      f"<p>{t(it['statement'])}</p>"
                      f'<p class="small">species {e(it["species"])} · level {e(it["level"])} · '
                      f'{dirtag(it["direction"])}{val}</p>'
                      f"<blockquote>“{e(it['quote'])}”</blockquote>")
    body, _, title = compose("spotcheck.md", scalars, {"spotcheck_items": "\n".join(sb)})
    page("spotcheck.html", title or "Spot-check this review", body)

    # ---------------- api ----------------
    os.makedirs(os.path.join(OUT, "api"), exist_ok=True)
    json.dump(fin, open(os.path.join(OUT, "api", "results.json"), "w"), indent=1)
    json.dump(load("part1/evidence_map.json"), open(os.path.join(OUT, "api", "evidence_map.json"), "w"), indent=1)
    json.dump({"built": today(), "results": len(fin), "studies": n_stud,
               "by_level": dict(by_level), "by_direction": dict(by_dir),
               "pairs_classified": len(classified)},
              open(os.path.join(OUT, "api", "summary.json"), "w"), indent=1)
    print(f"built {OUT}: {len(fin)} results, {n_stud} study pages, {len(classified)} pairs")
    print(f"tokens: extracted={n_extracted} extraction_studies={n_extraction_studies} "
          f"eligible={n_eligible} single_reviewer={n_single} limitations={n_limits} "
          f"unresolved={unresolved}")


if __name__ == "__main__":
    main()
