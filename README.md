# High Value Habits

**Question:** among retail households that are already shopping regularly, is buying across a *wider range of product categories* in year one associated with *stronger engagement* in year two — or is that just because the same households already shop more often?

**Live interactive version:** https://claude.ai/artifact/PUFqFStGmWNbwzS9HF3LLE
Drag the "top X%" slider, flip between the raw and confounder-adjusted views, and hover the scatter — every chart recomputes client-side from the 2,497 underlying households, nothing is a static image.

## TL;DR

- Public dataset: [dunnhumby "The Complete Journey"](https://www.kaggle.com/datasets/frtgnn/dunnhumby-the-complete-journey) (2,497 households, 102 weeks of transactions).
- Observation window weeks 1–52, outcome window weeks 53–102. "High value" = top quartile of future trip frequency.
- **Raw** relationship: highest category-breadth quartile households are ~59% high-value vs. ~3.5% in the lowest quartile — a huge, suspicious gap.
- The obvious confounder: high-breadth households were already shopping far more often, so they simply had more chances to touch more categories.
- **Adjusted** for prior trip frequency and prior spend (OLS, HC3 robust SE): category breadth still carries incremental signal — roughly **+3–4% future trips per 10 additional year-one categories** (p < 0.001).
- This is an **association, not a causal estimate**. Next step: a real intervention that nudges comparable customers toward one more relevant category, measured against a control group.

## Repo layout

```
analysis/
  high_value_habits.ipynb   the polished, narrated analysis (start here)
  exploration_raw.ipynb     the messier first pass — kept as-is to show the actual process
app/
  index.html, data.js       the interactive artifact above, as static files
  export_data.py            regenerates app/data.js from the raw dataset (pandas + statsmodels)
requirements.txt
```

To rerun the notebook or the export script: `pip install -r requirements.txt`, then run either — `kagglehub` downloads the dataset automatically on first use.

## How this was built

This is meant as an **AI-assisted work sample**, so here's the actual division of labor rather than a generic "built with AI" line:

- The question, the study design (observation/outcome window split, the "high value = top quartile of future trips" operationalization), and the decision to *distrust* the raw relationship and go looking for the confounder were mine.
- I worked with **Claude Code** end-to-end on execution: writing the pandas aggregation and OLS/HC3 regression, turning the exploratory notebook (`exploration_raw.ipynb`) into the narrated, cleaned-up version, building the interactive exploration tool in `app/` (vanilla JS, SVG charts computed live from the data — including a client-side delta-method confidence band off the model's covariance matrix), and setting up this repo end to end, including this README and the GitHub push.
- Every number on the interactive page is computed from the real household-level data at view time — nothing is a canned screenshot.

<!-- TODO(santiago): if you used AI earlier in exploration_raw.ipynb too (picking the dataset, debugging pandas, etc.), say so here specifically — this note currently only describes what happened in the Claude Code session that produced the clean notebook and the app. -->

## Caveats

- This is an **observational, association study** on an already-frequent-shopper population (the dunnhumby panel). It does not show that *causing* a household to adopt another category increases loyalty — selection and unobserved differences remain.
- "High value" here is an operational definition (top quartile of future trips), not a business-validated LTV metric.
