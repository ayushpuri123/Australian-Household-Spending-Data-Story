from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PATHS
# ---------------------------------------------------

DATA_FILE = Path(
    "data/processed/household_spending_seasonally_adjusted.csv"
)

OUTPUT_FOLDER = Path("outputs/charts")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = pd.read_csv(DATA_FILE)

df["date"] = pd.to_datetime(df["date"])

latest_date = df["date"].max()

yoy_metric = "Household spending - Through the year percentage change"

SOURCE_NOTE = (
    "Source: Australian Bureau of Statistics, Monthly Household Spending Indicator, "
    "July 2026. Seasonally adjusted, current prices."
)


# ---------------------------------------------------
# CHART 1
# NATIONAL CATEGORY GROWTH
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

category_growth = df[
    (df["date"] == latest_date)
    & (df["geography"] == "Australia")
    & (df["metric"] == yoy_metric)
    & (df["category"].isin(categories))
].copy()

category_growth = category_growth.sort_values(
    "value",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    category_growth["category"],
    category_growth["value"]
)

for i, value in enumerate(category_growth["value"]):
    plt.text(
        value + 0.1,
        i,
        f"{value:.1f}%",
        va="center"
    )

plt.xlabel("Year-on-year spending growth (%)")

plt.title(
    "Recreation and culture leads Australian household spending growth\n"
    "July 2026"
)

plt.xlim(
    0,
    category_growth["value"].max() + 1.2
)

plt.figtext(
    0.01,
    0.01,
    SOURCE_NOTE,
    ha="left",
    fontsize=8
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

plt.savefig(
    OUTPUT_FOLDER / "category_growth_july_2026.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ---------------------------------------------------
# CHART 2
# DISCRETIONARY VS NON-DISCRETIONARY OVER TIME
# ---------------------------------------------------

spending_type = df[
    (df["geography"] == "Australia")
    & (df["metric"] == yoy_metric)
    & (
        df["category"].isin([
            "Discretionary",
            "Non Discretionary"
        ])
    )
].copy()

pivot = spending_type.pivot_table(
    index="date",
    columns="category",
    values="value",
    aggfunc="mean"
)

pivot = pivot[
    pivot.index >= "2022-01-01"
]

plt.figure(figsize=(11, 6))

plt.plot(
    pivot.index,
    pivot["Discretionary"],
    label="Discretionary"
)

plt.plot(
    pivot.index,
    pivot["Non Discretionary"],
    label="Non-discretionary"
)

plt.axhline(
    0,
    linewidth=1
)

plt.ylabel("Year-on-year spending growth (%)")

plt.title(
    "Discretionary spending growth has overtaken non-discretionary spending\n"
    "Australia, January 2022 to July 2026"
)

plt.legend()

plt.figtext(
    0.01,
    0.01,
    SOURCE_NOTE,
    ha="left",
    fontsize=8
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

plt.savefig(
    OUTPUT_FOLDER / "discretionary_vs_non_discretionary.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ---------------------------------------------------
# CHART 3
# STATE / TERRITORY GROWTH
# ---------------------------------------------------

state_growth = df[
    (df["date"] == latest_date)
    & (df["geography"] != "Australia")
    & (df["metric"] == yoy_metric)
    & (
        df["category"]
        == "Total (Household Spending Categories)"
    )
].copy()

state_growth = state_growth.sort_values(
    "value",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    state_growth["geography"],
    state_growth["value"]
)

for i, value in enumerate(state_growth["value"]):
    plt.text(
        value + 0.1,
        i,
        f"{value:.1f}%",
        va="center"
    )

plt.xlabel("Year-on-year spending growth (%)")

plt.title(
    "NT and WA record Australia's strongest household spending growth\n"
    "July 2026"
)

plt.xlim(
    0,
    state_growth["value"].max() + 1.2
)

plt.figtext(
    0.01,
    0.01,
    SOURCE_NOTE,
    ha="left",
    fontsize=8
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

plt.savefig(
    OUTPUT_FOLDER / "state_spending_growth.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ---------------------------------------------------
# FINISHED
# ---------------------------------------------------

print("Charts created successfully:")
print("1. category_growth_july_2026.png")
print("2. discretionary_vs_non_discretionary.png")
print("3. state_spending_growth.png")