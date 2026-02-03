"""CLI: run inference on featured data or raw transactions."""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.config import Settings, get_model_dir, get_features_dir
from pipeline.inference.predictor import load_predictor
from pipeline.feature_engineering.fetcher import fetch_transactions_from_api, load_transactions_from_csv


def main():
    p = argparse.ArgumentParser(description="Run anomaly detection inference")
    p.add_argument("--model-dir", type=str, default=None, help="Path to trained model")
    p.add_argument("--input", type=str, default=None, help="Input: parquet (feature matrix) or CSV (raw transactions)")
    p.add_argument("--output", type=str, default=None, help="Output parquet path")
    p.add_argument("--source", choices=["api", "file"], default="file", help="When input is raw: fetch from API or read file")
    p.add_argument("--api-url", type=str, default=None)
    p.add_argument("--token", type=str, default=None)
    args = p.parse_args()

    settings = Settings()
    model_dir = Path(args.model_dir or get_model_dir())
    if not model_dir.exists() or not (model_dir / "config.json").exists():
        print(f"Model not found: {model_dir}")
        sys.exit(1)

    predictor = load_predictor(model_dir)

    if args.input:
        path = Path(args.input)
        if path.suffix.lower() == ".csv":
            df = load_transactions_from_csv(path)
            scored = predictor.score_transactions(df)
        else:
            df = pd.read_parquet(path)
            scored = predictor.score_dataframe(df)
    elif args.source == "api":
        df = fetch_transactions_from_api(
            base_url=args.api_url or settings.erp_api_base_url,
            token=args.token or settings.erp_api_token,
        )
        scored = predictor.score_transactions(df)
    else:
        # Default: use featured parquet then score
        feat_path = get_features_dir() / "transactions_featured.parquet"
        if not feat_path.exists():
            print("No input. Use --input or --source api or run feature_engineering first.")
            sys.exit(1)
        df = pd.read_parquet(feat_path)
        scored = predictor.score_dataframe(df)

    out_path = args.output
    if not out_path:
        out_path = Path(settings.output_dir) / "scored.parquet"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_parquet(out_path, index=False)
    n_anom = scored["is_anomaly"].sum() if "is_anomaly" in scored.columns else 0
    print(f"Wrote {len(scored)} rows to {out_path}, anomalies: {n_anom}")


if __name__ == "__main__":
    main()
