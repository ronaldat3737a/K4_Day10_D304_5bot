# Corruption Comparison Report

**Timestamp**: 2026-08-06T15:51:36.542097

## Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
|--------|----------|-----------|----------|
| judge_accuracy | 1.0000 | 0.9000 | 1.0000 |
| mean_judge_score | 4.7667 | 4.4000 | 4.8000 |
| mean_token_f1 | 0.7234 | 0.6761 | 0.7214 |
| retrieval_hit_rate | 1.0000 | 1.0000 | 1.0000 |
| samples | 30 | 30 | 30 |

### RAGAS Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
|--------|----------|-----------|----------|

## Data Quality Comparison

| Check | Baseline | Corrupted | Repaired |
|-------|----------|-----------|----------|
| age_days_non_negative | N/A | True | True |
| age_days_reasonable | N/A | True | True |
| paper_id_not_null | N/A | True | True |
| paper_id_unique | N/A | False | True |
| row_count | N/A | 23 | 24 |
| summary_min_length_10 | N/A | False | True |
| title_not_null | N/A | True | True |

## Freshness Comparison

| Metric | Baseline | Corrupted | Repaired |
|--------|----------|-----------|----------|
| is_fresh | N/A | True | True |
| latest_published | N/A | 2026-08-01T00:00:00 | 2026-08-01T00:00:00 |
| oldest_published | N/A | 2026-02-26T00:00:00 | 2026-02-13T00:00:00 |
| stale_rows | N/A | 0 | 0 |
| total_rows | N/A | 23 | 24 |

