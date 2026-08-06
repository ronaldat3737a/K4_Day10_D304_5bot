# Baseline Pipeline Report

**Timestamp**: 2026-08-06T15:22:02.990981

**LLM Provider**: custom
**Model**: openai/gpt-oss-120b

## Metrics

- samples: 30.0000
- retrieval_hit_rate: 1.0000
- mean_token_f1: 0.7234
- judge_accuracy: 1.0000
- mean_judge_score: 4.7667

## Ragas Metrics

- error: Ragas evaluation failed: 0

## Data Quality

- row_count: 24
- paper_id_not_null: True
- paper_id_unique: True
- title_not_null: True
- summary_min_length_10: True
- age_days_non_negative: True
- age_days_reasonable: True

## Freshness

- latest_published: 2026-08-01T00:00:00
- oldest_published: 2026-02-13T00:00:00
- stale_rows: 0
- total_rows: 24
- is_fresh: True
