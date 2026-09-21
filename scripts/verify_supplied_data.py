#!/usr/bin/env python3
"""Verify known outputs for the supplied challenge dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from fincrime_audit import build_priority_ranking, conversion_metrics, load_model_config, load_transactions

EXPECTED_TOP5 = [
    "dc283b17-bbe1-4ae9-a11c-0029d5ae71d9",
    "b8271606-4633-4d8f-8729-a2c8ebb8a49f",
    "25c2ecb3-5ec7-4fa6-8fc3-bbcf3a691217",
    "5c75c857-61f0-400e-ac7b-25451c57e8de",
    "4ee8690a-ebf7-435b-9fe2-103e8f83edc6",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    args = parser.parse_args()

    frame = load_transactions(args.data)
    metrics = conversion_metrics(frame)
    ranking = build_priority_ranking(frame, load_model_config())

    assert metrics["rows"] == 688651
    assert metrics["unique_users"] == 8021
    assert metrics["kyc_passed_denominator"] == 6989
    assert metrics["marketing"]["numerator"] == 5463
    assert metrics["sustainable_proxy"]["numerator"] == 5014
    assert ranking.head(5)["user_id"].tolist() == EXPECTED_TOP5
    print("Supplied-dataset verification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
