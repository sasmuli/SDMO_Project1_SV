import csv
import os
import string
import unicodedata
from itertools import combinations

import pandas as pd
from Levenshtein import ratio as sim
from pydriller import Repository

# === CONFIG ===
REPO_URL = "https://github.com/public-apis/public-apis"
OUTPUT_DIR = "project1devs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DEVS = set()

print("Mining repository:", REPO_URL)
for commit in Repository(REPO_URL).traverse_commits():
    # author
    DEVS.add((commit.author.name, commit.author.email))
    # committer (can be different person)
    DEVS.add((commit.committer.name, commit.committer.email))

print(f"Total raw (name,email) pairs collected: {len(DEVS)}")

devs_csv_path = os.path.join(OUTPUT_DIR, "devs.csv")
with open(devs_csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=",", quotechar='"')
    writer.writerow(["name", "email"])
    for name, email in sorted(DEVS):
        writer.writerow([name, email])

print(f"Wrote unique developers to {devs_csv_path}")

# Reload developer list from CSV so we have a clean list
DEVS = []
with open(devs_csv_path, "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader)  # skip header
    for row in reader:
        DEVS.append(row)

# First element is header, skip (defensive)
DEVS = DEVS[1:]


# --- Helper: normalize a developer (name/email) ---
def process(dev):
    """
    Takes a dev row [name, email] and returns:
    normalized full name,
    first name,
    last name,
    first initial,
    last initial,
    original email,
    email prefix (before @)
    """
    name: str = dev[0]

    # Remove punctuation
    trans = name.maketrans("", "", string.punctuation)
    name = name.translate(trans)

    # Remove accents/diacritics
    name = unicodedata.normalize("NFKD", name)
    name = "".join([c for c in name if not unicodedata.combining(c)])

    # Lowercase
    name = name.casefold()

    # Collapse whitespace
    name = " ".join(name.split())

    # Split into first / last
    parts = name.split(" ")
    if len(parts) == 2:
        first, last = parts
    elif len(parts) == 1:
        first, last = name, ""
    else:
        first, last = parts[0], " ".join(parts[1:])

    # initials
    i_first = first[0] if len(first) > 1 else ""
    i_last = last[0] if len(last) > 1 else ""

    # email + prefix
    email: str = dev[1]
    prefix = email.split("@")[0]

    return name, first, last, i_first, i_last, email, prefix


# --- Build all pairwise similarity rows ---
SIMILARITY = []
for dev_a, dev_b in combinations(DEVS, 2):
    # Pre-process both developers
    (
        name_a,
        first_a,
        last_a,
        i_first_a,
        i_last_a,
        email_a,
        prefix_a,
    ) = process(dev_a)

    (
        name_b,
        first_b,
        last_b,
        i_first_b,
        i_last_b,
        email_b,
        prefix_b,
    ) = process(dev_b)

    # Bird-style heuristic similarity signals
    c1 = sim(name_a, name_b)  # full normalized name similarity
    c2 = sim(prefix_b, prefix_a)  # email prefix similarity
    c31 = sim(first_a, first_b)  # first name similarity
    c32 = sim(last_a, last_b)  # last name similarity

    # Boolean heuristic checks based on initials in email usernames
    c4 = c5 = c6 = c7 = False

    # If we have enough info, check if email prefix embeds initials + lastname, etc.
    if i_first_a != "" and last_a != "":
        c4 = i_first_a in prefix_b and last_a in prefix_b
    if i_last_a != "":
        c5 = i_last_a in prefix_b and first_a in prefix_b
    if i_first_b != "" and last_b != "":
        c6 = i_first_b in prefix_a and last_b in prefix_a
    if i_last_b != "":
        c7 = i_last_b in prefix_a and first_b in prefix_a

    # Save row (use ORIGINAL names/emails for labeling)
    SIMILARITY.append(
        [
            dev_a[0],
            email_a,
            dev_b[0],
            email_b,
            c1,
            c2,
            c31,
            c32,
            c4,
            c5,
            c6,
            c7,
        ]
    )

# --- Build dataframe of all pairs ---
cols = [
    "name_1",
    "email_1",
    "name_2",
    "email_2",
    "c1",
    "c2",
    "c3.1",
    "c3.2",
    "c4",
    "c5",
    "c6",
    "c7",
]
df = pd.DataFrame(SIMILARITY, columns=cols)

# Save the full unfiltered pairs (optional, for traceability)
df.to_csv(
    os.path.join(OUTPUT_DIR, "devs_similarity.csv"),
    index=False,
    header=True,
)

# --- Thresholding phase for manual labeling set ---
t = 0.8
print("Threshold:", t)

# High-confidence checks (numerical scores)
df["c1_check"] = df["c1"] >= t
df["c2_check"] = df["c2"] >= t
df["c3_check"] = (df["c3.1"] >= t) & (df["c3.2"] >= t)

# For manual labeling:
# Only keep strong similarity matches (c1/c2/c3),
# and IGNORE the looser heuristics c4..c7 here.
df = df[df[["c1_check", "c2_check", "c3_check"]].any(axis=1)]

# Drop helper columns before saving final CSV
df = df[
    [
        "name_1",
        "email_1",
        "name_2",
        "email_2",
        "c1",
        "c2",
        "c3.1",
        "c3.2",
        "c4",
        "c5",
        "c6",
        "c7",
    ]
]

print("Pairs after thresholding:", len(df))

outfile = os.path.join(OUTPUT_DIR, f"devs_similarity_t={t}.csv")
df.to_csv(outfile, index=False, header=True)
print("Wrote:", outfile)
