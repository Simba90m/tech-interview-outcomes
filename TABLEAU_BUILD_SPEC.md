# Tech Interview Outcomes, Tableau Desktop build spec

This is the third dashboard in the portfolio series (after Workforce/HR Analytics and Logistics/Supply Chain). It uses a real 10,174-row interview dataset. Data source: `tableau_data/fct_interviews.csv` (one row per interview) and `tableau_data/dim_role.csv` (one row per role, pre-aggregated).

Before opening Tableau, copy the `tableau_data` folder to your machine (it will be committed to the GitHub repo, so a `git pull` on the repo folder is enough once that step is done).

## 1. Connect and set up data

1. Open Tableau Desktop, "Connect > Text File", pick `fct_interviews.csv`. Drag `dim_role.csv` in as a second connection (no join needed, it feeds a separate worksheet).
2. On `fct_interviews`, right-click `Interview Id` and set it to Dimension (it will default to Measure since it's numeric, but it is an ID, not something to sum).
3. Confirm `Is Requirement Leak` imports as Boolean. If it comes in as string ("True"/"False"), right-click it and use "Convert to Boolean", or create a calculated field `[Is Requirement Leak] = "True"`.
4. Rename fields for cleaner labels (right-click each, "Rename"):
   - `Role Display` to `Role`
   - `Role Family` stays as is
   - `Reason Category` to `Reason for Decision`

## 2. Calculated fields (create in fct_interviews)

**`Is Selected`**
```
IF [Decision] = "select" THEN 1 ELSE 0 END
```

**`Selection Rate`**
```
SUM([Is Selected]) / COUNT([Interview Id])
```
Format as Percentage, 1 decimal.

**`Exclude Anomaly Rows`** (Boolean parameter-backed filter, see Section 3)
```
IF [P: Exclude Data Quality Rows] THEN NOT [Is Requirement Leak] ELSE TRUE END
```

**`Anomaly Flag Label`** (for the callout sheet)
```
IF [Is Requirement Leak] THEN "Data quality anomaly (job requirement text leaked into reason field)" ELSE "Genuine decision reason" END
```

**`Word Count Ratio`**
```
[Transcript Word Count] / [Resume Word Count]
```
Useful as an optional scatter/detail measure if you want a fourth analytical view; not required for the core layout below.

## 3. Parameters

**`P: Exclude Data Quality Rows`**, Boolean, default value `True`. Add to a worksheet's Filters shelf via the calculated field above, and place the parameter control on the dashboard so viewers can toggle it, same idea as the checkbox in the Streamlit companion app.

## 4. Worksheets

### Sheet 1, "KPI Tiles"
Four single-value text tiles (or four separate worksheets combined in a horizontal container):
- **Interviews**: `COUNT([Interview Id])`, filtered by `Exclude Anomaly Rows`
- **Selected**: `SUM([Is Selected])`, filtered by `Exclude Anomaly Rows`
- **Selection Rate**: `[Selection Rate]`, filtered by `Exclude Anomaly Rows`
- **Data Quality Anomaly Rows**: `COUNT([Interview Id])` filtered to `[Is Requirement Leak] = TRUE`, unfiltered by the exclude toggle (this tile always shows the true anomaly count, it is the honesty callout)

Build each as its own worksheet: drag the measure to Text on the Marks card, format the font large (28-36pt), remove all axes/gridlines, add a small caption below in 10pt grey text explaining what it is. Use "Text Table" as the mark type, or simply a blank worksheet with just a Text mark.

### Sheet 2, "Selection Rate by Role"
- Columns: `Selection Rate`
- Rows: `Role` (sorted descending by Selection Rate: right-click the Role axis, Sort, Field: Selection Rate, Descending)
- Color: `Role Family`
- Mark type: Bar
- Filter: `Exclude Anomaly Rows` = True
- Label: show `Selection Rate` on the bar ends (Label shelf, format as %)
- Tooltip: include `Role`, `Role Family`, `Selection Rate`, and `COUNT([Interview Id])` as "Interviews"

This mirrors the horizontal bar chart already built in the Streamlit companion app, so the two feel like one product.

### Sheet 3, "Why Candidates Are Selected or Rejected"
- Columns: `CNT([Interview Id])`
- Rows: `Reason for Decision`
- Color: `Decision` (2 colors: teal for select, magenta/red for reject, matching the Streamlit app's `#0F9B8E` / `#D6006C`)
- Mark type: Bar, side-by-side (drag `Decision` to Columns as well, next to the reason field, or use the "Side-by-side bar" option under Marks)
- Filter: `Exclude Anomaly Rows` = True (this sheet should exclude the "Data Quality: Requirement Text Leaked" category entirely once the toggle is on, since it is not a real reason)
- Sort: descending by total count

### Sheet 4, "Resume & Transcript Length vs Outcome"
- Rows: `Decision`
- Columns: two measures, `AVG([Resume Word Count])` and `AVG([Transcript Word Count])`, using a dual-axis or simply two side-by-side bar charts (Measure Names/Measure Values approach: drag both measures into Columns, then right-click and "Dual Axis" if you want them overlaid, or leave as separate small-multiple columns for clarity)
- This is intentionally a small, quiet chart. It shows there is almost no length difference between selected and rejected candidates (roughly 336-338 avg resume words either way), which is itself an honest, slightly counter-intuitive finding worth calling out in a text annotation on the dashboard.

### Sheet 5, "Role Family Overview" (uses `dim_role.csv`)
- Columns: `SUM([Total Interviews])`
- Rows: `Role Family`
- Color: `Role Family`
- Mark type: Bar or Treemap (a treemap sized by `Total Interviews` and colored by `Selection Rate Pct` reads well as a portfolio-piece visual, since it gives a second encoding dimension for free)
- This gives the "zoomed out" view before a viewer drills into individual roles in Sheet 2.

### Sheet 6, "Data Quality Note" (text sheet)
A plain text worksheet, no chart. Content (paraphrase in your own words, keep it factual and specific):

> This dataset contains two real data quality issues found during modeling, both disclosed rather than hidden:
> 1. About 9.5% of rows (963 of 10,174) have the "reason for decision" field populated with leaked job-requirement text instead of a genuine decision reason. These rows are excluded by default (toggle above) and are counted separately in the KPI tile.
> 2. Three pairs of distinct candidates shared the same source ID in the raw data. A surrogate `interview_id` was generated to guarantee uniqueness; the original ID is preserved as `source_id` for traceability.

## 5. Dashboard actions

1. **Filter action**: from Sheet 5 (Role Family Overview) to Sheet 2 (Selection Rate by Role), on select, target the `Role Family` field. Clicking a bar/treemap segment in the overview narrows the role-level bar chart below it.
2. **Highlight action**: from Sheet 2 (Selection Rate by Role) to Sheet 3 (Why Candidates Are Selected or Rejected), on hover, highlighting by `Role Family`. Optional, but it gives the dashboard a connected, alive feel appropriate for a "masterpiece" showcase piece.
3. Add the `P: Exclude Data Quality Rows` parameter control to the dashboard toolbar (top-right is conventional) so it visibly governs every sheet that reads it.

## 6. Dashboard layout

Recommended structure, top to bottom:
1. Title: "Tech Interview Outcomes" with a one-line subtitle ("10,174 real interviews across 38 tech and non-tech roles")
2. KPI tiles row (Sheet 1, all four tiles side by side)
3. Parameter control (`P: Exclude Data Quality Rows`) aligned right of the KPI row
4. Two-column row: Role Family Overview (Sheet 5) on the left (narrower, ~35%), Selection Rate by Role (Sheet 2) on the right (wider, ~65%, this is the dashboard's centerpiece and needs vertical room for all 38 roles)
5. Two-column row: Why Candidates Are Selected or Rejected (Sheet 3) and Resume & Transcript Length vs Outcome (Sheet 4)
6. Data Quality Note (Sheet 6) as a footer strip, full width, small text

Use a consistent font (match the portfolio's existing typography if you have a preference), and reuse the teal/magenta color pair from the Streamlit app throughout so the two pieces read as one project when a recruiter looks at both.

## 7. Publish

Publish to Tableau Public under the same profile as your other two dashboards, name it "Tech Interview Outcomes". Once published, send me the link and I will fold it into the GitHub README, the portfolio site, and the GitHub profile README, matching the pattern used for the other two projects.
