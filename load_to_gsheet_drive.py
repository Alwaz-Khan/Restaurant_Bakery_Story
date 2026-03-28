import os
import time
import math
import numpy as np
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv
load_dotenv()

# =========================
# 🔁 RETRY LOGIC
# =========================
def retry_api_call(func, retries=5, base_delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            wait = base_delay * (2**attempt)
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            print(f"⏳ Retrying in {wait}s...")
            time.sleep(wait)

    raise Exception("❌ API failed after max retries")


# =========================
# 🧹 CLEAN DATA
# =========================
def clean_dataframe_for_sheets(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.astype(object)
    df = df.where(pd.notnull(df), None)
    return df


# =========================
# 📏 ENSURE SHEET SIZE
# =========================
def ensure_sheet_size(sheet, required_rows, required_cols):
    if sheet.row_count < required_rows or sheet.col_count < required_cols:
        sheet.resize(
            rows=max(sheet.row_count, required_rows),
            cols=max(sheet.col_count, required_cols),
        )


# =========================
# 📦 CORE UPLOAD
# =========================
def upload_dataframe_to_sheet(sheet, df, chunk_size=1000):
    df = clean_dataframe_for_sheets(df)

    data = [df.columns.tolist()] + df.values.tolist()
    total_rows = len(data)

    ensure_sheet_size(sheet, total_rows, len(data[0]))
    retry_api_call(lambda: sheet.clear())

    for i in range(0, total_rows, chunk_size):
        chunk = data[i : i + chunk_size]
        start_row = i + 1

        print(f"⬆️ Uploading rows starting at {start_row}")

        retry_api_call(
            lambda: sheet.update(values=chunk, range_name=f"A{start_row}")
        )


# =========================
# 🚀 PUBLIC FUNCTION (THIS IS WHAT YOU IMPORT)
# =========================
def upload_to_google_sheets(df, creds_path, sheet_name, worksheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)


    sheet = client.open(sheet_name).worksheet(worksheet_name)

    upload_dataframe_to_sheet(sheet, df)




# =========================
# 🚀 ENTRY POINT
# =========================
if __name__ == "__main__":
    
    df = pd.read_csv("data/master.csv")

    upload_to_google_sheets(
        df,
        creds_path=os.getenv("GOOGLE_CREDENTIALS_PATH"),
        sheet_name=os.getenv("GSHEET_NAME"),
        worksheet_name=os.getenv("GSHEET_WORKSHEET"),
    )

    print("✅ Pipeline complete")

