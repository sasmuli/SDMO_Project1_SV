import pandas as pd

from dedupe_utils import email_parts, generic_alias, improved_rule, norm, split_name, surname


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
            "c1": 0.6,
        }
    )
    # same surname + same domain → True even if c1<0.8
    assert improved_rule(row) is True


def test_improved_rule_blocks_weak_match():
    row = pd.Series(
        {
            "name_1": "Kyle White",
            "name_2": "Kyle White",
            "email_1": "kyle@xamarin.com",
            "email_2": "k.white@other.com",
            "c1": 0.6,
        }
    )
    # strong_name? yes (same surname). strong_email? no → False
    assert improved_rule(row) is False


def test_improved_rule_noreply_allows():
    row = pd.Series(
        {
            "name_1": "Eric Torre",
            "name_2": "ericuss",
            "email_1": "etorreg@gmail.com",
            "email_2": "eric@users.noreply.github.com",
            "c1": 0.85,
        }
    )
    # c1>=0.8 and any_noreply → True
    assert improved_rule(row) is True
