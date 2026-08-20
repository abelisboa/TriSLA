# TriSLA Experimental Dataset

This directory contains the consolidated experimental dataset used for the
evaluation of the TriSLA architecture.

## Dataset files

### Canonical dataset

`trisla_master_dataset_v2.parquet`

- Format: Apache Parquet
- Role: canonical scientific dataset
- Rows: 533
- Columns: 155
- Schema version: `3.2.0-sa22-append`
- SHA-256:
  `ab91d78557cab21a80bb460d000754827c6a242d74ea49ec8190d185e6f67631`

### CSV publication export

`trisla_master_dataset_v2.csv`

- Format: CSV
- Encoding: UTF-8
- Delimiter: comma
- Role: publication export of the canonical dataset
- Rows: 533
- Columns: 155
- SHA-256:
  `e97ad9f9a63c24cbcf6516054da3b2369e8d23624abfc33348175f05c5a57b71`

## Dataset consistency

The CSV and Parquet artifacts contain the same logical dataset. Their row
count, column count, column names, column order, null distribution, and logical
values were cross-validated before publication.

The Parquet artifact is the canonical representation. The CSV artifact is
provided as a human-accessible and tool-independent publication export.

## Experimental coverage

The dataset consolidates observations used in the experimental evaluation of
TriSLA, including data associated with:

- multidomain admission experiments;
- semantic robustness evaluation;
- machine-learning model benchmarking;
- runtime assurance;
- end-to-end lifecycle measurements.

The dataset includes measurements associated with RAN, transport, core,
semantic processing, machine-learning inference and explainability,
blockchain governance, admission decisions, runtime assurance, and end-to-end
processing.

## Integrity

The SHA-256 hashes listed above can be used to verify the integrity of the
published artifacts.

## Reproducibility

The dataset is published as a research artifact to support inspection and
reproducibility of the experimental evaluation of TriSLA.
