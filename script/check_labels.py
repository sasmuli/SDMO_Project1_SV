from pathlib import Path

import pandas as pd

fn = r"project1devs\devs_similarity_t=0.72_labeled.xlsx"
p = Path(fn)
if not p.exists():
    print(f"❌ File not found:\n{p.resolve()}")
    raise SystemExit(1)

print(f"File found:\n{p.resolve()}")

df = pd.read_excel(fn, engine="openpyxl")
print(f"Loaded Excel (header=0). Shape: {df.shape}")


def normalize_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.upper().str.strip()


# Try to find a label-like column by name
label_col = None
for c in df.columns:
    if str(c).strip().lower() in {"label", "labels", "labeled", "annotation"}:
        label_col = c
        break


# If not found by name, try to detect by contents (TP/FP in any column)
def detect_label_column_by_contents(frame: pd.DataFrame):
    best_col = None
    best_hits = 0
    for c in frame.columns:
        hits = normalize_series(frame[c]).isin(["TP", "FP"]).sum()
        if hits > best_hits:
            best_hits = hits
            best_col = c
    return best_col, best_hits


if label_col is None:
    # First attempt: detect in the current df
    cand_col, hits = detect_label_column_by_contents(df)
    if hits == 0:
        # Second attempt: read with no header (Excel might not have a real header row)
        df_nohdr = pd.read_excel(fn, engine="openpyxl", header=None)
        print("Re-read with header=None to scan raw contents.")
        cand_col, hits = detect_label_column_by_contents(df_nohdr)
        if hits > 0:
            # Promote the no-header frame and synthesize a column name
            df = df_nohdr
            label_col = cand_col
        else:
            print(" Could not find any column containing 'TP' or 'FP'.")
            print("Columns in header=0 read:", list(df.columns))
            raise SystemExit(2)
    else:
        label_col = cand_col

print(f"Using label column: {label_col!r}")

lab = normalize_series(df[label_col])
tp = (lab == "TP").sum()
fp = (lab == "FP").sum()
total = len(df)
unl = total - tp - fp
prec = (tp / (tp + fp)) if (tp + fp) else float("nan")

# -------- 5) Show a compact summary --------
print("\n=== Results ===")
print(f"Rows       : {total}")
print(f"TP         : {tp}")
print(f"FP         : {fp}")
print(f"Unlabeled  : {unl}")
print(f"Precision  : {prec:.3f}")
