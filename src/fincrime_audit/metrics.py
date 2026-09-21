"""Reproducible growth and risk metrics."""

from __future__ import annotations

import pandas as pd


def _user_profile(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby("USER_ID", sort=True)
    profile = grouped.agg(
        transaction_count=("USER_ID", "size"),
        card_payments=("TYPE", lambda values: int((values == "CARD_PAYMENT").sum())),
        fraud_events=("IS_FRAUD_BOOL", "sum"),
        kyc_states=("KYC", lambda values: "|".join(sorted(set(values)))),
    )
    return profile


def conversion_metrics(frame: pd.DataFrame) -> dict:
    """Calculate the comparable Marketing and stricter audit rates."""
    profile = _user_profile(frame)
    total_users = int(len(profile))
    kyc_passed = profile.loc[profile["kyc_states"] == "PASSED"]
    denominator = int(len(kyc_passed))

    marketing_n = int((kyc_passed["card_payments"] >= 1).sum())
    quality_n = int(((kyc_passed["card_payments"] >= 1) & (kyc_passed["fraud_events"] == 0)).sum())
    sustainable_n = int(((kyc_passed["card_payments"] >= 2) & (kyc_passed["fraud_events"] == 0)).sum())

    def rate(numerator: int, denominator_value: int) -> float:
        return 100.0 * numerator / denominator_value if denominator_value else 0.0

    return {
        "rows": int(len(frame)),
        "unique_users": total_users,
        "kyc_passed_denominator": denominator,
        "marketing": {
            "numerator": marketing_n,
            "denominator": denominator,
            "rate_pct": rate(marketing_n, denominator),
            "definition": "At least one CARD_PAYMENT among users observed exclusively as KYC PASSED.",
        },
        "matured_quality": {
            "numerator": quality_n,
            "denominator": denominator,
            "rate_pct": rate(quality_n, denominator),
            "definition": "At least one CARD_PAYMENT and no confirmed fraud among the same users.",
        },
        "sustainable_proxy": {
            "numerator": sustainable_n,
            "denominator": denominator,
            "rate_pct": rate(sustainable_n, denominator),
            "definition": "At least two CARD_PAYMENT rows and no confirmed fraud among the same users.",
        },
        "bridge": {
            "fraud_screen_users": marketing_n - quality_n,
            "fraud_screen_pp": rate(marketing_n - quality_n, denominator),
            "repeat_use_users": quality_n - sustainable_n,
            "repeat_use_pp": rate(quality_n - sustainable_n, denominator),
            "total_users": marketing_n - sustainable_n,
            "total_pp": rate(marketing_n - sustainable_n, denominator),
        },
        "limitations": [
            "The file contains no app-install, sign-up or product-eligibility cohort.",
            "The file contains no timestamps, so distinct-day use, velocity, recency and fixed maturation windows cannot be calculated.",
            "The file contains no settlement, reversal, refund, chargeback or realised-loss field.",
            "Confirmed fraud is an ex-post label and should not silently rewrite a contemporaneous conversion KPI.",
        ],
    }


def risk_overview(frame: pd.DataFrame) -> dict:
    """Return portfolio-level confirmed-fraud metrics and type breakdown."""
    total_rows = int(len(frame))
    fraud = frame[frame["IS_FRAUD_BOOL"]]
    by_type = (
        frame.groupby("TYPE", as_index=False)
        .agg(transactions=("USER_ID", "size"), fraud_events=("IS_FRAUD_BOOL", "sum"))
        .assign(fraud_rate_pct=lambda d: 100.0 * d["fraud_events"] / d["transactions"])
        .sort_values("fraud_rate_pct", ascending=False)
    )
    return {
        "confirmed_fraud_events": int(len(fraud)),
        "confirmed_fraud_rate_pct": 100.0 * len(fraud) / total_rows,
        "users_with_confirmed_fraud": int(fraud["USER_ID"].nunique()),
        "nonpositive_amount_rows": int(frame["AMOUNT_NUMERIC"].le(0).fillna(False).sum()),
        "by_type": by_type.to_dict(orient="records"),
    }
