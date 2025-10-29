import re
import unicodedata

import pandas as pd

from dedupe_utils import improved_rule

fn = r".\project1devs\devs_similarity_t=0.7_labeled.xlsx"
df = pd.read_excel(fn, engine="openpyxl")


def norm(s):
    s = str(s)
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s.strip().lower()


def name_tokens(n):
    return [t for t in re.split(r"[\s._\-\\]+", norm(n)) if t]


def surn(n):
    t = name_tokens(n)
    return t[-1] if t else ""


def email_parts(e):
    e = str(e)
    if "@" not in e:
        return ("", "")
    p, d = e.split("@", 1)
    return (p.lower(), d.lower())


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def generic_alias(e):
    e = str(e).lower()
    return ("users.noreply.github.com" in e) or e.endswith(".lan") or (".local" in e)


# derive helpers
px1, dom1 = zip(*df["email_1"].map(email_parts))
px2, dom2 = zip(*df["email_2"].map(email_parts))
df["p1"] = px1
df["p2"] = px2
df["d1"] = dom1
df["d2"] = dom2
df["same_domain"] = df["d1"].eq(df["d2"])
df["prefix_eq"] = df["p1"].eq(df["p2"])
df["any_noreply"] = df["email_1"].map(generic_alias) | df["email_2"].map(generic_alias)

df["tok_sim"] = [
    jaccard(name_tokens(a), name_tokens(b)) for a, b in zip(df["name_1"], df["name_2"])
]
df["surname_eq"] = [surn(a) == surn(b) for a, b in zip(df["name_1"], df["name_2"])]

# Use improved_rule from dedupe_utils
df["c1"] = df["tok_sim"]
pred = df.apply(improved_rule, axis=1)

df["rule_pred"] = pred.map({True: "TP", False: "FP"})

# compare to your manual labels
lab = df["label"].astype(str).str.upper().str.strip()
mask_labeled = lab.isin(["TP", "FP"])
tp = ((df["rule_pred"] == "TP") & (lab == "TP") & mask_labeled).sum()
fp = ((df["rule_pred"] == "TP") & (lab == "FP") & mask_labeled).sum()
tn = ((df["rule_pred"] == "FP") & (lab == "FP") & mask_labeled).sum()
fn = ((df["rule_pred"] == "FP") & (lab == "TP") & mask_labeled).sum()

prec = tp / (tp + fp) if (tp + fp) else float("nan")
rec = tp / (tp + fn) if (tp + fn) else float("nan")
f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) else float("nan")

print(f"Labeled rows used: {mask_labeled.sum()} of {len(df)}")
print(f"TP={tp}  FP={fp}  TN={tn}  FN={fn}")
print(f"Precision={prec:.3f}  Recall={rec:.3f}  F1={f1:.3f}")

# Optional: write a preview of disagreements to inspect
err = df.loc[
    mask_labeled & (df["rule_pred"] != lab),
    [
        "name_1",
        "email_1",
        "name_2",
        "email_2",
        "tok_sim",
        "prefix_eq",
        "same_domain",
        "any_noreply",
        "surname_eq",
        "rule_pred",
    ],
]
err.to_excel(r".\project1devs\disagreements.xlsx", index=False)
print("Wrote disagreements.xlsx for spot checks.")
