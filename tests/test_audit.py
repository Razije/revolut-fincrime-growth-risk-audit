from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from fincrime_audit.io import DataValidationError, load_transactions
from fincrime_audit.metrics import conversion_metrics
from fincrime_audit.scoring import build_priority_ranking, load_model_config, wilson_lower_bound


COLUMNS = [
    "USER_ID", "TYPE", "AMOUNT", "CURRENCY", "MERCHANT_COUNTRY",
    "KYC", "BIRTH_YEAR", "COUNTRY", "IS_FRAUD"
]


def sample_frame() -> pd.DataFrame:
    rows = [
        ["a", "CARD_PAYMENT", 100, "GBP", "GBR", "PASSED", 1990, "GB", True],
        ["a", "CARD_PAYMENT", 90, "GBP", "USA", "PASSED", 1990, "GB", True],
        ["a", "ATM", 80, "GBP", "GBR", "PASSED", 1990, "GB", True],
        ["b", "CARD_PAYMENT", 100000, "JPY", "JPN", "PASSED", 1980, "JP", True],
        ["b", "CARD_PAYMENT", 1, "JPY", "JPN", "PASSED", 1980, "JP", False],
        ["c", "CARD_PAYMENT", 20, "GBP", "GBR", "PASSED", 1975, "GB", False],
        ["c", "CARD_PAYMENT", 25, "GBP", "GBR", "PASSED", 1975, "GB", False],
        ["d", "TOPUP", 50, "EUR", "FRA", "PENDING", 1985, "FR", False],
    ]
    frame = pd.DataFrame(rows, columns=COLUMNS)
    csv = frame.to_csv(index=False).encode("utf-8")
    return load_transactions(BytesIO(csv))


def test_zip_loading_roundtrip(tmp_path):
    csv_path = tmp_path / "data.csv"
    pd.DataFrame([["x", "CARD_PAYMENT", 10, "GBP", "GBR", "PASSED", 1990, "GB", False]], columns=COLUMNS).to_csv(csv_path, index=False)
    zip_path = tmp_path / "data.zip"
    with ZipFile(zip_path, "w") as archive:
        archive.write(csv_path, arcname="fin_crime_data.csv")
    result = load_transactions(zip_path)
    assert len(result) == 1
    assert result.loc[0, "IS_FRAUD_BOOL"] == False


def test_missing_schema_is_rejected():
    invalid = BytesIO(b"USER_ID,TYPE\na,CARD_PAYMENT\n")
    try:
        load_transactions(invalid)
    except DataValidationError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Invalid schema should have been rejected")


def test_conversion_uses_same_kyc_passed_denominator():
    metrics = conversion_metrics(sample_frame())
    assert metrics["kyc_passed_denominator"] == 3
    assert metrics["marketing"]["numerator"] == 3
    assert metrics["matured_quality"]["numerator"] == 1
    assert metrics["sustainable_proxy"]["numerator"] == 1


def test_wilson_lower_bound_rewards_more_evidence():
    bounds = wilson_lower_bound(pd.Series([1, 100]), pd.Series([1, 100]))
    assert bounds.iloc[1] > bounds.iloc[0]


def test_ranking_excludes_nonfraud_users_and_limits_amount_dominance():
    ranking = build_priority_ranking(sample_frame(), load_model_config())
    assert set(ranking["user_id"]) == {"a", "b"}
    assert ranking.iloc[0]["user_id"] == "a"
    assert ranking.iloc[0]["fraud_events"] == 3
    assert ranking.iloc[1]["user_id"] == "b"
    assert ranking.iloc[1]["severity_score"] >= ranking.iloc[0]["severity_score"]
    assert "BIRTH_YEAR" not in ranking.columns
    assert "COUNTRY" not in ranking.columns


def test_model_weights_sum_to_one():
    config = load_model_config()
    assert abs(sum(config["weights"].values()) - 1.0) < 1e-12
