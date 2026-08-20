# TriSLA Public Dataset

This directory contains the versioned TriSLA dataset published as a
reproducibility artifact. The Parquet and CSV files provide the same logical
records in formats suited to programmatic processing and general inspection.

## Artifacts

| File | Format and role | Rows | Columns | Schema version | SHA-256 |
| --- | --- | ---: | ---: | --- | --- |
| `trisla_master_dataset_v2.parquet` | Apache Parquet; primary repository representation | 533 | 155 | `3.2.0-sa22-append` | `ab91d78557cab21a80bb460d000754827c6a242d74ea49ec8190d185e6f67631` |
| `trisla_master_dataset_v2.csv` | UTF-8 CSV with comma delimiter; accessible export | 533 | 155 | — | `e97ad9f9a63c24cbcf6516054da3b2369e8d23624abfc33348175f05c5a57b71` |

## Dataset consistency

The CSV and Parquet artifacts contain the same logical dataset. Their row
count, column count, column names, column order, null distribution, and logical
values were cross-validated before publication.

The Parquet artifact is the primary repository representation. The CSV
artifact is provided as a human-accessible and tool-independent export.

## Technical coverage

The dataset consolidates TriSLA observations associated with:

- multidomain admission;
- semantic processing;
- machine-learning inference and explainability;
- runtime assurance;
- end-to-end lifecycle measurements.

The dataset includes measurements associated with RAN, transport, core,
semantic processing, machine-learning inference and explainability, admission
decisions, runtime assurance, and end-to-end processing.

The schema also preserves blockchain-related compatibility fields from earlier
implementation campaigns. Their presence does not make blockchain part of the
current core architecture.

## Integrity

The SHA-256 hashes listed above can be used to verify the repository artifacts.

## Reproducibility

The dataset supports inspection and reproduction of workflows that consume
the published TriSLA records. Dataset files are versioned with the repository;
changes to documentation do not alter their contents.
