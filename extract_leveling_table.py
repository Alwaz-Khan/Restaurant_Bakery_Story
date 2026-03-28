import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_leveling_data(save_path=None):
    API_URL = "https://restaurantstory.fandom.com/api.php"

    params = {
        "action": "parse",
        "page": "Leveling",
        "format": "json"
    }

    # Fetch HTML
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    html = response.json()["parse"]["text"]["*"]

    # Parse HTML
    soup = BeautifulSoup(html, "lxml")

    # Find correct table
    tables = soup.find_all("table", {"class": "wikitable"})
    target_table = None

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if all(col in headers for col in ["level", "xp", "slots", "expansion"]):
            target_table = table
            break

    if not target_table:
        raise Exception("Target table not found")

    # Extract data
    rows = target_table.find_all("tr")

    headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
    data = []

    for row in rows[1:]:
        cols = row.find_all("td")
        cols = [col.get_text(strip=True) for col in cols]

        if len(cols) == len(headers):
            data.append(cols)

    df = pd.DataFrame(data, columns=headers)

    # Optional save
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"✅ Saved to {save_path}")

    return df


# ================================
# RUN
# ================================
if __name__ == "__main__":
    get_leveling_data("data/leveling.csv")