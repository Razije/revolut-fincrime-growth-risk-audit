#!/usr/bin/env python3
"""Entry point for analysis and dashboard execution."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fincrime_audit import build_priority_ranking, conversion_metrics, load_model_config, load_transactions, risk_overview
from fincrime_audit.reporting import write_outputs


def analyse(data_path: Path, output_dir: Path, config_path: Path) -> int:
    frame = load_transactions(data_path)
    config = load_model_config(config_path)
    conversion = conversion_metrics(frame)
    overview = risk_overview(frame)
    ranking = build_priority_ranking(frame, config)
    paths = write_outputs(output_dir, conversion, overview, ranking, config)

    print("Analysis complete")
    print(f"Rows: {conversion['rows']:,}; users: {conversion['unique_users']:,}")
    print(
        f"Conversion: {conversion['marketing']['rate_pct']:.2f}% -> "
        f"{conversion['sustainable_proxy']['rate_pct']:.2f}% "
        f"(-{conversion['bridge']['total_pp']:.2f} pp)"
    )
    print("Top 5 priority targets:")
    for _, row in ranking.head(int(config["top_n"])).iterrows():
        print(
            f"  #{int(row['priority_rank'])} {row['user_id']} | "
            f"score={row['priority_score']:.1f} | fraud_events={int(row['fraud_events'])}"
        )
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


def dashboard(data_path: Path, config_path: Path, port: int) -> int:
    env = os.environ.copy()
    env["FINCRIME_DATA"] = str(data_path.resolve())
    env["FINCRIME_MODEL_CONFIG"] = str(config_path.resolve())
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app.py"),
        "--server.port",
        str(port),
        "--server.address",
        "0.0.0.0",
        "--browser.gatherUsageStats",
        "false",
    ]
    return subprocess.call(command, cwd=ROOT, env=env)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the growth and financial-crime audit.")
    p.add_argument("mode", choices=["analyse", "dashboard"], help="Generate outputs or launch the dashboard.")
    p.add_argument("--data", required=True, type=Path, help="Path to fin_crime_data.csv or a ZIP containing it.")
    p.add_argument("--config", type=Path, default=ROOT / "risk_model.json", help="Risk-model configuration JSON.")
    p.add_argument("--output", type=Path, default=ROOT / "outputs", help="Analysis output directory.")
    p.add_argument("--port", type=int, default=8501, help="Dashboard port.")
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "analyse":
        raise SystemExit(analyse(args.data, args.output, args.config))
    raise SystemExit(dashboard(args.data, args.config, args.port))
