import pandas as pd
import numpy as np
import re

from rcp_lvl99_simulation import add_time_to_99
from extract_leveling_table import get_leveling_data

# ================================
# HELPER FUNCTIONS
# ================================

def clean_int(text):
    return int(re.sub(r"[^\d-]", "", str(text))) if pd.notna(text) else None


# ================================
# STEP 1 → CLEANING
# ================================

def clean_recipes(df):

    print("\n🧹 STARTING CLEANING STEP")

    print("🧼 Cleaning numeric fields...")
    df["rcp_cost"] = df["rcp_cost"].apply(clean_int).abs()
    df["rcp_income"] = df["rcp_income"].apply(clean_int)
    df["rcp_xp"] = df["rcp_xp"].apply(clean_int)
    df["rcp_servings"] = df["rcp_servings"].apply(clean_int)

    print("🛠 Fixing known issues...")
    fixes = {
        "Turtle Soup": "0.25 hrs",
        "Salmon Nigiri": "0.50 hrs",
        "Gilded Champagne": "1.00 hrs",
        "Midnight Martini": "3.00 hrs",
        "Golden Hour Cocktail": "8.00 hrs",
        "Silver Star Cupcakes": "8.00 hrs"
    }

    for k, v in fixes.items():
        df.loc[df["rcp_name"] == k, "rcp_time_hr"] = v

    
    print("✅ CLEANING COMPLETE")

    return df


# ================================
# STEP 2 → FEATURE ENGINEERING
# ================================

def time_profit_obtainability_column(df):

    print("\n⚙️ STARTING FEATURE ENGINEERING")

    print("⏱ Standardizing time format...")
    df["rcp_time_min"] = (
        pd.to_numeric(df["rcp_time_hr"].str.extract(r'(\d+\.?\d*)')[0], errors="coerce")
        .mul(60)
        .round()
        .astype("Int64")
    )
    
    print("📈 Calculating profit...")
    df["rcp_profit"] = df["rcp_income"] - df["rcp_cost"]

    print("🏷 Calculating obtainability...")
    df['rcp_obtainability'] = np.where(
        df['rcp_labels'].isna() |
        (df['rcp_labels'].str.strip().str.lower().isin(['', 'nan'])),
        'easy',
        'hard'
    )

    print("✅ FEATURE ENGINEERING COMPLETE")

    return df


# ================================
# PIPELINE WRAPPER
# ================================

def transform_recipes(input_csv, output_csv):

    print("\n🔧 STARTING TRANSFORMATION PIPELINE\n")

    df = pd.read_csv(input_csv)
    print(f"📥 Loaded → {len(df)} rows")

    # Step 1: Cleaning
    df = clean_recipes(df)

    # Step 2: Feature Engineering
    df = time_profit_obtainability_column(df)

    # -------- LOAD DATA --------
    try:
        df_leveling = pd.read_csv("data/leveling.csv")
        print("✅ Loaded leveling data from CSV")

    except FileNotFoundError:
        print("⚠️ CSV not found. Fetching data using function...")
        df_leveling = get_leveling_data("data/leveling.csv")

    df.to_csv(output_csv, index=False)

    df = add_time_to_99(df, df_leveling)

    df.to_csv(output_csv, index=False)

    print("\n✅ TRANSFORMATION COMPLETE")
    print(f"📁 CLEAN saved → {output_csv}")

    return df


# ================================
# TEST / RUN ENTRY POINT
# ================================

if __name__ == "__main__":

    RUN_MODE = "both"   # restaurant | bakery | both

    INPUTS = {
        "restaurant": "data_test/restaurant/01_recipes_all_raw.csv",
        "bakery": "data_test/bakery/01_recipes_all_raw.csv"
    }

    OUTPUTS = {
        "restaurant": "data_test/restaurant/02_recipes_all_clean.csv",
        "bakery": "data_test/bakery/02_recipes_all_clean.csv"
    }

    URLS = {
        "restaurant": "https://stm.gamerologizm.com/s8/restaurant_recipes_all.php?page={}",
        "bakery": "https://stm.gamerologizm.com/s8/bakery_recipes_all.php?page={}#content"
    }

    if RUN_MODE in ["restaurant", "both"]:
        transform_recipes(INPUTS["restaurant"], OUTPUTS["restaurant"])

    if RUN_MODE in ["bakery", "both"]:
        transform_recipes(INPUTS["bakery"], OUTPUTS["bakery"])