from pathlib import Path
import pandas as pd

RAW_FOLDER = Path("data/raw")
PROCESSED_FOLDER = Path("data/processed")

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

# Only household spending files 1–10
wanted_files = {
    f"56820{i:02d}.xlsx"
    for i in range(1, 11)
}

files = [
    file for file in RAW_FOLDER.rglob("*.xlsx")
    if file.name in wanted_files
]

print(f"Using {len(files)} household spending files.")


def load_abs_file(file_path):
    raw = pd.read_excel(
        file_path,
        sheet_name="Data1",
        header=None
    )

    # ABS metadata rows
    descriptions = raw.iloc[0]
    units = raw.iloc[1]
    series_types = raw.iloc[2]

    # Actual monthly data starts on Excel row 11
    data = raw.iloc[10:].copy()

    # First column contains Excel serial dates
    dates = pd.to_datetime(
        data.iloc[:, 0],
        errors="coerce"

    )

    frames = []

    for col in range(1, raw.shape[1]):

        # We only want Seasonally Adjusted data
        if str(series_types.iloc[col]).strip() != "Seasonally Adjusted":
            continue

        description = str(descriptions.iloc[col]).strip()

        if description == "" or description == "nan":
            continue

        parts = [
            part.strip()
            for part in description.split(";")
            if part.strip()
        ]

        if len(parts) < 3:
            continue

        metric = parts[0]
        category = parts[1]
        geography = parts[2]

        values = pd.to_numeric(
            data.iloc[:, col],
            errors="coerce"
        )

        temp = pd.DataFrame({
            "date": dates.reset_index(drop=True),
            "metric": metric,
            "category": category,
            "geography": geography,
            "unit": str(units.iloc[col]),
            "series_type": "Seasonally Adjusted",
            "value": values.reset_index(drop=True)
        })

        frames.append(temp)

    return pd.concat(frames, ignore_index=True)


# Combine all household spending files
all_data = pd.concat(
    [load_abs_file(file) for file in files],
    ignore_index=True
)

all_data = all_data.dropna(
    subset=["date", "value"]
)

# Remove duplicated Australia series appearing across tables
all_data = all_data.drop_duplicates(
    subset=[
        "date",
        "metric",
        "category",
        "geography",
        "series_type"
    ]
)

all_data = all_data.sort_values(
    ["date", "geography", "category"]
)

# Save clean dataset
output_file = (
    PROCESSED_FOLDER /
    "household_spending_seasonally_adjusted.csv"
)

all_data.to_csv(output_file, index=False)

print("\nClean dataset saved:")
print(output_file)


# ---------------------------------------------------
# LATEST MONTH ANALYSIS
# ---------------------------------------------------

latest_date = all_data["date"].max()

print("\nLatest month:")
print(latest_date.strftime("%B %Y"))


yoy_metric = (
    "Household spending - Through the year percentage change"
)


# ---------------------------------------------------
# 1. NATIONAL CATEGORY GROWTH
# ---------------------------------------------------

categories = [
    "Food",
    "Alcoholic beverages and tobacco",
    "Clothing and footwear",
    "Furnishings and household equipment",
    "Health",
    "Transport",
    "Recreation and culture",
    "Hotels, cafes and restaurants",
    "Miscellaneous goods and services"
]

national_categories = all_data[
    (all_data["date"] == latest_date)
    & (all_data["geography"] == "Australia")
    & (all_data["metric"] == yoy_metric)
    & (all_data["category"].isin(categories))
].copy()

national_categories = national_categories.sort_values(
    "value",
    ascending=False
)

print("\nNATIONAL CATEGORY GROWTH:")
print(
    national_categories[
        ["category", "value"]
    ].to_string(index=False)
)


# ---------------------------------------------------
# 2. DISCRETIONARY VS NON-DISCRETIONARY
# ---------------------------------------------------

disc = all_data[
    (all_data["date"] == latest_date)
    & (all_data["geography"] == "Australia")
    & (all_data["metric"] == yoy_metric)
    & (
        all_data["category"].isin([
            "Discretionary",
            "Non Discretionary"
        ])
    )
].copy()

print("\nDISCRETIONARY VS NON-DISCRETIONARY:")
print(
    disc[
        ["category", "value"]
    ].to_string(index=False)
)


# ---------------------------------------------------
# 3. STATE TOTAL SPENDING GROWTH
# ---------------------------------------------------

states = all_data[
    (all_data["date"] == latest_date)
    & (all_data["geography"] != "Australia")
    & (all_data["metric"] == yoy_metric)
    & (
        all_data["category"]
        == "Total (Household Spending Categories)"
    )
].copy()

states = states.sort_values(
    "value",
    ascending=False
)

print("\nSTATE SPENDING GROWTH:")
print(
    states[
        ["geography", "value"]
    ].to_string(index=False)
)