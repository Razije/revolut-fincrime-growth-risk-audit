"""Output writers for the growth and risk audit."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


TOP5_COLUMNS = [
    "priority_rank",
    "user_id",
    "priority_score",
    "fraud_events",
    "transaction_count",
    "fraud_rate_pct",
    "fraud_rate_wilson_lower_pct",
    "fraud_excess_z",
    "fraud_types",
    "fraud_type_list",
    "fraud_merchant_countries",
    "fraud_currencies",
    "repeatability_score",
    "conviction_score",
    "abnormality_score",
    "breadth_score",
    "severity_score",
    "severity_only_rank",
    "kyc_states",
    "selection_rationale",
]


def build_challenger_table(ranking: pd.DataFrame, top_n: int = 5, challenger_n: int = 5) -> pd.DataFrame:
    selected_ids = set(ranking.head(top_n)["user_id"])
    challengers = (
        ranking.loc[~ranking["user_id"].isin(selected_ids)]
        .sort_values(["severity_score", "priority_score"], ascending=False)
        .head(challenger_n)
        .copy()
    )
    challengers["why_not_selected"] = challengers.apply(
        lambda row: (
            f"Higher amount-severity signal alone was insufficient: composite rank {int(row['priority_rank'])}, "
            f"{int(row['fraud_events'])} confirmed events, repeatability {row['repeatability_score']:.1f}, "
            f"conviction {row['conviction_score']:.1f}, breadth {row['breadth_score']:.1f}."
        ),
        axis=1,
    )
    return challengers


def write_outputs(
    output_dir: str | Path,
    conversion: dict,
    overview: dict,
    ranking: pd.DataFrame,
    config: dict,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    top_n = int(config.get("top_n", 5))
    top5 = ranking.head(top_n).copy()
    challengers = build_challenger_table(ranking, top_n=top_n)

    ranking_path = output / "fraud_priority_ranking.csv"
    top5_path = output / "top_5_priority_targets.csv"
    challengers_path = output / "high_severity_not_selected.csv"
    summary_path = output / "audit_summary.json"
    report_path = output / "head_of_risk_brief.md"

    ranking.to_csv(ranking_path, index=False)
    top5[TOP5_COLUMNS].to_csv(top5_path, index=False)
    challengers.to_csv(challengers_path, index=False)

    summary = {
        "conversion": conversion,
        "risk_overview": overview,
        "risk_model": config,
        "top_5": top5[TOP5_COLUMNS].to_dict(orient="records"),
        "high_severity_not_selected": challengers[
            [
                "priority_rank",
                "user_id",
                "priority_score",
                "severity_score",
                "severity_only_rank",
                "fraud_events",
                "repeatability_score",
                "conviction_score",
                "breadth_score",
                "why_not_selected",
            ]
        ].to_dict(orient="records"),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report_path.write_text(_render_brief(conversion, overview, top5, challengers, config), encoding="utf-8")

    return {
        "ranking": ranking_path,
        "top5": top5_path,
        "challengers": challengers_path,
        "summary": summary_path,
        "brief": report_path,
    }


def _render_brief(conversion: dict, overview: dict, top5: pd.DataFrame, challengers: pd.DataFrame, config: dict) -> str:
    lines = [
        "# Head of Risk Brief: Growth Audit and Top 5 Priority Targets",
        "",
        "## Executive answer",
        "",
        (
            f"Marketing's rate is reproducible as **{conversion['marketing']['rate_pct']:.2f}%** "
            f"({conversion['marketing']['numerator']:,} / {conversion['marketing']['denominator']:,}). "
            f"The stricter repeat-use and no-confirmed-fraud proxy is "
            f"**{conversion['sustainable_proxy']['rate_pct']:.2f}%** "
            f"({conversion['sustainable_proxy']['numerator']:,} / {conversion['sustainable_proxy']['denominator']:,}), "
            f"a reduction of **{conversion['bridge']['total_pp']:.2f} percentage points**."
        ),
        "",
        (
            f"The dataset contains **{overview['confirmed_fraud_events']:,} confirmed-fraud events** involving "
            f"**{overview['users_with_confirmed_fraud']:,} users**. The Top 5 below are investigative priorities, "
            "not legal conclusions about identity or culpability."
        ),
        "",
        "## Top 5 investigative priorities",
        "",
        "| Rank | User ID | Score | Fraud events | Fraud rate | Types | Merchant countries | Severity-only rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in top5.iterrows():
        lines.append(
            f"| {int(row['priority_rank'])} | `{row['user_id']}` | {row['priority_score']:.1f} | "
            f"{int(row['fraud_events'])} | {row['fraud_rate_pct']:.1f}% | {int(row['fraud_types'])} | "
            f"{int(row['fraud_merchant_countries'])} | {int(row['severity_only_rank'])} |"
        )
    lines.extend(["", "### Why each target made the cut", ""])
    for _, row in top5.iterrows():
        lines.append(f"**#{int(row['priority_rank'])} `{row['user_id']}`.** {row['selection_rationale']}")
        lines.append("")

    lines.extend(
        [
            "## Why higher-amount users can rank below the Top 5",
            "",
            "`AMOUNT` is a transaction amount, not a realised-loss field, and the dataset spans multiple currencies. "
            "The model therefore never sums mixed-currency amounts. It converts each positive amount to a percentile "
            "within its transaction type and currency, then gives that severity signal only 10% weight. Repeatability, "
            "conservative fraud-rate conviction, excess fraud versus expected transaction mix, and attack breadth drive 90%.",
            "",
            "| Priority rank | High-severity non-selected user | Severity score | Fraud events | Repeatability | Conviction | Breadth | Why not selected |",
            "|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in challengers.iterrows():
        lines.append(
            f"| {int(row['priority_rank'])} | `{row['user_id']}` | {row['severity_score']:.1f} | "
            f"{int(row['fraud_events'])} | {row['repeatability_score']:.1f} | {row['conviction_score']:.1f} | "
            f"{row['breadth_score']:.1f} | {row['why_not_selected']} |"
        )

    lines.extend(
        [
            "",
            "## Model governance",
            "",
            "The ranking is deterministic and configurable in `risk_model.json`. Demographics, birth year and home "
            "country are excluded from the score. Merchant country is used only as operational attack breadth, not as "
            "an attribution of nationality. The file has no timestamps, device/IP data, counterparty network, case loss, "
            "chargeback or recovery fields; the ranking is therefore a triage queue for investigation, not an automated "
            "customer action or proof that a user is an attacker.",
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in conversion["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "- User-level priority should be independently reviewed before any restriction, filing or customer-impacting action.",
            "",
            f"Model version: `{config['version']}`. Generated deterministically from the supplied dataset.",
        ]
    )
    return "\n".join(lines) + "\n"
