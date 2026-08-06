from __future__ import annotations

import pandas as pd
from datetime import datetime
from pathlib import Path

from core.config import load_settings
from ingestion.crossref import fetch_source_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from evaluation.testset import build_test_set
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report, generate_corruption_report
from core.utils import write_json


def main() -> None:
    """Xây dựng corruption -> evaluate -> repair -> compare flow."""
    
    # 1. Load settings
    settings = load_settings()
    print(f"Loaded settings for provider: {settings.llm_provider}")
    
    # ==========================================
    # KHAI BÁO ĐƯỜNG DẪN LOCAL (Không cần config.py)
    # ==========================================
    data_dir = Path("data")
    
    # Corrupted Paths
    corruption_log_path = data_dir / "corruption_log.json"
    corrupted_csv_path = data_dir / "corrupted" / "papers_corrupted.csv"
    corrupted_json_path = data_dir / "corrupted" / "papers_corrupted.json"
    corrupted_embeddings_path = data_dir / "corrupted" / "corrupted_embeddings.json"
    corrupted_metrics_path = data_dir / "eval" / "corrupted_metrics.json"
    corrupted_answers_path = data_dir / "eval" / "corrupted_answers.json"
    corrupted_quality_path = data_dir / "quality" / "corrupted_quality.json"
    corrupted_freshness_path = data_dir / "quality" / "corrupted_freshness.json"
    
    # Repaired Paths
    repaired_csv_path = data_dir / "repaired" / "papers_repaired.csv"
    repaired_json_path = data_dir / "repaired" / "papers_repaired.json"
    repaired_embeddings_path = data_dir / "repaired" / "repaired_embeddings.json"
    repaired_metrics_path = data_dir / "eval" / "repaired_metrics.json"
    repaired_answers_path = data_dir / "eval" / "repaired_answers.json"
    repaired_quality_path = data_dir / "quality" / "repaired_quality.json"
    repaired_freshness_path = data_dir / "quality" / "repaired_freshness.json"
    
    # Report Path
    comparison_report_path = data_dir / "reports" / "corruption_comparison.md"
    # ==========================================

    # 2. Load baseline metrics and clean dataset (nếu đã tồn tại)
    print("Loading baseline data...")
    baseline_metrics = {}
    clean_df = None
    
    # Thử load baseline metrics nếu có
    if settings.paths.baseline_metrics.exists():
        try:
            import json
            with open(settings.paths.baseline_metrics, "r", encoding="utf-8") as f:
                baseline_metrics = json.load(f)
            print(f"Loaded baseline metrics from {settings.paths.baseline_metrics}")
        except Exception as e:
            print(f"Warning: Could not load baseline metrics: {e}")
    
    # Thử load clean dataset nếu có
    if settings.paths.clean_json.exists():
        try:
            clean_df = pd.read_json(settings.paths.clean_json, orient="records")
            print(f"Loaded clean dataset from {settings.paths.clean_json} with {len(clean_df)} records")
        except Exception as e:
            print(f"Warning: Could not load clean dataset: {e}")
    
    # Nếu không có clean dataset, cần chạy baseline trước
    if clean_df is None:
        print("Clean dataset not found. Please run baseline pipeline first (script/run_phase1.py)")
        return
    
    # 3. Tạo corrupted dataframe
    print("Corrupting clean data...")
    corrupted_df = corrupt_clean_dataframe(clean_df, corruption_log_path)
    print(f"Corrupted dataset has {len(corrupted_df)} records (original: {len(clean_df)})")
    
    # 4. Lưu corrupted artifacts
    print("Saving corrupted data...")
    corrupted_csv_path.parent.mkdir(parents=True, exist_ok=True)
    corrupted_json_path.parent.mkdir(parents=True, exist_ok=True)
    corrupted_df.to_csv(corrupted_csv_path, index=False)
    corrupted_df.to_json(corrupted_json_path, orient="records", date_format="iso", indent=2)
    print(f"Saved corrupted data to {corrupted_csv_path} and {corrupted_json_path}")
    
    # 5. Rebuild index và evaluate trên corrupted data
    print("Building Chroma index for corrupted data...")
    corrupted_index = LocalEmbeddingIndex.build(
        df=corrupted_df,
        settings=settings,
        embeddings_output_path=corrupted_embeddings_path,
    )
    print(f"Built corrupted index with collection: {corrupted_index.collection_name}")
    
    print("Evaluating corrupted pipeline...")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,  # Sử dụng cùng test set của phase 1
        metrics_output_path=corrupted_metrics_path,
        answers_output_path=corrupted_answers_path,
    )
    print(f"Corrupted evaluation completed. Retrieval hit rate: {corrupted_bundle.summary['retrieval_hit_rate']:.3f}")
    
    # 6. Chạy quality checks và freshness trên corrupted data
    print("Running data quality checks on corrupted data...")
    corrupted_quality_report = run_data_quality_checks(corrupted_df, settings, "corrupted")
    corrupted_quality_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(corrupted_quality_path, corrupted_quality_report)
    print(f"Corrupted quality report saved to {corrupted_quality_path}")
    
    print("Building freshness report for corrupted data...")
    corrupted_freshness_report = build_freshness_report(corrupted_df, settings, corrupted_freshness_path)
    print(f"Corrupted freshness report: {corrupted_freshness_report}")
    
    # 7. Repair lại từ raw records
    print("Repairing from raw records...")
    try:
        if settings.paths.raw_records_json.exists():
            print(f"Loading raw records from {settings.paths.raw_records_json}")
            import json
            from ingestion.crossref import PaperRecord
            with open(settings.paths.raw_records_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_records = [PaperRecord(**item) for item in data]
        else:
            print("Fetching raw records from Crossref API...")
            raw_records = fetch_source_records(settings)
    except Exception as e:
        print(f"Error loading/fetching raw records: {e}")
        raise
    
    print(f"Fetched {len(raw_records)} raw records for repair")
    
    run_date = datetime.now()
    repaired_df = build_clean_dataframe(raw_records, run_date)
    print(f"Repaired to {len(repaired_df)} records")
    
    print("Saving repaired data...")
    repaired_csv_path.parent.mkdir(parents=True, exist_ok=True)
    repaired_json_path.parent.mkdir(parents=True, exist_ok=True)
    repaired_df.to_csv(repaired_csv_path, index=False)
    repaired_df.to_json(repaired_json_path, orient="records", date_format="iso", indent=2)
    print(f"Saved repaired data to {repaired_csv_path} and {repaired_json_path}")
    
    # 8. Evaluate repaired dataset
    print("Building Chroma index for repaired data...")
    repaired_index = LocalEmbeddingIndex.build(
        df=repaired_df,
        settings=settings,
        embeddings_output_path=repaired_embeddings_path,
    )
    print(f"Built repaired index with collection: {repaired_index.collection_name}")
    
    print("Evaluating repaired pipeline...")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=repaired_metrics_path,
        answers_output_path=repaired_answers_path,
    )
    print(f"Repaired evaluation completed. Retrieval hit rate: {repaired_bundle.summary['retrieval_hit_rate']:.3f}")
    
    print("Running data quality checks on repaired data...")
    repaired_quality_report = run_data_quality_checks(repaired_df, settings, "repaired")
    repaired_quality_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(repaired_quality_path, repaired_quality_report)
    print(f"Repaired quality report saved to {repaired_quality_path}")
    
    print("Building freshness report for repaired data...")
    repaired_freshness_report = build_freshness_report(repaired_df, settings, repaired_freshness_path)
    print(f"Repaired freshness report: {repaired_freshness_report}")
    
    # 9. Tạo comparison report
    print("Generating comparison report...")
    comparison_report_path.parent.mkdir(parents=True, exist_ok=True)
    
    generate_corruption_report(
        report_path=comparison_report_path,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality_report,
        repaired_quality=repaired_quality_report,
        corrupted_freshness=corrupted_freshness_report,
        repaired_freshness=repaired_freshness_report,
    )
    print(f"Comparison report saved to {comparison_report_path}")
    
    print("Corruption flow completed successfully!")
    print(f"Summary:")
    
    baseline_hit_rate = baseline_metrics.get('retrieval_hit_rate', 'N/A')
    if isinstance(baseline_hit_rate, (int, float)):
        print(f"  Baseline hit rate: {baseline_hit_rate:.3f}")
    else:
        print(f"  Baseline hit rate: {baseline_hit_rate}")
        
    print(f"  Corrupted hit rate: {corrupted_bundle.summary['retrieval_hit_rate']:.3f}")
    print(f"  Repaired hit rate: {repaired_bundle.summary['retrieval_hit_rate']:.3f}")