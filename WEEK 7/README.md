# Delta Lake MERGE Implementation

## Objective
Perform incremental data processing using Delta Lake using Apache Spark.

## Steps Performed

1. Loaded the Sample Superstore dataset.
2. Performed data cleaning:
   - Checked for null values.
   - Removed duplicate records.
3. Renamed columns for Delta compatibility.
4. Stored cleaned data as a Delta table.
5. Created an incremental dataset.
6. Performed Delta Lake MERGE operation.
7. Updated existing records.
8. Inserted new records.
9. Validated the results.
10. Displayed the final dataset.

## Output

- Delta Table Created
- MERGE Operation Successful
- Existing Record Updated
- Two New Records Inserted
- Final Row Count: 9996
- No Duplicate Row_ID values