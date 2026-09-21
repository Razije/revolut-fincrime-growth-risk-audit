#!/usr/bin/env python3
"""Generate deterministic chart assets for the Head-of-Risk PDF."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
ASSETS = ROOT / "reports" / "head-of-risk" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INK = "#17324d"
MUTED = "#65788a"
GREEN = "#0b7355"
RED = "#a31d37"
BLUE = "#2f65a7"
AMBER = "#cf8b49"
GRID = "#dfe6ed"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelcolor": MUTED,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "axes.edgecolor": GRID,
    }
)


def short_id(value: str) -> str:
    return f"{value[:8]}…{value[-4:]}"


def priority_chart(top5: pd.DataFrame) -> None:
    data = top5.sort_values("priority_rank", ascending=False).copy()
    labels = [f"#{int(rank)}  {short_id(uid)}" for rank, uid in zip(data["priority_rank"], data["user_id"])]
    colors = [GREEN if rank == 1 else BLUE for rank in data["priority_rank"]]

    fig, ax = plt.subplots(figsize=(11.2, 5.2), dpi=180)
    bars = ax.barh(labels, data["priority_score"], color=colors, height=0.62)
    ax.set_xlim(0, 105)
    ax.set_xlabel("Composite priority score (0–100)")
    ax.set_title("Top 5 investigative priorities", loc="left", pad=14)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    for bar, score, events in zip(bars, data["priority_score"], data["fraud_events"]):
        ax.text(score + 0.8, bar.get_y() + bar.get_height() / 2, f"{score:.1f}", va="center", fontweight="bold", color=INK)
        ax.text(2.0, bar.get_y() + bar.get_height() / 2, f"{int(events):,} confirmed events", va="center", color="white", fontsize=9, fontweight="bold")

    fig.text(0.01, 0.01, "Scores are behavioural-risk priorities, not legal findings. Amount severity contributes 10%.", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(ASSETS / "top5_priority_scores.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def contrast_chart(top5: pd.DataFrame, challengers: pd.DataFrame) -> None:
    selected = top5.loc[top5["priority_rank"] == 5].iloc[0]
    challenger = challengers.sort_values("severity_score", ascending=False).iloc[0]
    components = [
        ("Repeatability", "repeatability_score"),
        ("Conviction", "conviction_score"),
        ("Abnormality", "abnormality_score"),
        ("Attack breadth", "breadth_score"),
        ("Amount severity", "severity_score"),
    ]
    selected_values = np.array([float(selected[column]) for _, column in components])
    challenger_values = np.array([float(challenger[column]) for _, column in components])
    y = np.arange(len(components))

    fig, ax = plt.subplots(figsize=(11.2, 5.2), dpi=180)
    height = 0.32
    ax.barh(y + height / 2, selected_values, height, color=GREEN, label=f"Selected #5 · {short_id(selected['user_id'])}")
    ax.barh(y - height / 2, challenger_values, height, color=AMBER, label=f"Severity challenger · {short_id(challenger['user_id'])}")
    ax.set_yticks(y, [label for label, _ in components])
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Component score (0–100)")
    ax.set_title("Selected #5 dominates four of five decision signals", loc="left", pad=34)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    for values, offset, color in [(selected_values, height / 2, GREEN), (challenger_values, -height / 2, AMBER)]:
        for index, value in enumerate(values):
            ax.text(min(value + 1.0, 102), index + offset, f"{value:.1f}", va="center", fontsize=8.5, fontweight="bold", color=color)

    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0.0, 1.01, 1.0, 0.1),
        mode="expand",
        ncol=2,
        frameon=False,
        fontsize=9,
        borderaxespad=0,
    )
    fig.text(
        0.01,
        0.01,
        f"Selected #5: {int(selected['fraud_events']):,} confirmed events across {int(selected['fraud_types'])} methods and {int(selected['fraud_merchant_countries'])} merchant countries. "
        f"Challenger: {int(challenger['fraud_events']):,} events across {int(challenger['fraud_types'])} methods and {int(challenger['fraud_merchant_countries'])} merchant country.",
        color=MUTED,
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(ASSETS / "selected_vs_severity_challenger.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    top5 = pd.read_csv(OUTPUTS / "top_5_priority_targets.csv")
    challengers = pd.read_csv(OUTPUTS / "high_severity_not_selected.csv")
    priority_chart(top5)
    contrast_chart(top5, challengers)
    print(ASSETS / "top5_priority_scores.png")
    print(ASSETS / "selected_vs_severity_challenger.png")


if __name__ == "__main__":
    main()
