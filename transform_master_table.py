import pandas as pd
import numpy as np

def transform_master(final_df):

    # Column normalization
    rcp_col = "rcp_obtainability"
    appl_col = "appl_obtainability"

    final_df[rcp_col] = final_df[rcp_col].astype(str).str.lower()
    final_df[appl_col] = final_df[appl_col].astype(str).str.lower()

    # Score calculation
    score = np.where(final_df[rcp_col] == "easy", 1, 3) + np.where(
        final_df[appl_col] == "easy", 1,
        np.where(final_df[appl_col] == "medium", 2, 3)
    )

    final_df["rcp_difficulty"] = score
    print("✅ Added column: rcp_difficulty")

    # Column ordering
    priority_cols = [
        "game_mode",
        "rcp_name",
        "appl_name",
        "rcp_level",
        "rcp_time_min",
        "rcp_xp",
        "rcp_profit",
        "rcp_difficulty",
        "min_to_lvl99",
        "time_to_lvl99"
    ]

    priority_cols = [col for col in priority_cols if col in final_df.columns]
    remaining_cols = [col for col in final_df.columns if col not in priority_cols]

    final_df = final_df[priority_cols + remaining_cols]
    print("✅ Columns reordered successfully")

    return final_df



# =========================
# 🚀 ENTRY POINT
# =========================
if __name__ == "__main__":
    
    df = pd.read_csv("data/master_raw.csv")
    final_df = transform_master(df)
    

    # Optional: save output
    final_df.to_csv("data/master_table.csv", index=False)
    print("✅ Saved master.csv")