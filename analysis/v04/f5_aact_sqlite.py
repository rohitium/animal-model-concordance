"""Load the ClinicalTrials.gov snapshot (AACT flat files, 2026-09-14) into a local SQLite subset, and
link trial interventions to the US human-medicine ingredient index (amendment A5).

Only the tables needed to classify the human side are loaded. The ingredient link is a lookup,
not a model: each intervention name and its "other names" are split into word n-grams (1-4 words),
salt-stripped with the same normaliser as f4_human_index.py, and kept where an n-gram equals an
indexed ingredient base. How each link was made (name or other-name; exact or salt-stripped) is
stored so it can be audited.

Output: data/raw/snapshots/aact/aact_subset.sqlite (gitignored; rebuilt from the snapshot)
"""
import sys, os, io, csv, zipfile, sqlite3, time
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from f4_human_index import norm, base

csv.field_size_limit(10**9)
ZIP = J("data", "raw", "snapshots", "aact", "20260914_export_ctgov.zip")
DB = J("data", "raw", "snapshots", "aact", "aact_subset.sqlite")

TABLES = {
    "studies": ["nct_id", "study_type", "brief_title", "official_title", "overall_status", "phase", "enrollment",
                "why_stopped", "start_date", "primary_completion_date", "completion_date", "results_first_posted_date",
                "source", "source_class"],
    "interventions": ["id", "nct_id", "intervention_type", "name", "description"],
    "intervention_other_names": ["id", "nct_id", "intervention_id", "name"],
    "conditions": ["id", "nct_id", "name"],
    "browse_conditions": ["id", "nct_id", "mesh_term", "mesh_type"],
    "designs": ["nct_id", "allocation", "intervention_model", "primary_purpose", "masking"],
    "design_groups": ["id", "nct_id", "group_type", "title", "description"],
    "design_group_interventions": ["id", "nct_id", "design_group_id", "intervention_id"],
    "outcomes": ["id", "nct_id", "outcome_type", "title", "description", "time_frame", "units", "param_type"],
    "outcome_analyses": ["id", "nct_id", "outcome_id", "non_inferiority_type", "non_inferiority_description",
                         "param_type", "param_value", "p_value_modifier", "p_value", "ci_percent", "ci_lower_limit",
                         "ci_upper_limit", "method", "groups_description", "estimate_description"],
    "study_references": ["id", "nct_id", "pmid", "reference_type"],
}
KEEP_TYPES = {"DRUG", "BIOLOGICAL", "GENETIC", "COMBINATION_PRODUCT"}

def rows(z, table, cols, bad):
    f = io.TextIOWrapper(z.open(f"{table}.txt"), encoding="utf-8", errors="replace", newline="")
    r = csv.reader(f, delimiter="|")
    head = next(r)
    idx = [head.index(c) for c in cols]
    for row in r:
        if len(row) != len(head):
            bad[table] = bad.get(table, 0) + 1
            continue
        yield [row[i] if row[i] != "" else None for i in idx]

def ngrams(name, nmax=4):
    toks = norm(name).split()
    for n in range(1, min(nmax, len(toks)) + 1):
        for i in range(len(toks) - n + 1):
            yield " ".join(toks[i:i + n])

def main():
    t0 = time.time()
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=OFF"); con.execute("PRAGMA synchronous=OFF")
    z = zipfile.ZipFile(ZIP)
    bad = {}
    for table, cols in TABLES.items():
        con.execute(f"CREATE TABLE {table} ({', '.join(cols)})")
        batch, n = [], 0
        for row in rows(z, table, cols, bad):
            if table == "outcomes" and row[2] != "PRIMARY":
                continue
            batch.append(row)
            if len(batch) >= 50000:
                con.executemany(f"INSERT INTO {table} VALUES ({','.join('?'*len(cols))})", batch); n += len(batch); batch = []
        if batch:
            con.executemany(f"INSERT INTO {table} VALUES ({','.join('?'*len(cols))})", batch); n += len(batch)
        con.commit()
        print(f"  {table:28s} {n:>10,} rows  (malformed skipped: {bad.get(table, 0)})  {time.time()-t0:.0f}s", flush=True)
    for col_table, col in (("studies", "nct_id"), ("interventions", "nct_id"), ("interventions", "id"),
                           ("intervention_other_names", "intervention_id"), ("conditions", "nct_id"),
                           ("browse_conditions", "nct_id"), ("designs", "nct_id"), ("design_groups", "id"),
                           ("design_group_interventions", "intervention_id"), ("outcomes", "nct_id"),
                           ("outcome_analyses", "outcome_id"), ("study_references", "nct_id")):
        con.execute(f"CREATE INDEX IF NOT EXISTS ix_{col_table}_{col} ON {col_table}({col})")

    keys = set(load("frames/human_index.json").keys())
    con.execute("CREATE TABLE ingredient_links (ingredient, intervention_id, nct_id, via, matched_text, kind)")
    other = {}
    for iid, name in con.execute("SELECT intervention_id, name FROM intervention_other_names"):
        other.setdefault(iid, []).append(name)
    links = []
    for iid, nct, itype, name in con.execute("SELECT id, nct_id, intervention_type, name FROM interventions"):
        if itype not in KEEP_TYPES:
            continue
        seen = set()
        for via, text in [("name", name)] + [("other_name", o) for o in other.get(iid, [])]:
            for g in ngrams(text or ""):
                b = base(g)
                if b in keys and b not in seen:
                    seen.add(b)
                    links.append((b, iid, nct, via, text, "exact" if g == b else "salt-stripped"))
        if len(links) > 50000:
            con.executemany("INSERT INTO ingredient_links VALUES (?,?,?,?,?,?)", links); links = []
    con.executemany("INSERT INTO ingredient_links VALUES (?,?,?,?,?,?)", links)
    con.execute("CREATE INDEX ix_links_ing ON ingredient_links(ingredient)")
    con.commit()
    n_links, n_ing = con.execute("SELECT COUNT(*), COUNT(DISTINCT ingredient) FROM ingredient_links").fetchone()
    print(f"ingredient links: {n_links:,} across {n_ing:,} ingredients; malformed rows skipped: {bad}; {time.time()-t0:.0f}s")
    save({"built": today(), "source_zip": os.path.relpath(ZIP, ROOT), "malformed_rows_skipped": bad,
          "ingredient_links": n_links, "ingredients_linked": n_ing}, "frames/aact_subset_build.json")

if __name__ == "__main__":
    main()
