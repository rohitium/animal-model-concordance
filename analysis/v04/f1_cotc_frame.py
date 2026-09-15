"""Sampling frame 1 (PLAN.md v0.4 §7.2): every NCI Comparative Oncology Trials Consortium trial.

Parses the program's open and completed trial pages into one record per trial. The agent tested
and any human counterpart are identified later, per trial, so nothing is filtered here.
Output: data/v04/frames/cotc.json
"""
import sys, os, re, html, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

BASE = "https://ccr.cancer.gov/comparative-oncology-program/"
UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/124 Safari/537.36"

def text_of(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="ignore")
    m = raw.find("<main")
    raw = raw[m:] if m > 0 else raw
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", raw))
    return [ln.strip() for ln in t.split("\n") if ln.strip()]

def parse(lines, status):
    trials, cur, field = [], None, None
    head = re.compile(r"^(COTC\s?\d{3}[A-Za-z]?(?:\s+Study\s+\d+)?)\s*:\s*(.+)$")
    for ln in lines:
        m = head.match(ln)
        if m:
            cur = {"trial_id": m.group(1).replace(" ", " "), "title": m.group(2), "status": status,
                   "purpose": "", "publications": []}
            trials.append(cur); field = None
            continue
        if cur is None:
            continue
        low = ln.rstrip(":").lower()
        if low in ("purpose", "participating sites", "sponsor", "study numbers",
                   "eligibility requirements", "publication", "publications", "learn more"):
            field = low
            continue
        if ln.startswith(("Main navigation", "Additional Clinical Trials", "Return to top")):
            cur, field = None, None
            continue
        if field == "purpose" or (status == "open" and field is None):
            cur["purpose"] = (cur["purpose"] + " " + ln).strip()
        elif field in ("publication", "publications"):
            cur["publications"].append(ln)
    return trials

def main():
    frame = parse(text_of(BASE + "closed-trials"), "completed") + parse(text_of(BASE + "trials"), "open")
    save({"source": BASE + "closed-trials ; " + BASE + "trials", "retrieved": today(),
          "n": len(frame), "trials": frame}, "frames/cotc.json")
    print(f"COTC frame: {len(frame)} trials "
          f"({sum(t['status']=='completed' for t in frame)} completed, "
          f"{sum(bool(t['publications']) for t in frame)} with a listed publication)")
    for t in frame:
        print(" ", t["trial_id"], "|", t["title"][:90])

if __name__ == "__main__":
    main()
