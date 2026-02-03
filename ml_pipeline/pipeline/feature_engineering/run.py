"""CLI: run feature engineering (API or CSV) and write features to disk."""
import argparse
import sys
from pathlib import Path

# Allow running as python -m pipeline.feature_engineering.run
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.config import Settings, get_features_dir, get_data_dir
from pipeline.feature_engineering.fetcher import fetch_transactions_from_api, load_transactions_from_csv
from pipeline.feature_engineering.features import build_feature_matrix


def main():
    p = argparse.ArgumentParser(description="Build feature matrix from ERP transactions")
    p.add_argument("--source", choices=["api", "csv"], default="api", help="Data source")
    p.add_argument("--csv-path", type=str, help="Path to CSV when source=csv")
    p.add_argument("--output", type=str, help="Output path (default: features/transactions_featured.parquet)")
    p.add_argument("--max-rows", type=int, default=None, help="Cap rows (dev)")
    p.add_argument("--api-url", type=str, default=None, help="Override ERP API base URL")
    p.add_argument("--token", type=str, default=None, help="JWT for API")
    args = p.parse_args()

    settings = Settings()
    if args.source == "api":
        df = fetch_transactions_from_api(
            base_url=args.api_url or settings.erp_api_base_url,
            token=args.token or settings.erp_api_token,
            max_rows=args.max_rows,
        )
    else:
        if not args.csv_path:
            print("--csv-path required when source=csv")
            sys.exit(1)
        df = load_transactions_from_csv(args.csv_path)

    if df.empty:
        print("No transactions loaded.")
        sys.exit(0)

    feat = build_feature_matrix(df, drop_na_rows=True)
    if feat.empty:
        print("No rows after feature build.")
        sys.exit(0)

    out_path = args.output
    if not out_path:
        base = Path.cwd()
        get_features_dir(base).mkdir(parents=True, exist_ok=True)
        out_path = get_features_dir(base) / "transactions_featured.parquet"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    feat.to_parquet(out_path, index=False)
    print(f"Wrote {len(feat)} rows to {out_path}")


if __name__ == "__main__":
    main()
