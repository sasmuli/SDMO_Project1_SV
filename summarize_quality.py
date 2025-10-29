from pathlib import Path

root = Path("reports/quality")
files = {
    "flake8": "flake8.txt",
    "pylint": "pylint.txt",
    "radon_cc": "radon-cc.txt",
    "radon_mi": "radon-mi.txt",
    "bandit": "bandit.txt",
    "mypy": "mypy.txt",
}

out = ["# Quality Summary (auto)\n"]

# Pylint score
try:
    with open(root / files["pylint"], "r", encoding="utf-8", errors="replace") as f:
        lines = [ln.replace('\x00', '') for ln in f.readlines()]
    score_line = next((ln.strip() for ln in lines if "Your code has been rated at" in ln), None)
    if score_line:
        out.append(f"- **Pylint**: {score_line}")
    else:
        out.append("- **Pylint**: score line not found")
        print(f"DEBUG: Read {len(lines)} lines from pylint.txt")
except Exception as e:
    out.append(f"- **Pylint**: Error reading file - {e}")

# Flake8 count
f = (root / files["flake8"]).read_text(encoding="utf-8", errors="ignore")
flake_count = 0 if not f.strip() else len(f.splitlines())
out.append(f"- **Flake8**: {flake_count} issues reported")

# Radon CC (C or worse)
try:
    cc = (root / files["radon_cc"]).read_text(encoding="utf-8", errors="ignore")
    hot = [ln.strip() for ln in cc.splitlines() if " - " in ln and (") C" in ln or ") D" in ln or ") E" in ln or ") F" in ln)]
    out.append("### Highest cyclomatic complexity (C or worse)")
    if hot:
        out.extend(f"  - {ln}" for ln in hot[:8])
    else:
        out.append("  - none >= C")
except Exception as e:
    out.append(f"### Radon CC: Error - {e}")

# Maintainability (compute average if not found)
try:
    with open(root / files["radon_mi"], "r", encoding="utf-8", errors="replace") as f:
        mi_lines = [ln.replace('\x00', '') for ln in f.readlines()]
    lines = [ln for ln in mi_lines if ".py - " in ln and "(" in ln and ")" in ln]
    scores = []
    for ln in lines:
        try:
            val = float(ln.split("(")[-1].split(")")[0])
            scores.append(val)
        except Exception:
            pass
    avg = sum(scores) / len(scores) if scores else 0
    out.append(f"- **Maintainability**: Average MI = {avg:.2f} ({len(scores)} files)")
    if not scores:
        print(f"DEBUG: Read {len(mi_lines)} lines, found {len(lines)} matching lines")
except Exception as e:
    out.append(f"- **Maintainability**: Error - {e}")


# Bandit summary
try:
    b = (root / files["bandit"]).read_text(encoding="utf-8", errors="ignore")
    sev_high = sum("Severity: High" in ln for ln in b.splitlines())
    sev_med  = sum("Severity: Medium" in ln for ln in b.splitlines())
    out.append(f"- **Bandit**: High={sev_high}, Medium={sev_med}")
except Exception as e:
    out.append(f"- **Bandit**: Error - {e}")

(root / "summary.md").write_text("\n".join(out), encoding="utf-8")
print("Wrote reports/quality/summary.md")
