"""Interactive Streamlit dashboard for the growth and fraud-priority audit."""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fincrime_audit import build_priority_ranking, conversion_metrics, load_model_config, load_transactions, risk_overview
from fincrime_audit.reporting import build_challenger_table

st.set_page_config(page_title="Growth & Financial-Crime Audit", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1420px;}
    [data-testid="stMetric"] {background: #f5f8fb; border: 1px solid #dce5ee; padding: 14px; border-radius: 12px;}
    .risk-note {padding: 14px 16px; border-left: 4px solid #a31d37; background: #faedf0; border-radius: 6px;}
    .good-note {padding: 14px 16px; border-left: 4px solid #0b7355; background: #eaf6f0; border-radius: 6px;}
    code {font-size: .88em;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def analyse_bytes(data: bytes, filename: str, config: dict):
    buffer = io.BytesIO(data)
    buffer.name = filename
    frame = load_transactions(buffer)
    return frame, conversion_metrics(frame), risk_overview(frame), build_priority_ranking(frame, config)


@st.cache_data(show_spinner=False)
def analyse_path(path: str, config: dict):
    frame = load_transactions(path)
    return frame, conversion_metrics(frame), risk_overview(frame), build_priority_ranking(frame, config)


@st.cache_data(show_spinner=False)
def load_published_results(summary_path: str, ranking_path: str):
    with Path(summary_path).open(encoding="utf-8") as handle:
        summary = json.load(handle)
    ranking = pd.read_csv(ranking_path)
    return None, summary["conversion"], summary["risk_overview"], ranking


def source_selector(config: dict):
    st.sidebar.header("Dataset")
    allow_upload = os.getenv("FINCRIME_ALLOW_UPLOAD", "true").lower() in {"1", "true", "yes"}
    uploaded = st.sidebar.file_uploader("Upload CSV or ZIP", type=["csv", "zip"]) if allow_upload else None
    configured = os.getenv("FINCRIME_DATA", "")
    if uploaded is not None:
        return analyse_bytes(uploaded.getvalue(), uploaded.name, config)
    if configured and Path(configured).exists():
        st.sidebar.success(f"Using configured file: {Path(configured).name}")
        return analyse_path(configured, config)
    summary_path = ROOT / "outputs" / "audit_summary.json"
    ranking_path = ROOT / "outputs" / "fraud_priority_ranking.csv"
    if summary_path.exists() and ranking_path.exists():
        st.sidebar.success("Using the published challenge results")
        st.sidebar.caption("The public deployment contains derived audit outputs only; the raw transaction file is not deployed.")
        return load_published_results(str(summary_path), str(ranking_path))
    st.sidebar.info("Upload `fin_crime_data.csv` or its ZIP archive to begin.")
    st.stop()


def conversion_tab(conversion: dict):
    st.subheader("Growth audit: 78.2% is reproducible, but it is not an app-funnel rate")
    a, b, c, d = st.columns(4)
    a.metric("Marketing reconstruction", f"{conversion['marketing']['rate_pct']:.1f}%", help=conversion["marketing"]["definition"])
    b.metric("Matured one-event quality", f"{conversion['matured_quality']['rate_pct']:.1f}%", f"−{conversion['bridge']['fraud_screen_pp']:.1f} pp")
    c.metric("Sustainable repeat-use proxy", f"{conversion['sustainable_proxy']['rate_pct']:.1f}%", f"−{conversion['bridge']['total_pp']:.1f} pp")
    d.metric("Comparable denominator", f"{conversion['kyc_passed_denominator']:,}", "Observed KYC PASSED only")

    chart = pd.DataFrame(
        [
            {"Definition": "Marketing: ≥1 card payment", "Rate": conversion["marketing"]["rate_pct"]},
            {"Definition": "After confirmed-fraud screen", "Rate": conversion["matured_quality"]["rate_pct"]},
            {"Definition": "Repeat use + no confirmed fraud", "Rate": conversion["sustainable_proxy"]["rate_pct"]},
        ]
    )
    fig = px.bar(
        chart,
        x="Rate",
        y="Definition",
        orientation="h",
        text=chart["Rate"].map(lambda value: f"{value:.1f}%"),
        color="Definition",
        color_discrete_sequence=["#a31d37", "#2f65a7", "#0b7355"],
    )
    fig.update_layout(showlegend=False, xaxis_title="Share of 6,989 observed KYC-PASSED users (%)", yaxis_title="", height=360)
    fig.update_xaxes(range=[65, 80], ticksuffix="%", gridcolor="#dfe6ed")
    fig.update_traces(textposition="outside", hovertemplate="%{y}<br>%{x:.2f}%<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div class="good-note"><strong>Reconciliation.</strong> The stricter rate removes
        <strong>{conversion['bridge']['fraud_screen_users']:,} users</strong> through the confirmed-fraud screen and
        <strong>{conversion['bridge']['repeat_use_users']:,} further users</strong> through the repeat-use requirement.
        The total difference is <strong>{conversion['bridge']['total_pp']:.2f} percentage points</strong> on the same denominator.</div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Data limitations"):
        for item in conversion["limitations"]:
            st.write(f"- {item}")


def overview_tab(frame: pd.DataFrame | None, overview: dict):
    st.subheader("Confirmed-fraud risk overview")
    a, b, c, d = st.columns(4)
    a.metric("Confirmed-fraud events", f"{overview['confirmed_fraud_events']:,}")
    b.metric("Fraud event rate", f"{overview['confirmed_fraud_rate_pct']:.2f}%")
    c.metric("Users with confirmed fraud", f"{overview['users_with_confirmed_fraud']:,}")
    d.metric("Non-positive amount rows", f"{overview['nonpositive_amount_rows']:,}", help="Excluded from amount-severity scoring.")

    by_type = pd.DataFrame(overview["by_type"])
    left, right = st.columns([1.05, 1])
    with left:
        fig = px.bar(
            by_type,
            x="TYPE",
            y="fraud_rate_pct",
            text=by_type["fraud_rate_pct"].map(lambda value: f"{value:.1f}%"),
            color="fraud_rate_pct",
            color_continuous_scale=["#dce8f5", "#a31d37"],
        )
        fig.update_layout(coloraxis_showscale=False, yaxis_title="Confirmed-fraud rate (%)", xaxis_title="", height=390)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        if frame is not None:
            fraud = frame.loc[frame["IS_FRAUD_BOOL"]]
            method = fraud.groupby("TYPE", as_index=False).size().rename(columns={"size": "Fraud events"})
        else:
            method = by_type[["TYPE", "fraud_events"]].rename(columns={"fraud_events": "Fraud events"})
        fig = px.pie(method, names="TYPE", values="Fraud events", hole=.55, color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(height=390, title="Confirmed-fraud event mix")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("Transaction amount is not treated as realised financial loss. Mixed currencies are not summed into one portfolio-loss figure.")


def targets_tab(ranking: pd.DataFrame, config: dict):
    top_n = int(config["top_n"])
    top5 = ranking.head(top_n).copy()
    challengers = build_challenger_table(ranking, top_n=top_n)

    st.subheader("Top 5 users for Head-of-Risk investigative priority")
    st.markdown(
        """
        <div class="risk-note"><strong>Interpretation:</strong> this is a triage priority list, not a legal finding.
        The model ranks only users with confirmed-fraud records. It excludes demographics and gives amount severity only 10%
        weight because <code>AMOUNT</code> is not a loss field and currencies are mixed.</div>
        """,
        unsafe_allow_html=True,
    )

    display = top5[
        [
            "priority_rank", "user_id", "priority_score", "fraud_events", "fraud_rate_pct",
            "fraud_types", "fraud_merchant_countries", "repeatability_score", "conviction_score",
            "abnormality_score", "breadth_score", "severity_score", "severity_only_rank"
        ]
    ].copy()
    numeric = [column for column in display.columns if column not in {"priority_rank", "user_id", "fraud_events", "fraud_types", "fraud_merchant_countries", "severity_only_rank"}]
    display[numeric] = display[numeric].round(1)
    st.dataframe(display, hide_index=True, use_container_width=True)

    score_long = top5.melt(
        id_vars=["priority_rank", "user_id"],
        value_vars=["repeatability_score", "conviction_score", "abnormality_score", "breadth_score", "severity_score"],
        var_name="Component",
        value_name="Score",
    )
    score_long["Target"] = score_long["priority_rank"].map(lambda value: f"#{value}")
    fig = px.bar(score_long, x="Score", y="Target", color="Component", orientation="h", barmode="stack")
    fig.update_layout(height=420, xaxis_title="Component percentile points (before weighting)", yaxis_title="", legend_title="Signal")
    st.plotly_chart(fig, use_container_width=True)

    for _, row in top5.iterrows():
        with st.expander(f"#{int(row['priority_rank'])} · {row['user_id']} · priority score {row['priority_score']:.1f}"):
            st.write(row["selection_rationale"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Confirmed events", f"{int(row['fraud_events'])}")
            c2.metric("Fraud rate", f"{row['fraud_rate_pct']:.1f}%")
            c3.metric("Fraud methods", f"{int(row['fraud_types'])}")
            c4.metric("Merchant countries", f"{int(row['fraud_merchant_countries'])}")
            st.caption(f"Observed fraud types: {row['fraud_type_list']}. KYC states: {row['kyc_states']}.")

    st.markdown("### Higher-severity users that were not selected")
    st.write(
        "These users have strong currency/type-normalised amount signals, but rank below the Top 5 because recurrence, "
        "conservative fraud-rate conviction, anomaly versus transaction mix, and attack breadth carry 90% of the model."
    )
    challenge_display = challengers[
        ["priority_rank", "user_id", "priority_score", "severity_score", "severity_only_rank", "fraud_events", "repeatability_score", "conviction_score", "breadth_score", "why_not_selected"]
    ].copy()
    for column in ["priority_score", "severity_score", "repeatability_score", "conviction_score", "breadth_score"]:
        challenge_display[column] = challenge_display[column].round(1)
    st.dataframe(challenge_display, hide_index=True, use_container_width=True)

    st.download_button(
        "Download Top 5 CSV",
        top5.to_csv(index=False).encode("utf-8"),
        file_name="top_5_priority_targets.csv",
        mime="text/csv",
    )


def methodology_tab(config: dict):
    st.subheader("Explainable priority model")
    weights = pd.DataFrame(
        [
            {"Signal": key.replace("_score", "").replace("_", " ").title(), "Weight": value}
            for key, value in config["weights"].items()
        ]
    )
    fig = px.bar(weights, x="Weight", y="Signal", orientation="h", text=weights["Weight"].map(lambda value: f"{value:.0%}"), color="Signal")
    fig.update_layout(showlegend=False, height=360, xaxis_tickformat=".0%", xaxis_title="Weight", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        **Repeatability (30%)** ranks confirmed-fraud event counts. **Conviction (25%)** uses the Wilson lower
        confidence bound of each user's fraud-event rate. **Abnormality (20%)** compares observed fraud events with
        the number expected from that user's transaction-type mix. **Breadth (15%)** combines fraud methods, merchant
        countries and currencies. **Severity (10%)** uses the mean of the user's top three positive fraud-transaction
        amount percentiles within transaction type and currency.
        """
    )
    st.markdown("#### Deliberate exclusions")
    for note in config["notes"]:
        st.write(f"- {note}")
    st.warning(
        "The dataset has no timestamps, devices, IP addresses, counterparties, case outcomes, recoveries, chargebacks or realised loss. "
        "Use the ranking to allocate investigation—not to automate customer restrictions or attribute criminal identity."
    )


config_path = Path(os.getenv("FINCRIME_MODEL_CONFIG", ROOT / "risk_model.json"))
config = load_model_config(config_path)
frame, conversion, overview, ranking = source_selector(config)

st.title("Growth & Financial-Crime Audit")
st.caption("Reproducible conversion analysis and explainable Head-of-Risk priority ranking")

tab1, tab2, tab3, tab4 = st.tabs(["Growth audit", "Risk overview", "Top 5 targets", "Methodology & controls"])
with tab1:
    conversion_tab(conversion)
with tab2:
    overview_tab(frame, overview)
with tab3:
    targets_tab(ranking, config)
with tab4:
    methodology_tab(config)
