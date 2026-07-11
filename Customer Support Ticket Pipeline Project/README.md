# Customer Support Ticket Resolution Pipeline

## Project Overview

This project implements a PySpark-based ETL pipeline to process customer support ticket data. The pipeline performs data validation, transformation, filtering, and aggregation using a Bronze → Silver → Gold architecture in Databricks.

The goal is to generate accurate performance reports for Team Leads and Support Agents while applying business rules defined in the project requirements.

## Technologies Used

- Databricks
- PySpark
- Delta Lake
- Python
- Spark SQL

## Project Architecture

```
Raw Data
    │
    ▼
Bronze Layer
    │
    ▼
Data Cleaning
    │
    ▼
Silver Layer
    │
    ▼
Business Rules
    │
    ▼
Gold Layer
    │
    ▼
Reporting
```
## Datasets

The notebook generates three datasets:

- Agent Profiles
- Day 1 Ticket Logs
- Day 2 Ticket Logs

These datasets simulate customer support ticket data.

## Business Rules Implemented

- Remove records with missing Ticket ID
- Remove records with missing Agent ID
- Remove records with missing Resolution Time
- Convert resolution time into minutes
- Round seconds ≥30 to the next minute
- Keep only **Resolved** tickets
- Keep only tickets with **Resolution Time > 15 minutes**
- Include only Team Leads **TL01–TL08**
- Remove Day 2 records for agents already successful on Day 1 (Carry-over Rule)

## Output Reports

### 1. Team Lead Performance Matrix

Shows the total number of valid resolved tickets handled under each Team Lead.

### 2. Per Agent Daily Performance

Shows the number of valid tickets resolved by each agent for each day.

## Project Workflow

1. Generate Bronze datasets
2. Validate data
3. Clean invalid records
4. Parse resolution time
5. Join with Agent Profiles
6. Apply business rules
7. Generate Gold reports
8. Export final CSV reports

