import argparse
import math
import os
from pathlib import Path

import mlflow
from mlflow import MlflowClient

MODEL_NAME = "food11"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--dataset",
        choices=["mini", "processed"],
        default="mini",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    candidate = client.get_model_version(
        MODEL_NAME,
        args.version,
    )

    champion = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    candidate_run = client.get_run(candidate.run_id)
    champion_run = client.get_run(champion.run_id)

    candidate_acc = candidate_run.data.metrics["test_accuracy"]
    champion_acc = champion_run.data.metrics["test_accuracy"]

    project_root = Path(__file__).resolve().parents[2]

    if args.dataset == "mini":
        evaluation_dir = (
            project_root
            / "data"
            / "food11_processed_mini"
            / "evaluation"
        )
    else:
        evaluation_dir = (
            project_root
            / "data"
            / "food11_processed"
            / "evaluation"
        )

    n = sum(
        1
        for path in evaluation_dir.rglob("*")
        if path.is_file()
    )

    se = math.sqrt(
        champion_acc * (1 - champion_acc) / n
    )
    threshold = champion_acc + 2 * se

    print(f"Candidate version: {candidate.version}")
    print(f"Candidate accuracy: {candidate_acc:.4f}")
    print(f"Champion version: {champion.version}")
    print(f"Champion accuracy: {champion_acc:.4f}")
    print(f"Test samples: {n}")
    print(f"2 * SE: {2 * se:.4f}")
    print(f"Promotion threshold: {threshold:.4f}")

    if candidate_acc >= threshold:
        decision = "promoted_to_champion"

        client.set_registered_model_alias(
            MODEL_NAME,
            "champion",
            candidate.version,
        )

        print("Decision: PROMOTE to champion")
    else:
        decision = "assigned_challenger"

        client.set_registered_model_alias(
            MODEL_NAME,
            "challenger",
            candidate.version,
        )

        print("Decision: keep champion, candidate becomes challenger")

    client.set_model_version_tag(
        MODEL_NAME,
        candidate.version,
        "promotion_decision",
        decision,
    )

    client.set_model_version_tag(
        MODEL_NAME,
        candidate.version,
        "candidate_accuracy",
        str(candidate_acc),
    )

    client.set_model_version_tag(
        MODEL_NAME,
        candidate.version,
        "champion_accuracy",
        str(champion_acc),
    )

    client.set_model_version_tag(
        MODEL_NAME,
        candidate.version,
        "promotion_threshold",
        str(threshold),
    )


if __name__ == "__main__":
    main()
