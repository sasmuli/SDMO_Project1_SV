import pandas as pd

from dedupe_utils import improved_rule


def test_rule_precision_on_tiny_sample():
    data = [
        # TP
        {
            "name_1": "David Britch",
            "email_1": "d@x.com",
            "name_2": "David Britch",
            "email_2": "d@x.com",
            "c1": 0.7,
            "label": "TP",
        },
        # TP via noreply
        {
            "name_1": "Eric Torre",
            "email_1": "et@gmail.com",
            "name_2": "Eric",
            "email_2": "e@users.noreply.github.com",
            "c1": 0.9,
            "label": "TP",
        },
        # FP (same first name, different domains/prefix)
        {
            "name_1": "Kyle White",
            "email_1": "k@xamarin.com",
            "name_2": "Kyle White",
            "email_2": "k@other.com",
            "c1": 0.7,
            "label": "FP",
        },
    ]
    df = pd.DataFrame(data)
    pred = df.apply(improved_rule, axis=1)
    tp = ((pred == True) & (df["label"] == "TP")).sum()
    fp = ((pred == True) & (df["label"] == "FP")).sum()
    assert tp == 2 and fp == 0
