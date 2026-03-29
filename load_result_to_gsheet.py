import os
import pandas as pd
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# =========================
# 🔹 CONFIG
# =========================
MODE_DEFAULT = "restaurant"
LEVEL_DEFAULT = 99
DIFFICULTY_DEFAULT = "hard"

# =========================
# 🔹 BUILD BASE DATA
# =========================
def build_df():
    data = [
        [1],[5],[10],[15],[30],[45],[60],
        [120],[180],[360],[540],[720],
        [1440],[2160],[2880]
    ]
    return pd.DataFrame(data, columns=["return_time (min)"])


# =========================
# 🔹 MAIN
# =========================
def push_result_gsheet(creds_path, spreadsheet_name, worksheet_name):

    df = build_df()

    # =========================
    # 🔹 AUTH
    # =========================
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=scope
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open(spreadsheet_name)
    sheet_name = worksheet_name

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # =========================
    # 🔹 ARCHIVE OLD SHEET
    # =========================
    existing = [ws.title for ws in spreadsheet.worksheets()]

    if sheet_name in existing:
        old = spreadsheet.worksheet(sheet_name)
        old.update_title(f"{sheet_name}_{timestamp}")

    # Create new sheet
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

    # =========================
    # 🔹 TITLE
    # =========================
    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 2,
                        "endRowIndex": 4,
                        "startColumnIndex": 1,
                        "endColumnIndex": 7
                    },
                    "mergeType": "MERGE_ALL"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 2,
                        "endRowIndex": 4,
                        "startColumnIndex": 1,
                        "endColumnIndex": 7
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "textFormat": {
                                "bold": True,
                                "fontSize": 30
                            }
                        }
                    },
                    "fields": "userEnteredFormat"
                }
            }
        ]
    })

    sheet.update(
        range_name="B3",
        values=[["Bakery/Restaurant Story"]]
    )

    # =========================
    # 🔹 FILTER UI
    # =========================
 
    # =========================
    # 🚀 SETUP GAME MODE FILTER
    # =========================
    sheet.update(range_name="H3", values=[["Mode"]])

    sheet.spreadsheet.batch_update({
        "requests": [
            # 🔹 Data Validation (H4)
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 3,
                        "endRowIndex": 4,
                        "startColumnIndex": 7,
                        "endColumnIndex": 8
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": "restaurant"},
                                {"userEnteredValue": "bakery"}
                            ]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            },
        ]
    })

    # 🔹 Default value
    sheet.update(
        range_name="H4",
        values=[["bakery"]]
    )

    # =========================
    # 🚀 SETUP LEVEL FILTER
    # =========================

    sheet.update(range_name="I3", values=[["Level"]])   # write level first (or after, both fine)

    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 3,   # Row 4
                        "endRowIndex": 4,
                        "startColumnIndex": 8,  # Column I
                        "endColumnIndex": 9
                    },
                    "rule": {
                        "condition": {
                            "type": "NUMBER_BETWEEN",
                            "values": [
                                {"userEnteredValue": "1"},
                                {"userEnteredValue": "99"}
                            ]
                        },
                        "strict": True,
                        "showCustomUi": True
                    }
                }
            }
        ]
    })

    sheet.update(
        range_name="I4",
        values=[[99]]
    )

    # ==============================
    # 🚀 SETUP RECIPE DIFFICULTY FILTER
    # ==============================

    sheet.update(range_name="J3", values=[["Recipe_Difficulty"]])   # write level first (or after, both fine)

    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 3,   # Row 4
                        "endRowIndex": 4,
                        "startColumnIndex": 9,  # Column J
                        "endColumnIndex": 10
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": "easy"},
                                {"userEnteredValue": "medium"},
                                {"userEnteredValue": "hard"}
                            ]
                        },
                        "strict": True,
                        "showCustomUi": True
                    }
                }
            }
        ]
    })

    sheet.update(
        range_name="J4",
        values=[["hard"]]
    )

    # ====================================
    # 🚀 SEPARATE FILTER AND MAIN TABLE
    # ====================================

    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 4,   # Row 5
                        "endRowIndex": 5,     # exclusive
                        "startColumnIndex": 1,  # Column B
                        "endColumnIndex": 10    # Column J
                    },
                    "mergeType": "MERGE_ALL"
                }
            }
        ]
    })


    # =========================
    # 🔹 CREATE TABLE HEADERS
    # =========================

    df["Best_XP_Recipe"] = ""  # placeholder column
    df["Appliance_xp"] = ""
    df["XP"] = ""
    df["XP/Hr"] = ""
    df["Best_Profit_Recipe"] = ""
    df["Appliance_$"] = ""
    df["Profit"] = ""
    df["Profit/Hr"] = ""

    sheet.update(
        range_name="B6",
        values=[df.columns.tolist()] + df.values.tolist()
    )

    # =========================
    # 🔹 UPDATE COLUMN WIDTHS
    # =========================

    column_widths = {
        "return_time (min)": 140,
        "Best_XP_Recipe": 150,
        "Appliance_xp": 150,
        "XP": 50,
        "XP/Hr": 50,
        "Best_Profit_Recipe": 150,
        "Appliance_$": 150,
        "Profit": 50,
        "Profit/Hr": 110
    }

    headers = df.columns.tolist()

    requests = []

    for i, col in enumerate(headers):
        width = column_widths.get(col, 120)  # default = 120px

        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": 1 + i,   # B column = index 1
                    "endIndex": 2 + i
                },
                "properties": {
                    "pixelSize": width
                },
                "fields": "pixelSize"
            }
        })

    sheet.spreadsheet.batch_update({
        "requests": requests
    })




    # =========================
    # 🔹 C Column: BEST RECIPE XP FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"""
    =INDEX(
    FILTER(
        master_table!$B:$B,
        master_table!$E:$E <= $B{row_num},
        master_table!$D:$D <= $I$4,
        master_table!$A:$A = $H$4,
        IF($J$4="easy", master_table!$H:$H=2,
        IF($J$4="medium", master_table!$H:$H<=3,
        IF($J$4="hard", master_table!$H:$H<=6)))
    ),
    MATCH(
        MAX(
        FILTER(
            master_table!$F:$F,
            master_table!$E:$E <= $B{row_num},
            master_table!$D:$D <= $I$4,
            master_table!$A:$A = $H$4,
            IF($J$4="easy", master_table!$H:$H=2,
            IF($J$4="medium", master_table!$H:$H<=3,
            IF($J$4="hard", master_table!$H:$H<=6)))
        )
        ),
        FILTER(
        master_table!$F:$F,
        master_table!$E:$E <= $B{row_num},
        master_table!$D:$D <= $I$4,
        master_table!$A:$A = $H$4,
        IF($J$4="easy", master_table!$H:$H=2,
        IF($J$4="medium", master_table!$H:$H<=3,
        IF($J$4="hard", master_table!$H:$H<=6)))
        ),
        0
    )
    )
    """.strip()

        formulas.append([formula])

    # Insert into column C (starting C7)
    sheet.update(
        range_name=f"C7:C{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )


    # =========================
    # 🔹 D Column: APPLIANCE_XP VLOOKUP FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=VLOOKUP($C{row_num},master_table!$B:$Y,2,0)"

        formulas.append([formula])

    # Insert into column D (starting D7)
    sheet.update(
        range_name=f"D7:D{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )



    # =========================
    # 🔹 E Column: XP VLOOKUP FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=VLOOKUP($C{row_num},master_table!$B:$Y,5,0)"

        formulas.append([formula])

    # Insert into column E (starting D7)
    sheet.update(
        range_name=f"E7:E{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )


    # =========================
    # 🔹 F Column: XP/Hr FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=ROUND((E{row_num}*60)/B{row_num}, 0)"

        formulas.append([formula])

    # Insert into column F (starting F7)
    sheet.update(
        range_name=f"F7:F{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )






    # =========================
    # 🔹 G Column: BEST PROFIT RECIPE FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"""
    =INDEX(
    FILTER(
        master_table!$B:$B,
        master_table!$E:$E <= $B{row_num},
        master_table!$D:$D <= $I$4,
        master_table!$A:$A = $H$4,
        IF($J$4="easy", master_table!$H:$H=2,
        IF($J$4="medium", master_table!$H:$H<=3,
        IF($J$4="hard", master_table!$H:$H<=6)))
    ),
    MATCH(
        MAX(
        FILTER(
            master_table!$G:$G,
            master_table!$E:$E <= $B{row_num},
            master_table!$D:$D <= $I$4,
            master_table!$A:$A = $H$4,
            IF($J$4="easy", master_table!$H:$H=2,
            IF($J$4="medium", master_table!$H:$H<=3,
            IF($J$4="hard", master_table!$H:$H<=6)))
        )
        ),
        FILTER(
        master_table!$G:$G,
        master_table!$E:$E <= $B{row_num},
        master_table!$D:$D <= $I$4,
        master_table!$A:$A = $H$4,
        IF($J$4="easy", master_table!$H:$H=2,
        IF($J$4="medium", master_table!$H:$H<=3,
        IF($J$4="hard", master_table!$H:$H<=6)))
        ),
        0
    )
    )
    """.strip()

        formulas.append([formula])

    # Insert into column G (starting G7)
    sheet.update(
        range_name=f"G7:G{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )




    # =========================
    # 🔹 H Column: APPLIANCE_$ VLOOKUP FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=VLOOKUP($G{row_num},master_table!$B:$Y,2,0)"

        formulas.append([formula])

    # Insert into column H (starting H7)
    sheet.update(
        range_name=f"H7:H{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )



    # =========================
    # 🔹 I Column: PROFIT VLOOKUP FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=VLOOKUP($G{row_num},master_table!$B:$Y,6,0)"

        formulas.append([formula])

    # Insert into column I (starting H7)
    sheet.update(
        range_name=f"I7:I{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )



    # =========================
    # 🔹 J Column: PROFIT/Hr FORMULA
    # =========================
    start_row = 7
    num_rows = len(df)

    formulas = []

    for i in range(num_rows):
        row_num = start_row + i

        formula = f"=ROUND((I{row_num}*60)/B{row_num}, 0)"

        formulas.append([formula])

    # Insert into column J (starting J7)
    sheet.update(
        range_name=f"J7:J{6+num_rows}",
        values=formulas,
        value_input_option="USER_ENTERED"
    )





    # =========================
    # 🔹 FORMATTING
    # =========================
    start_row = 5
    start_col = 1
    end_row = start_row + len(df) + 1
    end_col = start_col + len(df.columns)

    sheet.spreadsheet.batch_update({
        "requests": [

            # Header bold + center
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": start_row,
                        "endRowIndex": start_row + 1,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                            "horizontalAlignment": "CENTER"
                        }
                    },
                    "fields": "userEnteredFormat"
                }
            },

            # Borders
            {
                "updateBorders": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 2,
                        "endRowIndex": 21,
                        "startColumnIndex": 1,
                        "endColumnIndex": 10
                    },
                    "innerHorizontal": {"style": "SOLID"},
                    "innerVertical": {"style": "SOLID"},
                    "top": {"style": "SOLID_MEDIUM"},
                    "bottom": {"style": "SOLID_MEDIUM"},
                    "left": {"style": "SOLID_MEDIUM"},
                    "right": {"style": "SOLID_MEDIUM"}
                }
            }

        ]
    })





    # =========================
    # 🔹 COLOR FORMATTING ON FILTERS
    # =========================


    sheet.spreadsheet.batch_update({
        "requests": [
            # 🔹 H3 (Header Styling)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 2,   # H3
                        "endRowIndex": 3,
                        "startColumnIndex": 7,
                        "endColumnIndex": 10
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.75,
                                "green": 0.85,
                                "blue": 1
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },

            # 🔹 H4 (Value Styling)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 3,   # H4
                        "endRowIndex": 4,
                        "startColumnIndex": 7,
                        "endColumnIndex": 10
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.9,
                                "green": 0.95,
                                "blue": 1
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            }
        ]
    })



# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    push_result_gsheet(
        creds_path=os.getenv("GOOGLE_CREDENTIALS_PATH"),
        spreadsheet_name=os.getenv("GSHEET_NAME"),
        worksheet_name=os.getenv("GSHEET_WORKSHEET2"),
    )