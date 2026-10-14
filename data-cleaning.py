import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# SUPERMARKET CASE STUDY
# ============================================================

# CSV FILE
df = pd.read_csv("supermarket_sales_case_study.csv")


# ============================================================
# STEP 1: LOAD AND LOOK
# ============================================================

print("\n" + "=" * 60)
print("STEP 1: LOAD AND LOOK")
print("=" * 60)

print("Rows and Columns:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nColumn Types:")
print(df.dtypes)


# ============================================================
# STEP 2: AUDIT BEFORE YOU FIX
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: AUDIT BEFORE YOU FIX")
print("=" * 60)

# Missing values
print("\nMissing values:")
print(df.isnull().sum())


# Exact duplicate rows
print("\nExact duplicate rows:")
print(df.duplicated().sum())


# Invoice IDs that appear more than once
print("\nInvoice IDs appearing more than once:")

invoice_counts = df["Invoice ID"].value_counts()

print(
    invoice_counts[
        invoice_counts > 1
    ]
)


# Gender values
print("\nDistinct Gender values:")
print(df["Gender"].unique())


# Payment values
print("\nDistinct Payment values:")
print(df["Payment"].unique())


# ============================================================
# AUDIT TRAIL
# ============================================================

audit_trail = []


def add_audit(step, before, after):

    audit_trail.append({
        "Step": step,
        "Rows Before": before,
        "Rows After": after,
        "Rows Removed": before - after
    })


# ============================================================
# STEP 3: DROP EXACT DUPLICATES
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: DROP EXACT DUPLICATES")
print("=" * 60)

before = len(df)

df = df.drop_duplicates().copy()

after = len(df)

add_audit(
    "Step 3 - Drop exact duplicates",
    before,
    after
)

print("Rows before:", before)
print("Rows after:", after)
print("Rows removed:", before - after)


# ============================================================
# STEP 4: RESOLVE CONFLICTING INVOICE IDs
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: RESOLVE CONFLICTING INVOICE IDs")
print("=" * 60)

before = len(df)

# Rule:
# If an Invoice ID appears more than once,
# the later row is the correction.
# Therefore, keep the LAST row.

df = df.drop_duplicates(
    subset="Invoice ID",
    keep="last"
).copy()

after = len(df)

add_audit(
    "Step 4 - Resolve conflicting Invoice IDs",
    before,
    after
)

print("Rows before:", before)
print("Rows after:", after)
print("Rows removed:", before - after)


# ============================================================
# STEP 5: STANDARDISE TEXT COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("STEP 5: STANDARDISE TEXT COLUMNS")
print("=" * 60)


# -------------------------
# Gender
# -------------------------

df["Gender"] = (
    df["Gender"]
    .astype("string")
    .str.strip()
    .str.lower()
)

gender_map = {
    "male": "Male",
    "m": "Male",
    "female": "Female",
    "f": "Female"
}

df["Gender"] = df["Gender"].map(gender_map)


# -------------------------
# Payment
# -------------------------

df["Payment"] = (
    df["Payment"]
    .astype("string")
    .str.strip()
    .str.lower()
)

payment_map = {
    "cash": "Cash",
    "credit card": "Credit card",
    "creditcard": "Credit card",
    "credit-card": "Credit card",
    "ewallet": "Ewallet",
    "e-wallet": "Ewallet",
    "e wallet": "Ewallet"
}

df["Payment"] = df["Payment"].map(payment_map)


print("\nGender after cleaning:")
print(df["Gender"].value_counts(dropna=False))

print("\nPayment after cleaning:")
print(df["Payment"].value_counts(dropna=False))


# ============================================================
# STEP 6: FIX NEGATIVE QUANTITIES
# ============================================================

print("\n" + "=" * 60)
print("STEP 6: FIX NEGATIVE QUANTITIES")
print("=" * 60)

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
)

negative_count = (
    df["Quantity"] < 0
).sum()

print(
    "Negative quantities before:",
    negative_count
)

# Minus sign is a typing error.
# Convert negative quantities to positive.

df["Quantity"] = df["Quantity"].abs()

print(
    "Negative quantities after:",
    (df["Quantity"] < 0).sum()
)


# ============================================================
# STEP 7: PARSE MIXED DATES
# ============================================================

print("\n" + "=" * 60)
print("STEP 7: PARSE MIXED DATES")
print("=" * 60)


# Convert to string
date_text = (
    df["Date"]
    .astype("string")
    .str.strip()
)


# First format:
# month/day/year
# Example: 1/6/2023

date_1 = pd.to_datetime(
    date_text,
    format="%m/%d/%Y",
    errors="coerce"
)


# Second format:
# day-month-year
# Example: 06-01-2023

date_2 = pd.to_datetime(
    date_text,
    format="%d-%m-%Y",
    errors="coerce"
)


# Use first format, then second
df["Date"] = date_1.fillna(date_2)


print(
    "Missing/invalid dates:",
    df["Date"].isna().sum()
)


# ============================================================
# STEP 8: CHECK TOTAL
# ============================================================

print("\n" + "=" * 60)
print("STEP 8: CHECK TOTAL")
print("=" * 60)


df["Unit price"] = pd.to_numeric(
    df["Unit price"],
    errors="coerce"
)

df["Total"] = pd.to_numeric(
    df["Total"],
    errors="coerce"
)


# Formula:
# Total = Quantity × Unit price × 1.05

calculated_total = (
    df["Quantity"]
    * df["Unit price"]
    * 1.05
)


# Difference between existing Total
# and calculated Total

difference = (
    df["Total"] - calculated_total
).abs()


wrong_total = (
    difference > 0.50
)


print(
    "Incorrect Total values:",
    wrong_total.sum()
)


# Replace Total if difference > $0.50

df.loc[
    wrong_total,
    "Total"
] = calculated_total[
    wrong_total
]


# ============================================================
# STEP 9: HANDLE REMAINING MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("STEP 9: HANDLE REMAINING MISSING VALUES")
print("=" * 60)


# Customer type -> Unknown

df["Customer type"] = (
    df["Customer type"]
    .astype("string")
    .str.strip()
)

df["Customer type"] = (
    df["Customer type"]
    .fillna("Unknown")
)


# Rating -> median

df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

rating_median = df["Rating"].median()

print(
    "Rating median:",
    rating_median
)

df["Rating"] = (
    df["Rating"]
    .fillna(rating_median)
)


# Drop rows without Date

before = len(df)

df = df.dropna(
    subset=["Date"]
).copy()

after = len(df)

add_audit(
    "Step 9 - Remove rows with missing Date",
    before,
    after
)

print(
    "Rows removed:",
    before - after
)


# ============================================================
# STEP 10: AUDIT TRAIL
# ============================================================

print("\n" + "=" * 60)
print("STEP 10: AUDIT TRAIL")
print("=" * 60)

audit_df = pd.DataFrame(
    audit_trail
)

print(audit_df)

audit_df.to_csv(
    "cleaning_audit_trail.csv",
    index=False
)


# ============================================================
# ANSWERING THE BRIEF
# ============================================================


# ============================================================
# 1. ADD TIME COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("TIME COLUMNS")
print("=" * 60)


# Year
df["Year"] = df["Date"].dt.year


# Quarter
df["Quarter"] = (
    df["Date"].dt.year.astype(str)
    + "Q"
    + df["Date"].dt.quarter.astype(str)
)


# Day of week
df["Day of week"] = (
    df["Date"].dt.day_name()
)


# Hour
time_parsed = pd.to_datetime(
    df["Time"].astype(str),
    errors="coerce"
)

df["Hour"] = time_parsed.dt.hour


print(
    df[
        [
            "Date",
            "Time",
            "Year",
            "Quarter",
            "Day of week",
            "Hour"
        ]
    ].head()
)


# ============================================================
# 2. BUCKET THE TRADING DAY
# ============================================================

print("\n" + "=" * 60)
print("TRADING DAY BUCKETS")
print("=" * 60)


def trading_bucket(hour):

    if pd.isna(hour):
        return np.nan

    if 10 <= hour < 13:
        return "Morning"

    elif 13 <= hour < 17:
        return "Afternoon"

    elif 17 <= hour < 21:
        return "Evening"

    else:
        return np.nan


df["Trading Period"] = (
    df["Hour"]
    .apply(trading_bucket)
)


# Hours per bucket

bucket_hours = {
    "Morning": 3,
    "Afternoon": 4,
    "Evening": 4
}


# Transactions
transactions = (
    df.groupby("Trading Period")
    .size()
)


# Transactions per hour
transactions_per_hour = (
    transactions
    / pd.Series(bucket_hours)
)


print(
    "\nTransactions per hour:"
)

print(
    transactions_per_hour
)


# ============================================================
# 3. REVENUE PER BRANCH PER QUARTER
# ============================================================

print("\n" + "=" * 60)
print("BRANCH QUARTERLY REVENUE")
print("=" * 60)


quarterly = (
    df.groupby(
        ["Branch", "Year", "Quarter"],
        as_index=False
    )["Total"]
    .sum()
)

quarterly = quarterly.rename(
    columns={
        "Total": "Revenue"
    }
)


# Target
quarterly["Target"] = 100000


# Variance
quarterly["Variance"] = (
    quarterly["Revenue"]
    - quarterly["Target"]
)


# Percentage of target
quarterly["% of target"] = (
    quarterly["Revenue"]
    / quarterly["Target"]
    * 100
)


# Hit?
quarterly["Hit"] = (
    quarterly["Revenue"]
    >= quarterly["Target"]
)


print(quarterly)


# Save
quarterly.to_csv(
    "quarterly_branch_revenue.csv",
    index=False
)


# ============================================================
# 4. SUMMARISE EACH BRANCH
# ============================================================

print("\n" + "=" * 60)
print("BRANCH SUMMARY")
print("=" * 60)


branch_summary = (
    quarterly
    .groupby("Branch")
    .agg(
        Average_Quarterly_Revenue=(
            "Revenue",
            "mean"
        ),
        Quarters_Hit=(
            "Hit",
            "sum"
        ),
        Total_Quarters=(
            "Hit",
            "count"
        )
    )
    .reset_index()
)


# Best quarter

best = (
    quarterly.loc[
        quarterly.groupby(
            "Branch"
        )["Revenue"].idxmax()
    ]
    [
        [
            "Branch",
            "Quarter",
            "Revenue"
        ]
    ]
)

best = best.rename(
    columns={
        "Quarter": "Best Quarter",
        "Revenue": "Best Quarter Revenue"
    }
)


# Worst quarter

worst = (
    quarterly.loc[
        quarterly.groupby(
            "Branch"
        )["Revenue"].idxmin()
    ]
    [
        [
            "Branch",
            "Quarter",
            "Revenue"
        ]
    ]
)

worst = worst.rename(
    columns={
        "Quarter": "Worst Quarter",
        "Revenue": "Worst Quarter Revenue"
    }
)


# Merge

branch_summary = branch_summary.merge(
    best,
    on="Branch",
    how="left"
)

branch_summary = branch_summary.merge(
    worst,
    on="Branch",
    how="left"
)


# ============================================================
# YoY GROWTH
# ============================================================

year_revenue = (
    quarterly
    .groupby(
        ["Branch", "Year"]
    )["Revenue"]
    .sum()
    .unstack()
)


if 2023 in year_revenue.columns and 2024 in year_revenue.columns:

    year_revenue["YoY Growth %"] = (
        (
            year_revenue[2024]
            /
            year_revenue[2023]
        )
        - 1
    ) * 100

    yoy = (
        year_revenue[
            ["YoY Growth %"]
        ]
        .reset_index()
    )

    branch_summary = branch_summary.merge(
        yoy,
        on="Branch",
        how="left"
    )


print(branch_summary)


branch_summary.to_csv(
    "branch_summary.csv",
    index=False
)


# ============================================================
# 5. FIND BUSY TIMES
# ============================================================

print("\n" + "=" * 60)
print("BUSY TIMES")
print("=" * 60)


# Transactions per weekday

weekday_transactions = (
    df.groupby("Day of week")
    .size()
)


# Number of actual dates for each weekday

weekday_count = (
    df[
        [
            "Date",
            "Day of week"
        ]
    ]
    .drop_duplicates()
    .groupby("Day of week")
    .size()
)


# Average per day

average_per_day = (
    weekday_transactions
    / weekday_count
)


weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


average_per_day = (
    average_per_day
    .reindex(weekday_order)
)


print(
    "\nAverage transactions per day:"
)

print(
    average_per_day
)


# ============================================================
# HOUR + WEEKDAY HEATMAP DATA
# ============================================================

hour_weekday = (
    df.groupby(
        [
            "Day of week",
            "Hour"
        ]
    )
    .size()
)


heatmap_data = (
    hour_weekday
    / weekday_count
)


heatmap_data = (
    heatmap_data
    .unstack(
        level=0
    )
    .reindex(
        columns=weekday_order
    )
)


print(
    "\nHour x weekday average:"
)

print(
    heatmap_data
)


# ============================================================
# HEATMAP
# ============================================================

plt.figure(
    figsize=(12, 7)
)

plt.imshow(
    heatmap_data.T,
    aspect="auto",
    cmap="YlOrRd"
)

plt.colorbar(
    label="Average Transactions per Day"
)

plt.xticks(
    range(len(heatmap_data.index)),
    heatmap_data.index
)

plt.yticks(
    range(len(heatmap_data.columns)),
    heatmap_data.columns
)

plt.xlabel("Hour")
plt.ylabel("Day of Week")

plt.title(
    "Average Transactions by Hour and Day of Week"
)

plt.tight_layout()

plt.savefig(
    "busy_times_heatmap.png",
    dpi=300
)

plt.show()


# ============================================================
# 6. CHART EACH BRANCH'S 8 QUARTERS
# ============================================================

print("\n" + "=" * 60)
print("BRANCH REVENUE CHART")
print("=" * 60)


plt.figure(
    figsize=(12, 7)
)


for branch in sorted(
    quarterly["Branch"].unique()
):

    branch_data = (
        quarterly[
            quarterly["Branch"] == branch
        ]
        .sort_values(
            ["Year", "Quarter"]
        )
    )

    plt.plot(
        branch_data["Quarter"],
        branch_data["Revenue"],
        marker="o",
        label=f"Branch {branch}"
    )


# Target line

plt.axhline(
    y=100000,
    color="red",
    linestyle="--",
    label="Target = $100,000"
)


plt.title(
    "Quarterly Revenue by Branch"
)

plt.xlabel(
    "Quarter"
)

plt.ylabel(
    "Revenue ($)"
)

plt.xticks(
    rotation=45
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "branch_quarterly_revenue.png",
    dpi=300
)

plt.show()


# ============================================================
# SAVE CLEAN DATA
# ============================================================

df.to_csv(
    "supermarket_sales_cleaned.csv",
    index=False
)


# ============================================================
# FIVE-LINE MANAGEMENT SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("MANAGEMENT SUMMARY")
print("=" * 60)


for _, row in branch_summary.iterrows():

    print(
        f"Branch {row['Branch']} average quarterly "
        f"revenue was ${row['Average_Quarterly_Revenue']:,.2f}."
    )

    print(
        f"Branch {row['Branch']} hit the $100,000 target "
        f"in {int(row['Quarters_Hit'])} of "
        f"{int(row['Total_Quarters'])} quarters."
    )

    print(
        f"Branch {row['Branch']} best quarter was "
        f"{row['Best Quarter']} with "
        f"${row['Best Quarter Revenue']:,.2f} revenue."
    )

    print(
        f"Branch {row['Branch']} worst quarter was "
        f"{row['Worst Quarter']} with "
        f"${row['Worst Quarter Revenue']:,.2f} revenue."
    )

    if "YoY Growth %" in branch_summary.columns:
        print(
            f"Branch {row['Branch']} YoY growth was "
            f"{row['YoY Growth %']:.2f}%."
        )

    print()


# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("COMPLETED")
print("=" * 60)

print(
    "Final rows:",
    len(df)
)

print(
    "Final columns:",
    len(df.columns)
)

print("\nFiles created:")

print("- supermarket_sales_cleaned.csv")
print("- cleaning_audit_trail.csv")
print("- quarterly_branch_revenue.csv")
print("- branch_summary.csv")
print("- busy_times_heatmap.png")
print("- branch_quarterly_revenue.png")