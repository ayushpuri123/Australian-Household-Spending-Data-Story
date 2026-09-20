from pathlib import Path
import pandas as pd

data_folder = Path("data/raw")

# Finds Excel files even if ABS put them inside another folder
files = list(data_folder.rglob("*.xlsx"))

print(f"\nFound {len(files)} Excel files.\n")

for file in files:
    print("=" * 70)
    print("FILE:", file.name)

    excel_file = pd.ExcelFile(file)

    print("SHEETS:")
    for sheet in excel_file.sheet_names:
        print("  -", sheet)

    print()
    