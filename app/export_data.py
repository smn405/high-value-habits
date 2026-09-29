import os, json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import kagglehub

path = kagglehub.dataset_download("frtgnn/dunnhumby-the-complete-journey")

transactions = pd.read_csv(os.path.join(path, "transaction_data.csv"))
products = pd.read_csv(os.path.join(path, "product.csv"))

df = transactions.merge(products[["PRODUCT_ID", "COMMODITY_DESC"]], on="PRODUCT_ID", how="left")

past = df[df["WEEK_NO"] <= 52].copy()
future = df[df["WEEK_NO"] > 52].copy()

past_behavior = (
    past.groupby("household_key")
    .agg(
        trips=("BASKET_ID", "nunique"),
        spend=("SALES_VALUE", "sum"),
        active_weeks=("WEEK_NO", "nunique"),
        commodity_breadth=("COMMODITY_DESC", "nunique"),
    )
    .reset_index()
)

future_value = (
    future.groupby("household_key")
    .agg(
        future_trips=("BASKET_ID", "nunique"),
        future_spend=("SALES_VALUE", "sum"),
        future_active_weeks=("WEEK_NO", "nunique"),
    )
    .reset_index()
)

analysis = past_behavior.merge(future_value, on="household_key", how="left", validate="1:1")
analysis[["future_trips", "future_spend", "future_active_weeks"]] = analysis[
    ["future_trips", "future_spend", "future_active_weeks"]
].fillna(0)

analysis["log_trips"] = np.log1p(analysis["trips"])
analysis["log_spend"] = np.log1p(analysis["spend"])
analysis["log_future_trips"] = np.log1p(analysis["future_trips"])
analysis["commodity_breadth_10"] = analysis["commodity_breadth"] / 10

model = smf.ols(
    "log_future_trips ~ log_trips + log_spend + commodity_breadth_10", data=analysis
).fit(cov_type="HC3")

# Household-level rows for the client-side scatter / recompute (rounded, only what's needed)
rows = analysis[
    ["household_key", "trips", "spend", "commodity_breadth", "future_trips", "future_spend"]
].copy()
rows["spend"] = rows["spend"].round(1)
rows["future_spend"] = rows["future_spend"].round(1)
records = rows.to_dict(orient="records")

param_order = list(model.params.index)
cov = model.cov_params().loc[param_order, param_order].values.tolist()

out = {
    "n_households": int(len(analysis)),
    "households": records,
    "model": {
        "param_order": param_order,
        "params": {k: float(v) for k, v in model.params.items()},
        "bse": {k: float(v) for k, v in model.bse.items()},
        "pvalues": {k: float(v) for k, v in model.pvalues.items()},
        "cov": cov,
        "rsquared": float(model.rsquared),
        "median_log_trips": float(np.log1p(analysis["trips"].median())),
        "median_log_spend": float(np.log1p(analysis["spend"].median())),
        "p25_trips": float(analysis["trips"].quantile(0.25)),
        "p25_spend": float(analysis["spend"].quantile(0.25)),
        "p75_trips": float(analysis["trips"].quantile(0.75)),
        "p75_spend": float(analysis["spend"].quantile(0.25 * 3)),
        "median_trips": float(analysis["trips"].median()),
        "median_spend": float(analysis["spend"].median()),
        "breadth_p10": float(analysis["commodity_breadth"].quantile(0.10)),
        "breadth_p90": float(analysis["commodity_breadth"].quantile(0.90)),
    },
}

out_path = "/private/tmp/claude-501/-Users-santiagonovoa-walmart/ef80b4e3-38eb-4210-8d95-401e4022e349/scratchpad/analysis_data.json"
with open(out_path, "w") as f:
    json.dump(out, f)

print("wrote", out_path, "households:", len(records))
print(model.summary())
