"""PKR cost estimates and contractor quote checks. Prices come only from data/rates.csv, never from the AI."""
import os

import pandas as pd

import config

COLS = ["id", "kaam", "unit", "min_rs", "max_rs", "shehar", "tareekh", "source"]
ROOT = os.path.dirname(os.path.abspath(__file__))


def load_rates(path=None):
    """Load the rate table. Missing columns are added so new CSV rows never break the app."""
    path = path or os.path.join(ROOT, config.RATES_CSV)
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=COLS)
    for c in COLS:
        if c not in df.columns:
            df[c] = None
    df["min_rs"] = pd.to_numeric(df["min_rs"], errors="coerce")
    df["max_rs"] = pd.to_numeric(df["max_rs"], errors="coerce")
    df["id"] = df["id"].astype(str).str.strip()
    return df[COLS]


def priced(df):
    """Only the rows where both min_rs and max_rs are filled in."""
    return df[df["min_rs"].notna() & df["max_rs"].notna()]


def prompt_options(df):
    """Work list shown to the AI (ID and name only, never prices)."""
    return "\n".join("%s: %s (%s)" % (r.id, r.kaam, r.unit) for r in df.itertuples())


def estimate(work_ids, df, qty=0):
    """Rate range for each priced work item. If qty (sq ft) is given, 'sq ft' items also get a total."""
    out = []
    p = priced(df).set_index("id")
    for wid in work_ids:
        if wid not in p.index:
            continue
        r = p.loc[wid]
        item = {"id": wid, "kaam": r["kaam"], "unit": r["unit"], "min": float(r["min_rs"]),
                "max": float(r["max_rs"]), "total_min": None, "total_max": None}
        if qty and "sq ft" in str(r["unit"]).lower():
            item["total_min"] = item["min"] * qty
            item["total_max"] = item["max"] * qty
        out.append(item)
    return out


def pending(work_ids, df):
    """Work items chosen by the AI that exist in the table but have no price yet."""
    p_ids = set(priced(df)["id"])
    rows = df.set_index("id")
    return [{"id": w, "kaam": rows.loc[w, "kaam"], "unit": rows.loc[w, "unit"]}
            for w in work_ids if w in rows.index and w not in p_ids]


COLOR = {"very_low": "yellow", "fair": "green", "slightly_high": "yellow", "very_high": "red"}


def quote_check(job_id, qty, quote, df):
    p = priced(df).set_index("id")
    if job_id not in p.index or qty <= 0:
        return None
    r = p.loc[job_id]
    low, high = float(r["min_rs"]) * qty, float(r["max_rs"]) * qty
    if quote < low * config.QUOTE_LOW_FACTOR:
        v = "very_low"
    elif quote <= high:
        v = "fair"
    elif quote <= high * config.QUOTE_HIGH_FACTOR:
        v = "slightly_high"
    else:
        v = "very_high"
    return {"verdict": v, "low": low, "high": high, "color": COLOR[v]}
