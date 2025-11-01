# analyze_patterns.py
import re
import sys
import unicodedata

import pandas as pd

fn = r"project1devs\devs_similarity_t=0.72_labeled.xlsx"
df = pd.read_excel(fn, engine="openpyxl")

print("Columns found:", list(df.columns))


def normalize_upper(s: pd.Series) -> pd.Series:
    # normalize text for robust matching
    return s.astype(str).str.upper().str.strip()


# 1) Detect label column by contents (TP/FP) – works even if it's "Column13"
hits = {}
for c in df.columns:
    try:
        hits[c] = normalize_upper(df[c]).isin(["TP", "FP"]).sum()
    except Exception:
        hits[c] = 0

label_col = max(hits, key=hits.get)
if hits[label_col] == 0:
    sys.exit(
        "No TP/FP labels found in any column. Open the file and check which column has the labels."
    )

print(f"Using label column: {label_col!r}")

lab = normalize_upper(df[label_col])
# Also accept TRUE/FALSE or 1/0 in case you used booleans
lab = lab.replace({"TRUE": "TP", "FALSE": "FP", "1": "TP", "0": "FP"})

df["is_tp"] = lab.eq("TP")
df["is_fp"] = lab.eq("FP")


# 2) Use your renamed identity columns
# If you changed headers to name_1, email_1, name_2, email_2 this will work.
# If not, it will fall back to first 4 columns.
def get_or_fallback(name, idx):
    if name in df.columns:
        return name
    return df.columns[idx]


name1 = get_or_fallback("name_1", 0)
email1 = get_or_fallback("email_1", 1)
name2 = get_or_fallback("name_2", 2)
email2 = get_or_fallback("email_2", 3)

print(
    f"Detected identity columns:\n  name_1  -> {name1}\n  email_1 -> {email1}\n  name_2  -> {name2}\n  email_2 -> {email2}"
)


# 3) Helpers
def norm_txt(s):
    s = str(s)
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s.strip().lower()


def split_name(n):
    return [p for p in re.split(r"[\s._\\-]+", norm_txt(n)) if p]


def surname(n):
    t = split_name(n)
    return t[-1] if t else ""


def email_parts(e):
    e = str(e)
    if "@" not in e:
        return ("", "")
    p, d = e.split("@", 1)
    return (p.lower(), d.lower())


def is_generic_alias(e):
    e = str(e).lower()
    return ("users.noreply.github.com" in e) or e.endswith(".lan") or (".local" in e)


# 4) Features
df["surname_1"] = df[name1].apply(surname)
df["surname_2"] = df[name2].apply(surname)
df["same_surname"] = df["surname_1"].eq(df["surname_2"])

p1, d1 = zip(*df[email1].map(email_parts))
p2, d2 = zip(*df[email2].map(email_parts))
df["p1"], df["d1"], df["p2"], df["d2"] = p1, d1, p2, d2

df["same_domain"] = df["d1"].eq(df["d2"])
df["prefix_match"] = df["p1"].eq(df["p2"])
df["any_noreply"] = df[email1].map(is_generic_alias) | df[email2].map(is_generic_alias)

# 5) Breakdown
print("\n--- FP breakdown ---")
for col in ["same_domain", "same_surname", "any_noreply", "prefix_match"]:
    vc = df.loc[df["is_fp"], col].value_counts(dropna=False)
    print(col, dict(vc))

print("\n--- TP breakdown ---")
for col in ["same_domain", "same_surname", "any_noreply", "prefix_match"]:
    vc = df.loc[df["is_tp"], col].value_counts(dropna=False)
    print(col, dict(vc))
