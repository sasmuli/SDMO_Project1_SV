import pandas as pd

from script.dedupe_utils import email_parts, generic_alias, improved_rule, norm, split_name, surname


def test_norm_accents_and_case():
    assert norm("ÁndrÉ  Silva ") == "andre  silva"


def test_split_name_various_delims():
    assert split_name("Eric_Torre") == ["eric", "torre"]
    assert split_name("David.Britch") == ["david", "britch"]
    assert split_name("CESAR DELA TORRE")[-1] == "torre"


def test_surname():
    assert surname("Nish Anil") == "anil"
    assert surname("  ") == ""


def test_email_parts():
    assert email_parts("a.b@Microsoft.com") == ("a.b", "microsoft.com")
    assert email_parts("bad-email") == ("", "")


def test_generic_alias():
    assert generic_alias("david@users.noreply.github.com")
    assert generic_alias("david@host.local")
    assert not generic_alias("david@microsoft.com")


def test_improved_rule_basic_same_domain_and_surname():
    row = pd.Series(
        {
            "name_1": "David Britch",
            "name_2": "David Britch",
            "email_1": "david@contoso.com",
            "email_2": "david@contoso.com",
            "tok_sim": 0.85,
        }
    )
    # same surname + same domain + tok_sim >= 0.7 → True
    assert improved_rule(row) is True


def test_improved_rule_blocks_weak_match():
    row = pd.Series(
        {
            "name_1": "Kyle White",
            "name_2": "Kyle White",
            "email_1": "kyle@xamarin.com",
            "email_2": "k.white@other.com",
            "tok_sim": 0.85,
        }
    )
    # same surname but different domains → False
    assert improved_rule(row) is False


def test_improved_rule_rejects_noreply():
    row = pd.Series(
        {
            "name_1": "Eric Torre",
            "name_2": "ericuss",
            "email_1": "etorreg@gmail.com",
            "email_2": "eric@users.noreply.github.com",
            "tok_sim": 0.85,
        }
    )
    # New rule: hard reject noreply emails (security concern) → False
    assert improved_rule(row) is False
