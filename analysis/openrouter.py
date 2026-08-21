"""OpenRouter client. Key is read from .env (gitignored) and never logged."""
import os, json, time, hashlib, urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "screening", "llm_cache")
os.makedirs(CACHE, exist_ok=True)

def _key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        env = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env):
            for line in open(env):
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip("'\"")
    if not k:
        raise RuntimeError("OPENROUTER_API_KEY not found (.env is gitignored; see .env.example)")
    return k

def chat(model, messages, schema=None, temperature=0, max_tokens=400, retries=5):
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens}
    if schema:
        body["response_format"] = {"type": "json_schema",
                                   "json_schema": {"name": "screen", "strict": True, "schema": schema}}
    ck = hashlib.sha1(json.dumps(body, sort_keys=True).encode()).hexdigest()[:24]
    path = os.path.join(CACHE, f"{ck}.json")
    if os.path.exists(path):
        return json.load(open(path))
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
                "Authorization": f"Bearer {_key()}", "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/animal-model-concordance",
                "X-Title": "animal-model-concordance"})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode())
            if "choices" not in d:
                last = RuntimeError(f"no choices: {str(d)[:300]}")
                time.sleep(3 * (a + 1)); continue
            json.dump(d, open(path, "w"))
            return d
        except urllib.error.HTTPError as e:
            detail = ""
            try: detail = e.read().decode()[:300]
            except Exception: pass
            last = RuntimeError(f"HTTP {e.code}: {detail}")
            # 429/402/5xx are transient or capacity-related; back off hard.
            time.sleep(min(60, 5 * (2 ** a)))
        except Exception as e:
            last = e
            time.sleep(3 * (a + 1))
    raise last

def content(d):
    return d["choices"][0]["message"]["content"]

def usd(d):
    u = d.get("usage") or {}
    return u.get("cost", 0.0)
