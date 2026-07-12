# E-Commerce Order Analytics System

An end-to-end data engineering and analytics pipeline built natively with Python and SQL. The system injects structural data inconsistencies into mock transactions, cleans them using Pandas, migrates them to a relational SQLite database schema, and generates advanced business intelligence reports via a custom Command-Line Interface (CLI).

## System Architecture

1. **Data Generation (`generate_data.py`)**: Produces messy datasets across Customers, Products, Orders, and Items while intentionally injecting a target layout of missing values, string anomalies, and broken date strings.
2. **Data Cleaning (`clean_data.py`)**: Standardizes formats, handles null records safely, enforces string normalizations, ensures referential integrity, and generates a data quality tracking report.
3. **Database Migration (`load_to_db.py`)**: Establishes schema fields featuring Primary Keys, Check Constraints, and Foreign Key relations before ingesting the clean datasets.
4. **CLI Analytics Portal (`report_cli.py`)**: A pure Python-implemented report engine running advanced window functions, CTEs, self-joins, and dynamic time-period filters without any external visualization library requirements.

## How to Run the Project

### 1. Ingest Data Pipeline
```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/load_to_db.py  

# Basic Aggregations (Queries 1-6)
python scripts/report_cli.py --file aggregations.sql

# Advanced Window Functions (Queries 7-11)
python scripts/report_cli.py --file window_functions.sql

# Cohort & Retention Metrics (Queries 12-16)
python scripts/report_cli.py --file cohort_analysis.sql

#Generate Dynamic Period KPI Summaries
python scripts/report_cli.py --summary 2025-01-01 2026-12-31