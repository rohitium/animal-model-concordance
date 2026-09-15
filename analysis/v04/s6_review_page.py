"""Build the human review page (PLAN.md v0.4 §8.1 stage 5, §8.4).

The page carries the flagged items and the audit sample as embedded content. The reviewer's
decisions are stored as rows in the artifact's database (collections `resolutions` and `audit`),
which `s7_import_review.py` reads back. Nothing the reviewer decides is written into this HTML.

Output: data/v04/review/index.html
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

SHOW = ["what_is_compared", "species", "species_as_reported", "model_type", "index_test_kind", "level",
        "disease_area", "metric", "metric_as_reported", "value", "unit", "ci_low", "ci_high",
        "numerator", "denominator", "provenance", "location", "pdf_page"]

def slim(rec):
    if not rec:
        return None
    if "index_tests" in rec:
        return rec
    d = {k: rec.get(k) for k in SHOW}
    d["quote"] = rec.get("quote")
    return d

def main():
    queue = load("review_queue.json", [])
    audit = load("audit_sample.json", [])
    scope = load("s1_scope.json")
    items = [{"id": q["id"], "pmid": q["pmid"], "title": q.get("title"), "kind": q.get("kind", "comparison"),
              "reasons": q["reasons"], "record": slim(q["record"]), "other": slim(q.get("other_extraction")),
              "pages": q.get("pdf_pages")} for q in queue]
    aud = [{"id": a["id"], "pmid": a["pmid"], "title": scope.get(a["pmid"], {}).get("title"),
            "record": slim(a["record"]), "page": a.get("pdf_page")} for a in audit]
    data = json.dumps({"generated": today(), "items": items, "audit": aud}, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", data)
    os.makedirs(os.path.join(V04, "review"), exist_ok=True)
    open(os.path.join(V04, "review", "index.html"), "w").write(html)
    print(f"review page: {len(items)} flagged items, {len(aud)} audit items")

TEMPLATE = r"""<title>Concordance Review Queue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F4F6F3; --surface:#FFFFFF; --ink:#1C2420; --muted:#5C6862; --line:#D9DFDA;
  --accent:#1F6F6A; --accent-ink:#FFFFFF; --flag:#9A6512; --flag-bg:#FBF1DE;
  --ok:#2C7A4B; --ok-bg:#E3F2E8; --bad:#A8412C; --bad-bg:#F8E4DE; --unsure:#5B5F9E; --unsure-bg:#E8E9F6;
  --diff:#FFF3C4; --quote-bg:#EEF2EF;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --ground:#121614; --surface:#1A201D; --ink:#E3E8E5; --muted:#98A39D; --line:#2C3530;
  --accent:#5FB3AB; --accent-ink:#0E1412; --flag:#E2B25C; --flag-bg:#33291A;
  --ok:#77C796; --ok-bg:#1D3326; --bad:#E58C77; --bad-bg:#3A221C; --unsure:#A9ADEA; --unsure-bg:#262842;
  --diff:#3D3718; --quote-bg:#202824;
}}
:root[data-theme="dark"]{
  --ground:#121614; --surface:#1A201D; --ink:#E3E8E5; --muted:#98A39D; --line:#2C3530;
  --accent:#5FB3AB; --accent-ink:#0E1412; --flag:#E2B25C; --flag-bg:#33291A;
  --ok:#77C796; --ok-bg:#1D3326; --bad:#E58C77; --bad-bg:#3A221C; --unsure:#A9ADEA; --unsure-bg:#262842;
  --diff:#3D3718; --quote-bg:#202824;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font:15px/1.5 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;padding-inline:20px;padding-block:24px 64px}
.wrap{max-width:1080px;margin:0 auto;display:grid;gap:20px}
header{display:grid;gap:6px}
h1{font-size:24px;font-weight:600;margin:0;text-wrap:balance}
.sub{color:var(--muted);margin:0;max-width:70ch}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;position:sticky;top:0;background:var(--ground);padding-block:10px;z-index:2;border-bottom:1px solid var(--line)}
.tabs,.filters{display:flex;flex-wrap:wrap;gap:6px}
button,select,input,textarea{font:inherit;color:inherit}
.tab{border:1px solid var(--line);background:var(--surface);padding:6px 12px;border-radius:6px;cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
select{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:6px 8px;max-width:100%}
.progress{font-variant-numeric:tabular-nums;color:var(--muted);font-size:14px}
.progress b{color:var(--ink)}
.notice{border:1px solid var(--flag);background:var(--flag-bg);color:var(--ink);padding:10px 14px;border-radius:6px}
.list{display:grid;gap:14px}
.item{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px;display:grid;gap:12px}
.item[data-state="accept"],.item[data-state="correct"]{border-left:4px solid var(--ok)}
.item[data-state="reject"]{border-left:4px solid var(--bad)}
.item[data-state="unsure"]{border-left:4px solid var(--unsure)}
.head{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;justify-content:space-between}
.study{font-weight:600;margin:0;font-size:15px;text-wrap:balance}
.meta{font:13px "IBM Plex Mono",ui-monospace,monospace;color:var(--muted)}
.meta a{color:var(--accent)}
.reasons{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.reasons li{background:var(--flag-bg);color:var(--ink);border:1px solid color-mix(in srgb,var(--flag) 45%,transparent);border-radius:4px;padding:2px 8px;font-size:13px;max-width:100%}
.quote{background:var(--quote-bg);border-radius:6px;padding:10px 12px;font:13.5px/1.55 "IBM Plex Mono",ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}
.quote small{display:block;color:var(--muted);margin-bottom:4px;font-family:"IBM Plex Sans",sans-serif}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:500;white-space:nowrap;width:1%}
td{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
tr.diff td{background:var(--diff)}
thead th{font-family:"IBM Plex Sans",sans-serif;color:var(--ink);font-weight:600}
.actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.act{border:1px solid var(--line);background:var(--surface);border-radius:6px;padding:6px 12px;cursor:pointer}
.act:hover{border-color:var(--accent)}
.act[aria-pressed="true"][data-v="accept"],.act[aria-pressed="true"][data-v="correct"],.act[aria-pressed="true"][data-v="yes"]{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
.act[aria-pressed="true"][data-v="reject"],.act[aria-pressed="true"][data-v="no"]{background:var(--bad-bg);border-color:var(--bad);color:var(--bad)}
.act[aria-pressed="true"][data-v="unsure"]{background:var(--unsure-bg);border-color:var(--unsure);color:var(--unsure)}
.act:disabled{opacity:.5;cursor:not-allowed}
.fix{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;width:100%}
.fix label{display:grid;gap:2px;font-size:12.5px;color:var(--muted)}
.fix input,.fix textarea{background:var(--ground);border:1px solid var(--line);border-radius:6px;padding:6px 8px;color:var(--ink)}
.fix textarea{min-height:56px;grid-column:1/-1}
.saved{font-size:12.5px;color:var(--muted)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.empty{color:var(--muted);padding:24px 0}
@media (max-width:560px){ th{white-space:normal} }
</style>

<div class="wrap">
  <header>
    <h1>Concordance Review Queue</h1>
    <p class="sub">Items the automated checks could not settle, and a random sample of items they accepted. Decide each against the paper's PDF. Your decisions are saved as you go and read back into the pipeline.</p>
  </header>
  <div id="notice" class="notice" hidden></div>
  <div class="bar">
    <div class="tabs" role="tablist">
      <button class="tab" role="tab" id="tab-flags" aria-selected="true">Flagged</button>
      <button class="tab" role="tab" id="tab-audit" aria-selected="false">Audit sample</button>
    </div>
    <div class="filters">
      <select id="f-reason" aria-label="Filter by reason"><option value="">All reasons</option></select>
      <select id="f-state" aria-label="Filter by status"><option value="open">Undecided</option><option value="">All</option><option value="done">Decided</option></select>
    </div>
    <div class="progress" id="progress"></div>
  </div>
  <div class="list" id="list"></div>
</div>

<script type="application/json" id="data">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("data").textContent);
const state = { tab: "flags", reason: "", status: "open", res: {}, aud: {}, db: null };
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const reasonKey = r => r.split(/[:—(]/)[0].trim();

const reasons = [...new Set(DATA.items.flatMap(i => i.reasons.map(reasonKey)))].sort();
for (const r of reasons) { const o = document.createElement("option"); o.value = r; o.textContent = r; $("#f-reason").append(o); }

function recordTable(rec, other) {
  if (!rec) return "";
  if (rec.index_tests) {
    return `<div class="tablewrap"><table><thead><tr><th>Index test</th><th>Kind</th></tr></thead><tbody>${
      rec.index_tests.map(t => `<tr><td>${esc(t.description)}</td><td>${esc(t.kind)}</td></tr>`).join("")}</tbody></table></div>`;
  }
  const keys = Object.keys(rec).filter(k => k !== "quote");
  const rows = keys.map(k => {
    const a = rec[k], b = other ? other[k] : undefined;
    const diff = other && JSON.stringify(a) !== JSON.stringify(b);
    return `<tr class="${diff ? "diff" : ""}"><th>${esc(k.replace(/_/g, " "))}</th><td>${esc(a)}</td>${other ? `<td>${esc(b)}</td>` : ""}</tr>`;
  }).join("");
  return `<div class="tablewrap"><table>${other ? `<thead><tr><th></th><th>Extraction shown</th><th>Other extractor</th></tr></thead>` : ""}<tbody>${rows}</tbody></table></div>`;
}

function quoteBlock(rec, label) {
  if (!rec || !rec.quote) return "";
  return `<p class="quote"><small>${esc(label)}</small>${esc(rec.quote)}</p>`;
}

function flagCard(it) {
  const r = state.res[it.id];
  const decided = r && r.decision;
  const isScope = it.kind === "confirm-study-exclusion";
  const choices = isScope
    ? [["accept", "Confirm exclusion"], ["reject", "Reinstate study"], ["unsure", "Unsure"]]
    : [["accept", "Accept as extracted"], ["correct", "Accept with correction"], ["reject", "Reject"], ["unsure", "Unsure"]];
  const pages = it.pages && it.pages.length ? `PDF p. ${it.pages.join(", ")}` : "";
  return `<article class="item" data-id="${esc(it.id)}" data-state="${esc(decided || "")}">
    <div class="head"><p class="study">${esc(it.title || "Untitled")}</p>
      <span class="meta"><a href="https://pubmed.ncbi.nlm.nih.gov/${esc(it.pmid)}/" target="_blank" rel="noopener">PMID ${esc(it.pmid)}</a> · ${esc(it.id)}${pages ? " · " + esc(pages) : ""}</span></div>
    <ul class="reasons">${it.reasons.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
    ${quoteBlock(it.record, "Quote, extraction shown")}${it.other && it.other.quote !== it.record?.quote ? quoteBlock(it.other, "Quote, other extractor") : ""}
    ${recordTable(it.record, it.other)}
    <div class="actions">${choices.map(([v, l]) => `<button class="act" data-v="${v}" aria-pressed="${decided === v}" ${state.db ? "" : "disabled"}>${l}</button>`).join("")}
      <span class="saved">${r && r.at ? "Saved " + esc(new Date(r.at).toLocaleString()) : ""}</span></div>
    <div class="fix" ${decided === "correct" || decided === "reject" || decided === "unsure" ? "" : "hidden"}>
      ${decided === "correct" ? `<label>Correct value<input id="val-${esc(it.id)}" data-f="value" value="${esc(r.value ?? "")}"></label>
      <label>Correct species<input id="sp-${esc(it.id)}" data-f="species" value="${esc(r.species ?? "")}"></label>
      <label>Correct level (A/B/C)<input id="lv-${esc(it.id)}" data-f="level" value="${esc(r.level ?? "")}"></label>` : ""}
      <textarea id="note-${esc(it.id)}" data-f="note" placeholder="Note (what is wrong, or why you are unsure)">${esc(r?.note ?? "")}</textarea>
    </div>
  </article>`;
}

function auditCard(it) {
  const r = state.aud[it.id];
  const v = r && r.correct;
  return `<article class="item" data-id="${esc(it.id)}" data-state="${v === "yes" ? "accept" : v === "no" ? "reject" : v ? "unsure" : ""}">
    <div class="head"><p class="study">${esc(it.title || "Untitled")}</p>
      <span class="meta"><a href="https://pubmed.ncbi.nlm.nih.gov/${esc(it.pmid)}/" target="_blank" rel="noopener">PMID ${esc(it.pmid)}</a> · ${esc(it.id)}${it.page ? " · PDF p. " + esc(it.page) : ""}</span></div>
    ${quoteBlock(it.record, "Quote")}
    ${recordTable(it.record, null)}
    <div class="actions">${[["yes","Every field correct"],["no","Something is wrong"],["unsure","Unsure"]].map(([val,l]) => `<button class="act" data-v="${val}" aria-pressed="${v === val}" ${state.db ? "" : "disabled"}>${l}</button>`).join("")}
      <span class="saved">${r && r.at ? "Saved " + esc(new Date(r.at).toLocaleString()) : ""}</span></div>
    <div class="fix" ${v === "no" || v === "unsure" ? "" : "hidden"}><textarea id="anote-${esc(it.id)}" data-f="note" placeholder="Which field is wrong, and what should it be?">${esc(r?.note ?? "")}</textarea></div>
  </article>`;
}

function render() {
  const flags = state.tab === "flags";
  $("#tab-flags").setAttribute("aria-selected", flags); $("#tab-audit").setAttribute("aria-selected", !flags);
  $("#f-reason").hidden = !flags;
  const src = flags ? DATA.items : DATA.audit;
  const store = flags ? state.res : state.aud;
  const isDone = it => flags ? !!(store[it.id] && store[it.id].decision) : !!(store[it.id] && store[it.id].correct);
  let list = src;
  if (flags && state.reason) list = list.filter(i => i.reasons.some(r => reasonKey(r) === state.reason));
  if (state.status === "open") list = list.filter(i => !isDone(i));
  if (state.status === "done") list = list.filter(isDone);
  const done = src.filter(isDone).length;
  $("#progress").innerHTML = `<b>${done}</b> of ${src.length} decided`;
  $("#list").innerHTML = list.length ? list.map(flags ? flagCard : auditCard).join("")
    : `<p class="empty">${src.length ? "Nothing left under this filter." : "No items in this list."}</p>`;
}

let pending = {};
async function save(id, patch) {
  const flags = state.tab === "flags";
  const store = flags ? state.res : state.aud;
  store[id] = { ...(store[id] || {}), ...patch, at: Date.now() };
  if (!state.db) return;
  clearTimeout(pending[id]);
  pending[id] = setTimeout(async () => {
    try { await state.db.doc(`${flags ? "resolutions" : "audit"}/${id}`).set(store[id]); }
    catch (e) { showNotice(`Could not save ${id}: ${e.code || e.message}. Your choice is shown but not stored; try again.`); }
  }, 400);
}

document.addEventListener("click", e => {
  const tab = e.target.closest(".tab");
  if (tab) { state.tab = tab.id === "tab-flags" ? "flags" : "audit"; render(); return; }
  const b = e.target.closest(".act"); if (!b) return;
  const id = b.closest(".item").dataset.id;
  const v = b.dataset.v;
  if (state.tab === "flags") save(id, { decision: v }); else save(id, { correct: v });
  const keepOpen = state.status;
  state.status = ""; render(); state.status = keepOpen;
  document.querySelector(`.item[data-id="${CSS.escape(id)}"]`)?.scrollIntoView({ block: "nearest" });
});
document.addEventListener("input", e => {
  const f = e.target.dataset.f; if (!f) return;
  const id = e.target.closest(".item").dataset.id;
  save(id, { [f]: e.target.value });
});
$("#f-reason").addEventListener("change", e => { state.reason = e.target.value; render(); });
$("#f-state").addEventListener("change", e => { state.status = e.target.value; render(); });

function showNotice(msg) { const n = $("#notice"); n.textContent = msg; n.hidden = false; }

render();
(async () => {
  const db = window.claude ? await window.claude.use("db") : null;
  if (!db) { showNotice("Saving is not available in this view, so decisions cannot be recorded. Open the page in Claude to review."); return; }
  state.db = db;
  const listen = (col, target) => db.collection(col).onSnapshot(snap => {
    for (const d of snap.docs) if (d.exists) target[d.id] = d.data();
    if (!document.activeElement || !document.activeElement.dataset.f) render();
  }, err => showNotice(`Live sync stopped (${err.code}). Reload the page to reconnect.`));
  listen("resolutions", state.res); listen("audit", state.aud);
  render();
})();
</script>
"""

if __name__ == "__main__":
    main()
