"""
SageMaker training entrypoint.
When running on SageMaker, data is in /opt/ml/input/data/train and model output in /opt/ml/model.
Run locally with same layout for compatibility.
"""
import argparse
import os
import sys
from pathlib import Path

# Default paths used by SageMaker
SM_INPUT_DATA = os.environ.get("SM_INPUT_DATA_DIR", "/opt/ml/input/data")
SM_MODEL_DIR = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
SM_CHANNEL_TRAIN = os.path.join(SM_INPUT_DATA, "train")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline.training.train import train


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-components", type=int, default=8)
    parser.add_argument("--n-clusters", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    # SageMaker places featured data at channel "train"; expect transactions_featured.parquet
    features_path = Path(SM_CHANNEL_TRAIN) / "transactions_featured.parquet"
    if not features_path.exists():
        # Fallback for local run
        features_path = Path("features") / "transactions_featured.parquet"
    if not features_path.exists():
        raise FileNotFoundError(
            f"Training data not found at {features_path}. "
            "Upload transactions_featured.parquet to the train channel."
        )

    train(
        features_path=features_path,
        model_dir=SM_MODEL_DIR,
        n_components=args.n_components,  # from --n-components
        n_clusters=args.n_clusters,      # from --n-clusters
        random_state=args.random_state,
    )
    print(f"Model artifacts written to {SM_MODEL_DIR}")


if __name__ == "__main__":
    main()
