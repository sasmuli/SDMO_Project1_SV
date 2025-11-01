# dedupe_utils.py
import re
import unicodedata


def norm(s: str) -> str:
    s = str(s)
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s.strip().lower()


def split_name(n: str):
    n = norm(n)
    parts = [p for p in re.split(r"[\s._\-\\]+", n) if p]
    return parts


def surname(n: str) -> str:
    parts = split_name(n)
    return parts[-1] if parts else ""


def email_parts(e: str):
    e = str(e)
    if "@" not in e:
        return ("", "")
    p, d = e.split("@", 1)
    return (p.lower(), d.lower())


def generic_alias(e: str) -> bool:
    e = str(e).lower()
    return ("users.noreply.github.com" in e) or (e.endswith(".lan") or ".local" in e)


# dedupe_utils.py
def improved_rule(row):
    name1, name2 = row["name_1"], row["name_2"]
    email1, email2 = row["email_1"], row["email_2"]
    tok_sim = row.get("tok_sim", 0.0)

    def email_parts(e):
        e = str(e)
        if "@" not in e:
            return ("", "")
        p, d = e.lower().split("@", 1)
        return p, d

    def surname(n):
        parts = re.split(r"[\s._\\\-]+", unicodedata.normalize("NFKD", str(n).lower()))
        parts = [p for p in parts if p]
        return parts[-1] if parts else ""

    def is_generic_alias(e):
        e = e.lower()
        return any(
            kw in e
            for kw in [
                "noreply",
                "users.noreply.github.com",
                ".lan",
                ".local",
                "bot",
                "ci",
                "automation",
            ]
        )

    p1, d1 = email_parts(email1)
    p2, d2 = email_parts(email2)
    s1, s2 = surname(name1), surname(name2)

    # 1. hard reject auto/bot style addresses (too risky)
    if is_generic_alias(email1) or is_generic_alias(email2):
        return False

    # 2. very strong signal:
    # same surname, same domain, and names are pretty similar
    if s1 and s2 and s1 == s2 and d1 == d2 and tok_sim >= 0.7:
        return True

    # 3. same prefix+domain and EXTREMELY similar names
    # this allows "same gmail" etc. but only if names are like exact match
    if (p1 == p2) and (d1 == d2) and tok_sim >= 0.90:
        return True

    return False
