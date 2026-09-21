"""Explainable ranking of confirmed-fraud users for investigative priority."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "risk_model.json"
COMPONENTS = [
    "repeatability_score",
    "conviction_score",
    "abnormality_score",
    "breadth_score",
    "severity_score",
]


def load_model_config(path: str | Path | None = None) -> dict:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with config_path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    weights = config["weights"]
    missing = set(COMPONENTS) - set(weights)
    if missing:
        raise ValueError(f"Missing model weights: {sorted(missing)}")
    if not np.isclose(sum(float(weights[name]) for name in COMPONENTS), 1.0):
        raise ValueError("Risk-model weights must sum to 1.0.")
    return config


def wilson_lower_bound(successes: pd.Series, trials: pd.Series, z: float = 1.96) -> pd.Series:
    successes = successes.astype(float)
    trials = trials.astype(float).clip(lower=1.0)
    phat = successes / trials
    denominator = 1.0 + z**2 / trials
    centre = phat + z**2 / (2.0 * trials)
    adjustment = z * np.sqrt((phat * (1.0 - phat) / trials) + (z**2 / (4.0 * trials**2)))
    return ((centre - adjustment) / denominator).clip(lower=0.0, upper=1.0)


def percentile_score(values: pd.Series) -> pd.Series:
    clean = values.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return clean.rank(method="average", pct=True) * 100.0


def _amount_percentiles(frame: pd.DataFrame) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    valid = frame["AMOUNT_NUMERIC"].gt(0) & frame["AMOUNT_NUMERIC"].notna()
    result.loc[valid] = (
        frame.loc[valid]
        .groupby(["TYPE", "CURRENCY"], observed=True)["AMOUNT_NUMERIC"]
        .rank(method="average", pct=True)
    )
    return result


def build_priority_ranking(frame: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    """Rank confirmed-fraud users using behaviour, conviction and breadth.

    Raw mixed-currency transaction totals are deliberately excluded. Severity is
    based on transaction-amount percentiles within TYPE × CURRENCY and receives
    only 10% of the composite weight.
    """
    config = config or load_model_config()
    working = frame.copy()
    working["AMOUNT_PERCENTILE"] = _amount_percentiles(working)

    global_type_rates = working.groupby("TYPE", observed=True)["IS_FRAUD_BOOL"].mean()
    user_type_counts = working.groupby(["USER_ID", "TYPE"], observed=True).size().unstack(fill_value=0)
    expected = user_type_counts.mul(global_type_rates, axis=1).sum(axis=1)

    base = working.groupby("USER_ID", sort=True).agg(
        transaction_count=("USER_ID", "size"),
        fraud_events=("IS_FRAUD_BOOL", "sum"),
        kyc_states=("KYC", lambda values: "|".join(sorted(set(values)))),
    )
    base["expected_fraud_events"] = expected.reindex(base.index).fillna(0.0)
    base = base.loc[base["fraud_events"] > 0].copy()
    base["fraud_rate_pct"] = 100.0 * base["fraud_events"] / base["transaction_count"]
    base["fraud_rate_wilson_lower_pct"] = 100.0 * wilson_lower_bound(
        base["fraud_events"], base["transaction_count"], float(config["wilson_z"])
    )
    base["fraud_excess_z"] = (
        base["fraud_events"] - base["expected_fraud_events"]
    ) / np.sqrt(base["expected_fraud_events"] + 0.5)

    fraud = working.loc[working["IS_FRAUD_BOOL"]].copy()
    fraud_group = fraud.groupby("USER_ID", sort=True)
    detail = fraud_group.agg(
        fraud_types=("TYPE", "nunique"),
        fraud_merchant_countries=("MERCHANT_COUNTRY", lambda v: v.replace("", np.nan).nunique()),
        fraud_currencies=("CURRENCY", lambda v: v.replace("", np.nan).nunique()),
        fraud_type_list=("TYPE", lambda v: ", ".join(sorted(set(v)))),
        fraud_merchant_country_list=("MERCHANT_COUNTRY", lambda v: ", ".join(sorted(set(x for x in v if x)))),
    )

    positive_fraud = fraud.loc[fraud["AMOUNT_PERCENTILE"].notna()]
    severity_top_n = int(config["severity_top_n_events"])
    severity = positive_fraud.groupby("USER_ID")["AMOUNT_PERCENTILE"].apply(
        lambda values: float(values.nlargest(severity_top_n).mean())
    )
    amount_breakdown = fraud_group.apply(
        lambda group: json.dumps(
            {
                str(currency): float(amount)
                for currency, amount in group.groupby("CURRENCY")["AMOUNT_NUMERIC"].sum(min_count=1).dropna().items()
            },
            sort_keys=True,
        ),
        include_groups=False,
    ).rename("recorded_fraud_amount_by_currency")

    ranking = base.join(detail, how="left").join(severity.rename("severity_raw"), how="left").join(amount_breakdown, how="left")
    ranking["severity_raw"] = ranking["severity_raw"].fillna(0.0)
    ranking["repeatability_score"] = percentile_score(np.log1p(ranking["fraud_events"]))
    ranking["conviction_score"] = percentile_score(ranking["fraud_rate_wilson_lower_pct"])
    ranking["abnormality_score"] = percentile_score(ranking["fraud_excess_z"])

    type_breadth = percentile_score(ranking["fraud_types"])
    market_breadth = percentile_score(ranking["fraud_merchant_countries"])
    currency_breadth = percentile_score(ranking["fraud_currencies"])
    ranking["breadth_score"] = 0.50 * type_breadth + 0.35 * market_breadth + 0.15 * currency_breadth
    ranking["severity_score"] = percentile_score(ranking["severity_raw"])

    ranking["priority_score"] = sum(
        ranking[name] * float(config["weights"][name]) for name in COMPONENTS
    )
    ranking = ranking.reset_index().rename(columns={"USER_ID": "user_id"})
    ranking = ranking.sort_values(
        ["priority_score", "fraud_events", "user_id"], ascending=[False, False, True]
    ).reset_index(drop=True)
    ranking["priority_rank"] = np.arange(1, len(ranking) + 1)
    ranking["severity_only_rank"] = ranking["severity_score"].rank(method="min", ascending=False).astype(int)

    ranking["selection_rationale"] = ranking.apply(_selection_rationale, axis=1)
    ordered = [
        "priority_rank",
        "user_id",
        "priority_score",
        "fraud_events",
        "transaction_count",
        "fraud_rate_pct",
        "fraud_rate_wilson_lower_pct",
        "expected_fraud_events",
        "fraud_excess_z",
        "fraud_types",
        "fraud_type_list",
        "fraud_merchant_countries",
        "fraud_merchant_country_list",
        "fraud_currencies",
        "repeatability_score",
        "conviction_score",
        "abnormality_score",
        "breadth_score",
        "severity_score",
        "severity_only_rank",
        "kyc_states",
        "recorded_fraud_amount_by_currency",
        "selection_rationale",
    ]
    return ranking[ordered]


def _selection_rationale(row: pd.Series) -> str:
    strengths = sorted(
        [
            ("repeatability", row["repeatability_score"]),
            ("conservative fraud-rate conviction", row["conviction_score"]),
            ("excess fraud versus transaction mix", row["abnormality_score"]),
            ("attack breadth", row["breadth_score"]),
            ("currency/type-normalised amount severity", row["severity_score"]),
        ],
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    strength_text = ", ".join(f"{name} ({score:.1f}/100)" for name, score in strengths)
    return (
        f"Priority rank {int(row['priority_rank'])}: {int(row['fraud_events'])} confirmed events across "
        f"{int(row['fraud_types'])} transaction type(s) and {int(row['fraud_merchant_countries'])} merchant "
        f"country/countries. Strongest signals: {strength_text}. Amount severity is capped at 10% of the score."
    )
