from __future__ import annotations

import pandas as pd
from datetime import datetime
from pathlib import Path

from core.config import load_settings
from ingestion.crossref import fetch_source_records
from ingestion.cleaning import build_clean_dataframe
from evaluation.testset import build_test_set
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from core.utils import write_json

def main() -> None:
    """TODO(student): xay dung baseline pipeline end-to-end.

    Pseudo-code:
    1. Load settings.
    2. Load hoac fetch raw records.
    3. Clean data.
    4. Save clean CSV/JSON.
    5. Build Chroma index.
    6. Tao hoac load evaluation set.
    7. Evaluate.
    8. Run quality checks va freshness report.
    9. Tao markdown report.
    10. Co the demo agent tren vai sample question.
    """

    """Xây dựng baseline pipeline end-to-end."""
    
    # 1. Load settings
    settings = load_settings()
    print(f"Loaded settings for provider: {settings.llm_provider}")
    
    # 2. Load hoac fetch raw records
    try:
        # Thử load từ file nếu đã tồn tại
        if settings.paths.raw_records_json.exists():
            print(f"Loading raw records from {settings.paths.raw_records_json}")
            import json
            from ingestion.crossref import PaperRecord
            with open(settings.paths.raw_records_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = [PaperRecord(**item) for item in data]
        else:
            print("Fetching raw records from Crossref API...")
            records = fetch_source_records(settings)
    except Exception as e:
        print(f"Error loading/fetching raw records: {e}")
        raise
    
    print(f"Fetched {len(records)} raw records")
    
    # 3. Clean data
    print("Cleaning data...")
    run_date = datetime.now()
    df = build_clean_dataframe(records, run_date)
    print(f"Cleaned to {len(df)} records")
    
    # 4. Save clean CSV/JSON
    print("Saving clean data...")
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    settings.paths.clean_json.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.paths.clean_csv, index=False)
    df.to_json(settings.paths.clean_json, orient="records", date_format="iso", indent=2)
    print(f"Saved clean data to {settings.paths.clean_csv} and {settings.paths.clean_json}")
    
    # 5. Build Chroma index
    print("Building Chroma index...")
    index = LocalEmbeddingIndex.build(
        df=df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"Built index with collection: {index.collection_name}")
    
    # 6. Tao hoac load evaluation set
    print("Building test set...")
    if settings.paths.eval_testset.exists():
        print(f"Loading existing test set from {settings.paths.eval_testset}")
        import json
        with open(settings.paths.eval_testset, "r", encoding="utf-8") as f:
            test_set = json.load(f)
    else:
        print("Creating new test set...")
        test_set = build_test_set(df, settings.paths.eval_testset)
    print(f"Test set has {len(test_set)} samples")
    
    # 7. Evaluate
    print("Evaluating pipeline...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    print(f"Evaluation completed. Retrieval hit rate: {bundle.summary['retrieval_hit_rate']:.3f}")
    
    # 8. Run quality checks va freshness report
    print("Running data quality checks...")
    quality_report = run_data_quality_checks(df, settings, "baseline")
    quality_report_path = settings.paths.quality_dir / "baseline_quality.json"
    settings.paths.quality_dir.mkdir(parents=True, exist_ok=True)
    write_json(quality_report_path, quality_report)
    print(f"Quality report saved to {quality_report_path}")
    
    print("Building freshness report...")
    freshness_report = build_freshness_report(df, settings, settings.paths.freshness_report)
    print(f"Freshness report: {freshness_report}")
    
    # 9. Tao markdown report
    print("Generating markdown report...")
    report_path = settings.paths.baseline_report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Baseline Pipeline Report\n\n")
        f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
        f.write(f"**LLM Provider**: {settings.llm_provider}\n")
        f.write(f"**Model**: {settings.model_name}\n\n")
        f.write("## Metrics\n\n")
        for key, value in bundle.summary.items():
            if key != "ragas":
                f.write(f"- {key}: {value:.4f}\n")
        f.write("\n")
        if isinstance(bundle.summary.get("ragas"), dict) and not bundle.summary["ragas"].get("skipped"):
            f.write("## Ragas Metrics\n\n")
            for key, value in bundle.summary["ragas"].items():
                if isinstance(value, (int, float)):
                    f.write(f"- {key}: {value:.4f}\n")
                else:
                    f.write(f"- {key}: {value}\n")
        f.write("\n")
        f.write("## Data Quality\n\n")
        for check, result in quality_report.items():
            f.write(f"- {check}: {result}\n")
        f.write("\n")
        f.write("## Freshness\n\n")
        for key, value in freshness_report.items():
            f.write(f"- {key}: {value}\n")
    
    print(f"Markdown report saved to {report_path}")
    print("Baseline pipeline completed successfully!")
