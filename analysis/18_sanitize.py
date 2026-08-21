"""Move non-proportional quantities out of proportion fields.

Extraction can be faithful to the source yet place a value in the wrong field:
Redfern 2003 reports a 30-fold hERG safety margin, which is not a proportion.
Leaving it in concordance_value keeps the audit permanently red and risks a
'3000%' rendering. This relocates such values, preserving them with their unit."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
P = os.path.join(ROOT, "data", "db", "fulltext_extract.json")
d = json.load(open(P))
moved = []
for pm, v in d.items():
    if "error" in v: continue
    for f in ("concordance_value", "sensitivity", "specificity", "ppv", "npv"):
        x = v.get(f)
        if isinstance(x, (int, float)) and not (0 <= x <= 1):
            v["reported_quantity"] = x
            v["reported_quantity_unit"] = v.get("concordance_metric") or f
            v["reported_quantity_note"] = f"moved from {f}: not a proportion"
            v[f] = None
            moved.append((pm, f, x))
json.dump(d, open(P, "w"), indent=1)
print(f"relocated {len(moved)} non-proportional value(s)")
for pm, f, x in moved: print(f"  {pm}: {x} out of {f}")
