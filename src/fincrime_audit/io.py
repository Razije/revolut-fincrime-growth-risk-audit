"""Input loading and validation for the transaction audit."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from zipfile import BadZipFile, ZipFile

import pandas as pd

REQUIRED_COLUMNS = {
    "USER_ID",
    "TYPE",
    "AMOUNT",
    "CURRENCY",
    "MERCHANT_COUNTRY",
    "KYC",
    "BIRTH_YEAR",
    "COUNTRY",
    "IS_FRAUD",
}


class DataValidationError(ValueError):
    """Raised when an input cannot support the audit calculation."""


def _read_csv(source: str | Path | BinaryIO) -> pd.DataFrame:
    return pd.read_csv(source, low_memory=False)


def _read_zip(source: str | Path | BinaryIO) -> pd.DataFrame:
    try:
        with ZipFile(source) as archive:
            candidates = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX/")
            ]
            if len(candidates) != 1:
                raise DataValidationError(
                    f"Expected exactly one CSV in the ZIP; found {len(candidates)}."
                )
            with archive.open(candidates[0]) as handle:
                return _read_csv(handle)
    except BadZipFile as exc:
        raise DataValidationError("The supplied ZIP file is invalid.") from exc


def _is_zip(source: str | Path | BinaryIO) -> bool:
    if isinstance(source, (str, Path)):
        return str(source).lower().endswith(".zip")
    name = getattr(source, "name", "")
    if str(name).lower().endswith(".zip"):
        return True
    position = source.tell()
    signature = source.read(4)
    source.seek(position)
    return signature == b"PK\x03\x04"


def load_transactions(source: str | Path | BinaryIO | bytes) -> pd.DataFrame:
    """Load and standardise the audit dataset from CSV or ZIP.

    The returned frame preserves the original fields and adds numeric/boolean
    canonical forms used by the calculations.
    """
    if isinstance(source, bytes):
        source = BytesIO(source)

    frame = _read_zip(source) if _is_zip(source) else _read_csv(source)
    frame.columns = [str(column).strip().upper() for column in frame.columns]

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise DataValidationError(f"Missing required columns: {sorted(missing)}")
    if frame.empty:
        raise DataValidationError("The dataset is empty.")

    frame = frame.copy()
    for column in ["USER_ID", "TYPE", "CURRENCY", "MERCHANT_COUNTRY", "KYC", "COUNTRY"]:
        frame[column] = frame[column].fillna("").astype(str).str.strip()
    frame["TYPE"] = frame["TYPE"].str.upper()
    frame["CURRENCY"] = frame["CURRENCY"].str.upper()
    frame["MERCHANT_COUNTRY"] = frame["MERCHANT_COUNTRY"].str.upper()
    frame["KYC"] = frame["KYC"].str.upper()
    frame["COUNTRY"] = frame["COUNTRY"].str.upper()
    frame["AMOUNT_NUMERIC"] = pd.to_numeric(frame["AMOUNT"], errors="coerce")
    frame["IS_FRAUD_BOOL"] = (
        frame["IS_FRAUD"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
    )

    if frame["USER_ID"].eq("").any():
        raise DataValidationError("USER_ID contains blank values.")
    if frame["IS_FRAUD_BOOL"].isna().any():
        bad = sorted(frame.loc[frame["IS_FRAUD_BOOL"].isna(), "IS_FRAUD"].astype(str).unique())
        raise DataValidationError(f"IS_FRAUD contains unsupported values: {bad[:5]}")

    frame["IS_FRAUD_BOOL"] = frame["IS_FRAUD_BOOL"].astype(bool)
    return frame
