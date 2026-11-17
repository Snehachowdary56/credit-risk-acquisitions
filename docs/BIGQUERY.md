# Running the strategy analysis in Google BigQuery (cloud-based analytics)

The scored applications (`output/scored_applications.csv`, 1,000 rows: purpose, term, amount, age, outcome, score, PD) are loaded into **Google BigQuery**, and the adjudication strategy is reproduced with SQL in the cloud.

## Steps (BigQuery Sandbox: free, no credit card)

1. Open **console.cloud.google.com/bigquery** and sign in with a Google account. Accept the terms and create a project when asked (for example `credit-risk-analytics`).
2. In the **Explorer** panel, click the three dots next to the project → **Create dataset** → Dataset ID `credit` → **Create dataset**.
3. Click the three dots next to `credit` → **Create table**:
   - Create table from: **Upload** → choose `scored_applications.csv`
   - Table: `scored_applications`
   - Schema: tick **Auto detect**
   - Click **Create table**
4. Click **+** (new query tab), paste a query from `sql/bigquery/`, and click **Run**:
   - `01_cutoff_strategy.sql`: approval rate, bad rate, expected loss and profit for every cutoff
   - `02_operations_bands.sql`: auto-approve / refer / auto-decline volumes and bad rates
   - `03_segment_outcomes.sql`: application outcomes by loan purpose
   - `04_marketing_targeting.sql`: profit per application by segment for campaign targeting
5. Compare with the Python results in `output/summary.md`: they should match exactly (the SQL was checked against the Python output).

## Expected results (to check your run)

| Query | Check |
|---|---|
| 01 | cutoff 540: approval rate 0.325, bad rate 0.077, profit 28,303 |
| 02 | auto-approve 325, refer 169, auto-decline 506 applications |
| 03 | domestic appliances: 280 applications, approval rate 0.486 |
| 04 | top segment: car (used), 25+ months, profit per application 319.9 |
