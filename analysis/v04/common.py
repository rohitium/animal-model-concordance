"""Shared helpers for the v0.4 pipeline (PLAN.md v0.4, tag protocol-v0.4).

Everything that more than one stage needs lives here: paths, the frozen vocabularies, the model
ladder (§8.2), a cached LLM call that can attach the PDF, per-page PDF text, and mechanical
location of a number or quote on a page (§8.1 stage 2).
"""
import os, sys, json, re, hashlib, base64, time, subprocess, threading, datetime
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
J = lambda *p: os.path.join(ROOT, *p)
V04 = J("data", "v04")
CACHE = J("data", "v04", "cache")
os.makedirs(os.path.join(CACHE, "llm"), exist_ok=True)
os.makedirs(os.path.join(CACHE, "text"), exist_ok=True)
sys.path.insert(0, J("analysis"))
import openrouter as orr  # noqa: E402  (key handling only)

# --- §8.2 model ladder -----------------------------------------------------------------------
# Two families per tier. A stage moves up only on measured failure; the tier used is recorded on
# every output so no stage silently mixes models.
LADDER = {
    1: {"A": "google/gemini-2.5-flash-lite", "B": "openai/gpt-5-nano"},
    2: {"A": "google/gemini-2.5-flash", "B": "openai/gpt-5-mini"},
}
def tier(stage):
    """Tier for a stage, from AMC_TIER_<STAGE> or AMC_TIER, default 1."""
    return int(os.environ.get(f"AMC_TIER_{stage.upper()}", os.environ.get("AMC_TIER", "1")))

# --- frozen vocabularies (§4) ----------------------------------------------------------------
# Disease areas are a starting set (§4.1). A comparison that fits none is recorded as "new" with a
# proposed name, never forced into the nearest row; new rows are logged as amendments.
DISEASE_AREAS = [
    "oncology", "immunology-inflammation", "infectious-disease", "cardiovascular",
    "metabolic-endocrine", "renal", "liver-gi", "neurology", "psychiatry-addiction",
    "pain-musculoskeletal", "respiratory", "ophthalmology", "haematology", "dermatology",
    "reproductive-developmental", "cross-cutting-toxicology", "new",
]
SPECIES = [
    "mouse", "rat", "other-rodent", "rabbit", "pig-minipig", "sheep-goat", "non-human-primate",
    "dog", "cat", "horse", "zebrafish", "drosophila", "c-elegans", "other-species",
    "grouped-label",
]
MODEL_TYPES = ["induced", "engineered", "spontaneous-lab", "spontaneous-companion", "healthy",
               "mixed-or-not-stated"]
LEVELS = ["A", "B", "C"]  # D is counted at screening, never extracted (§4.3)

def species_column(species, model_type):
    """§4.2: laboratory and companion dogs/cats are separate columns."""
    if species in ("dog", "cat"):
        return f"companion-{species}" if model_type == "spontaneous-companion" else f"laboratory-{species}"
    return species

# --- io --------------------------------------------------------------------------------------
def load(path, default=None):
    p = path if os.path.isabs(path) else os.path.join(V04, path)
    if not os.path.exists(p):
        return {} if default is None else default
    return json.load(open(p))

def save(obj, path):
    p = path if os.path.isabs(path) else os.path.join(V04, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, p)

def today():
    return datetime.date.today().isoformat()

def pdf_path(pm):
    p = J("data", "raw", "fulltext", f"{pm}.pdf")
    return p if os.path.exists(p) else None

def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()

# --- LLM call --------------------------------------------------------------------------------
class Truncated(RuntimeError):
    """Model output could not be parsed as JSON; not retried."""

# One cap on simultaneous API calls across every thread, so stages can nest parallel work
# (candidates x records) without flooding a provider.
API_SLOTS = threading.BoundedSemaphore(int(os.environ.get("AMC_MAX_CONCURRENCY", "48")))

def _env_key(name):
    """Read a key from the environment or .env. Never logged or returned to output."""
    k = os.environ.get(name)
    if not k and os.path.exists(J(".env")):
        for line in open(J(".env")):
            if line.strip().startswith(name + "="):
                k = line.split("=", 1)[1].strip().strip("'\"")
    return k

# Direct-provider fallback, used only when OpenRouter throttles, errors or hangs, and only when the
# SAME model is available directly — a stage never silently switches models (§8.2).
# gemini-2.5-flash-lite is not offered to new direct-API users (checked 2026-09-14), so Gemini calls
# have no fallback.
DIRECT = {"openai/gpt-5-nano": ("openai", "gpt-5-nano"), "openai/gpt-5-mini": ("openai", "gpt-5-mini"),
          "anthropic/claude-sonnet-5": ("anthropic", "claude-sonnet-5")}
DIRECT_KEY = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}

def _direct_anthropic(model_id, system, content, schema, max_tokens, deadline_s):
    """Anthropic Messages API with the same inputs. The PDF goes as a document block; structured output is forced
    through a single tool whose input schema is the requested schema. Normalised to the OpenRouter response shape."""
    blocks = []
    for c in content:
        if c["type"] == "text":
            blocks.append({"type": "text", "text": c["text"]})
        elif c["type"] == "file":
            data = c["file"]["file_data"].split(",", 1)[1]
            blocks.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}})
    body = {"model": model_id, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": blocks}],
            "tools": [{"name": "answer", "description": "Return the answer.", "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "answer"}}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                 headers={"x-api-key": _env_key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    d = json.loads(_read_with_deadline(req, deadline_s))
    tool = next((b for b in d.get("content", []) if b.get("type") == "tool_use"), None)
    if tool is None:
        raise RuntimeError(f"anthropic direct: no tool_use block (stop_reason={d.get('stop_reason')})")
    return {"choices": [{"message": {"content": json.dumps(tool["input"])}, "finish_reason": d.get("stop_reason")}],
            "usage": d.get("usage", {}), "route": "anthropic-direct"}

def _direct_openai(model_id, system, content, schema, max_tokens, deadline_s):
    parts = []
    for c in content:
        parts.append(c)
    body = {"model": model_id, "max_completion_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": parts}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "out", "strict": True, "schema": schema}}}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {_env_key('OPENAI_API_KEY')}",
                                          "Content-Type": "application/json"})
    d = json.loads(_read_with_deadline(req, deadline_s))
    d["route"] = "openai-direct"
    return d

_cost_lock = threading.Lock()
COST = {"usd": 0.0, "calls": 0, "cached": 0}

def _read_with_deadline(req, deadline_s):
    """Read a response under a wall-clock deadline.

    A socket timeout alone is not enough: OpenRouter sends keep-alive bytes while a request is
    processing, which resets the per-read timeout, so a generation stuck upstream hung jobs
    indefinitely (observed 2026-09-14). Reading in chunks lets us check the clock between them.
    """
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=60) as r:
        buf = []
        while True:
            if time.monotonic() - start > deadline_s:
                raise TimeoutError(f"no complete response within {deadline_s}s")
            chunk = r.read1(65536) if hasattr(r, "read1") else r.read(65536)
            if not chunk:
                break
            buf.append(chunk)
    return b"".join(buf).decode()

def ask(model, system, user, schema, pm=None, max_tokens=32000, retries=4, deadline_s=None):
    """One structured call, optionally with the study's PDF attached. Cached on every input.

    Returns (parsed_json, meta). Raises after `retries` failures.
    """
    pdf_b64, pdf_hash = None, None
    if pm:
        raw = open(pdf_path(pm), "rb").read()
        pdf_hash = sha(raw)
        pdf_b64 = base64.b64encode(raw).decode()
    key = sha(json.dumps([model, system, user, schema, pdf_hash, max_tokens], sort_keys=True))[:32]
    cp = os.path.join(CACHE, "llm", f"{key}.json")
    if os.path.exists(cp):
        d = json.load(open(cp))
        with _cost_lock:
            COST["cached"] += 1
        return json.loads(d["choices"][0]["message"]["content"]), {"model": model, "cached": True}

    content = [{"type": "text", "text": user}]
    too_many_pages = bool(pdf_b64) and model.startswith("anthropic/") and len(pages(pm)) > 100   # Anthropic PDF limit
    if pdf_b64 and (len(raw) > 14_000_000 or too_many_pages):
        # Providers cap request bodies (Google AI Studio: 20 MB after base64). Send the PDF's text layer with
        # page markers instead, so page citations still work; tables survive as text, figures do not.
        text = "\n".join(f"--- PDF page {i} ---\n{t}" for i, t in enumerate(pages(pm), 1))[:600_000]
        content[0]["text"] = user + "\n\nFULL TEXT (PDF too large to attach; text layer with page markers):\n" + text
        pdf_b64 = None
    if pdf_b64:
        content.append({"type": "file", "file": {"filename": f"{pm}.pdf",
                        "file_data": f"data:application/pdf;base64,{pdf_b64}"}})
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "out", "strict": True, "schema": schema}}}
    if pdf_b64:
        body["plugins"] = [{"id": "file-parser", "pdf": {"engine": "native"}}]
    if not model.startswith("openai/gpt-5"):
        body["temperature"] = 0
    if deadline_s is None:
        deadline_s = 420 if pdf_b64 else 120
    last = None
    provider = DIRECT.get(model, (None,))[0]
    can_direct = provider is not None and bool(_env_key(DIRECT_KEY[provider]))
    use_direct = can_direct and bool(os.environ.get("AMC_DIRECT_FIRST"))
    for a in range(retries):
        try:
            with API_SLOTS:
                if use_direct:
                    fn = _direct_anthropic if provider == "anthropic" else _direct_openai
                    d = fn(DIRECT[model][1], system, content, schema, max_tokens, deadline_s)
                else:
                    req = urllib.request.Request(orr.URL, data=json.dumps(body).encode(), headers={
                        "Authorization": f"Bearer {orr._key()}", "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/animal-model-concordance", "X-Title": "amc-v04"})
                    d = json.loads(_read_with_deadline(req, deadline_s))
                    d["route"] = "openrouter"
            choice = (d.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            if not msg.get("content"):
                raise RuntimeError(f"empty content: {str(d)[:200]}")
            try:
                parsed = json.loads(msg["content"])
            except json.JSONDecodeError as e:
                fr = choice.get("finish_reason") or choice.get("native_finish_reason")
                if fr in ("length", "max_tokens", "MAX_TOKENS") and len(msg["content"]) < 2000 \
                        and max_tokens < 100000:
                    # A reasoning model spent the budget thinking and ran out a few hundred
                    # characters into the answer. Not a runaway: retry once with a larger budget
                    # (a different request, so not a deterministic repeat).
                    return ask(model, system, user, schema, pm=pm, max_tokens=max_tokens * 3,
                               retries=retries, deadline_s=deadline_s)
                if fr in ("length", "max_tokens", "stop", "MAX_TOKENS", "STOP"):
                    # Truncated or runaway output. At temperature 0 a retry reproduces it, so fail
                    # now and let the stage record the error and flag the item.
                    raise Truncated(f"unparseable output (finish_reason={fr}, "
                                    f"{len(msg['content'])} chars): {e}")
                # A provider error mid-generation (finish_reason "error" etc.) is transient: retry.
                raise RuntimeError(f"provider error mid-generation (finish_reason={fr})")
            json.dump(d, open(cp, "w"))
            with _cost_lock:
                COST["usd"] += (d.get("usage") or {}).get("cost", 0) or 0
                COST["calls"] += 1
            return parsed, {"model": model, "cached": False}
        except Truncated:
            raise
        except urllib.error.HTTPError as e:
            try:
                last = RuntimeError(f"HTTP {e.code} ({'direct' if use_direct else 'openrouter'}): {e.read().decode()[:200]}")
            except Exception:
                last = RuntimeError(f"HTTP {e.code}")
            if (e.code in (402, 429) or e.code >= 500) and can_direct:
                use_direct = True if e.code == 402 else not use_direct   # out of OpenRouter credit: stay direct
            time.sleep(min(30, 3 * 2 ** a))
        except Exception as e:
            last = e
            if isinstance(e, TimeoutError) and can_direct:
                use_direct = not use_direct
            time.sleep(2 * (a + 1))
    raise last

def pmap(fn, items, workers=24, label=""):
    """Parallel map preserving keys; errors are returned as {'error': ...}, never swallowed."""
    out = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, it): it for it in items}
        for i, f in enumerate(as_completed(futs), 1):
            it = futs[f]
            try:
                out[it] = f.result()
            except Exception as e:
                out[it] = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
            if i % 10 == 0 or i == len(items):
                print(f"  {label} {i}/{len(items)}  ${COST['usd']:.3f}  cached={COST['cached']}", flush=True)
    return out

# --- PDF text and mechanical location (§8.1 stage 2) ----------------------------------------
def pages(pm):
    """Text of each PDF page (1-based list index 0 = page 1), cached."""
    cp = os.path.join(CACHE, "text", f"{pm}.json")
    if os.path.exists(cp):
        return json.load(open(cp))
    r = subprocess.run(["pdftotext", "-layout", pdf_path(pm), "-"], capture_output=True)
    txt = r.stdout.decode("utf-8", errors="ignore")
    pg = txt.split("\f")
    if pg and not pg[-1].strip():
        pg = pg[:-1]
    json.dump(pg, open(cp, "w"))
    return pg

_LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "−": "-", "–": "-", "—": "-", "·": ".", " ": " "}
def _clean(s):
    for k, v in _LIG.items():
        s = s.replace(k, v)
    return s

def number_forms(x):
    """Textual forms a number may take in a paper: 71 -> '71'; 0.65 -> '0.65', '.65'; 85.05 ...
    Also the percentage/proportion twin (0.43 <-> 43), since papers switch between them."""
    if x is None:
        return set()
    x = float(x)
    forms = set()
    def add(v):
        for f in (f"{v:g}", f"{v:.1f}", f"{v:.2f}", f"{v:.3f}"):
            f = f.rstrip("0").rstrip(".") if "." in f else f
            forms.add(f)
            if f.startswith("0."):
                forms.add(f[1:])
            if f.startswith("-0."):
                forms.add("-" + f[2:])
            if abs(v) >= 1000 and float(v).is_integer():
                forms.add(f"{int(v):,}")
    add(x)
    if 0 < abs(x) <= 1:
        add(round(x * 100, 4))
    elif 1 < abs(x) <= 100:
        add(round(x / 100, 6))
    return {f for f in forms if f not in ("0", "1", "-0")} or {f"{x:g}"}

def find_number(text, x):
    """True if any textual form of x occurs as a whole number token in text."""
    t = _clean(text)
    for f in number_forms(x):
        if re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", t):
            return True
    return False

def _norm(s):
    return re.sub(r"[^a-z0-9%.]+", " ", _clean(s).lower()).split()

def quote_score(quote, text):
    """Share of the quote's word 4-grams present on the page (robust to line breaks, hyphens)."""
    q = _norm(quote)
    if len(q) < 4:
        return 1.0 if q and " ".join(q) in " ".join(_norm(text)) else 0.0
    tw = " " + " ".join(_norm(text)) + " "
    grams = [" ".join(q[i:i + 4]) for i in range(len(q) - 3)]
    return sum(1 for g in grams if f" {g} " in tw) / len(grams)

def locate(pm, values, quote):
    """Pages on which every given value occurs, and the best quote match.

    Returns {'pages_all_values': [...], 'best_quote_page': n, 'quote_score': s}.
    """
    pg = pages(pm)
    vals = [v for v in values if v is not None]
    hits = [i + 1 for i, t in enumerate(pg) if vals and all(find_number(t, v) for v in vals)]
    best, score = None, 0.0
    if quote:
        for i, t in enumerate(pg):
            s = quote_score(quote, t)
            if s > score:
                best, score = i + 1, s
    return {"pages_all_values": hits, "best_quote_page": best, "quote_score": round(score, 3),
            "n_pages": len(pg), "text_layer": sum(len(t) for t in pg) > 500}
