import pandas as pd

from script.dedupe_utils import improved_rule


def test_rule_precision_on_tiny_sample():
    data = [
        # TP: same surname + same domain + high tok_sim
        {
            "name_1": "David Britch",
            "email_1": "david@microsoft.com",
            "name_2": "David Britch",
            "email_2": "d.britch@microsoft.com",
            "tok_sim": 0.85,
            "label": "TP",
        },
        # TP: same prefix+domain + very high tok_sim
        {
            "name_1": "Eric Torre",
            "email_1": "etorre@gmail.com",
            "name_2": "Eric Torre",
            "email_2": "etorre@gmail.com",
            "tok_sim": 0.95,
            "label": "TP",
        },
        # FP: same surname but different domains
        {
            "name_1": "Kyle White",
            "email_1": "kyle@xamarin.com",
            "name_2": "Kyle White",
            "email_2": "k.white@other.com",
            "tok_sim": 0.85,
            "label": "FP",
        },
    ]
    df = pd.DataFrame(data)
    pred = df.apply(improved_rule, axis=1)
    tp = ((pred == True) & (df["label"] == "TP")).sum()
    fp = ((pred == True) & (df["label"] == "FP")).sum()
    assert tp == 2 and fp == 0
