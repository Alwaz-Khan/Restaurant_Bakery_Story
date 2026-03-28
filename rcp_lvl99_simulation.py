import pandas as pd
import numpy as np


# =========================
# ⚡ PREP LEVEL ARRAYS (ONE TIME)
# =========================


def prepare_level_arrays(df_levels):
    df_levels.columns = df_levels.columns.str.strip().str.lower()

    # 🔴 FORCE NUMERIC CONVERSION
    df_levels["xp"] = (
        df_levels["xp"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df_levels["xp"] = pd.to_numeric(df_levels["xp"], errors="raise")

    df_levels["slots"] = pd.to_numeric(df_levels["slots"], errors="coerce")

    df_levels = df_levels.sort_values("xp")

    xp_array = df_levels["xp"].values.astype(np.int64)
    slots_array = df_levels["slots"].ffill().fillna(2).values.astype(int)

    return xp_array, slots_array


# =========================
# 🔁 FAST SIMULATION FUNCTION
# =========================

def time_to_99_fast(row, xp_array, slots_array, target_xp=803600):

    xp = 0
    cycle = 0
    stoves = 2

    xp_per_dish = row["rcp_xp"]
    cook_time = row["rcp_time_min"]

    idx = 0
    n = len(xp_array)

    while xp < target_xp:
        cycle += 1
        xp += stoves * xp_per_dish

        while idx < n and xp >= xp_array[idx]:
            stoves = slots_array[idx]
            idx += 1

    total_minutes = cycle * cook_time

    return total_minutes  # ✅ return minutes


# ======================================
# 🔁 Custom Time Format FUNCTION
# ======================================

def format_minutes_to_readable(minutes):

    #if pd.isna(minutes):
    #    return None  # or "N/A"

    minutes = int(minutes)

    years = minutes // (60 * 24 * 365)
    minutes %= (60 * 24 * 365)

    months = minutes // (60 * 24 * 30)
    minutes %= (60 * 24 * 30)

    days = minutes // (60 * 24)
    minutes %= (60 * 24)

    hours = minutes // 60
    minutes %= 60

    parts = []

    if years: parts.append(f"{years} years")
    if months: parts.append(f"{months} months")
    if days: parts.append(f"{days} days")
    if hours: parts.append(f"{hours} hours")
    if minutes: parts.append(f"{minutes} minutes")

    return " ".join(parts) if parts else "0 minutes"


# =========================
# 🚀 APPLY TO DATAFRAME
# =========================
def add_time_to_99(df_recipes, df_levels):

    xp_array, slots_array = prepare_level_arrays(df_levels)

    # 🔢 RAW NUMERIC COLUMN
    df_recipes["min_to_lvl99"] = df_recipes.apply(
        time_to_99_fast,
        axis=1,
        xp_array=xp_array,
        slots_array=slots_array
    )

    # 🧾 HUMAN READABLE COLUMN
    df_recipes["time_to_lvl99"] = df_recipes["min_to_lvl99"].apply(
        format_minutes_to_readable
    )

    return df_recipes


# =========================
# 🧪 MAIN (SINGLE + BATCH TEST)
# =========================
if __name__ == "__main__":

    # -------- LOAD DATA --------
    df_leveling = pd.read_csv("data/leveling.csv")

    # Example recipe table
    df_recipes = pd.DataFrame([
        {"rcp_name": "French Toast", "rcp_xp": 6, "rcp_time_min": 1},
        {"rcp_name": "Peking Duck", "rcp_xp": 340, "rcp_time_min": 2760},
        {"rcp_name": "Lemon Lime Soda", "rcp_xp": 209, "rcp_time_min": 2780}
    ])

    # -------- APPLY TO ALL RECIPES --------
    df_recipes = add_time_to_99(df_recipes, df_leveling)

    print("\n=== ALL RECIPES ===")
    #print(df_recipes[["rcp_name", "days_to_99"]])
    print(df_recipes[["rcp_name", "min_to_lvl99", "time_to_lvl99"]])
