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
def improved_rule(row) -> bool:
    c1 = float(row.get("c1", 0) or 0)
    name1, name2 = str(row.get("name_1", "")), str(row.get("name_2", ""))
    email1, email2 = str(row.get("email_1", "")), str(row.get("email_2", ""))

    s1, s2 = surname(name1), surname(name2)
    same_surname = s1 != "" and s1 == s2

    p1, d1 = email_parts(email1)
    p2, d2 = email_parts(email2)
    same_domain = d1 != "" and d1 == d2

    # NEW: treat prefix_match as strong only if long enough OR same domain
    prefixes_equal = p1 != "" and p1 == p2
    long_prefix = len(p1) >= 3  # tweakable threshold
    prefix_match_strong = prefixes_equal and (same_domain or long_prefix)

    any_noreply = generic_alias(email1) or generic_alias(email2)

    strong_name = (c1 >= 0.8) or same_surname
    strong_email = same_domain or prefix_match_strong or any_noreply

    return bool(strong_name and strong_email)
