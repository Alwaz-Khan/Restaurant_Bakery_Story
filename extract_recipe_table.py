import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_text(parent, selector):
    tag = parent.select_one(selector)
    return tag.get_text(strip=True) if tag else None


def extract_recipes(base_url, output_path):

    print("\n🚀 STARTING RECIPE EXTRACTION PIPELINE\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    all_data = []
    page = 1
    total_scraped = 0

    while True:
        print(f"\n🔄 Scraping page {page}...")

        url = base_url.format(page)
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ Stopped at page {page} (status {response.status_code})")
            break

        soup = BeautifulSoup(response.text, "lxml")

        recipes = soup.select("span.appliance_single_recipe")

        if not recipes:
            print("✅ No more recipes found. Stopping.")
            break

        print(f"✅ Found {len(recipes)} recipes on page {page}")

        page_data = []

        for r in recipes:
            try:
                name = safe_text(r, "div.invtitle2")

                recipe_img = r.select_one("div.rcp_view img")
                recipe_img = recipe_img["src"] if recipe_img else None

                appl_img = r.select_one("span.appl_view img")
                appl_img = appl_img["src"] if appl_img else None

                block = r.select_one("div.hide-on-mobile")
                if not block:
                    continue

                stats = block.select_one("div.detstats")
                if not stats:
                    continue

                cost = safe_text(stats, "div.rcpcost")
                servings = safe_text(stats, "div.rcpserv")
                time_val = safe_text(stats, "div.rcptime")
                xp = safe_text(stats, "div.rcpxp")
                income = safe_text(stats, "div.rcpincome")

                appl_names = block.select("div.applname")
                appliance = appl_names[0].get_text(strip=True) if len(appl_names) > 0 else None
                release_date = appl_names[-1].get_text(strip=True) if len(appl_names) > 1 else None

                labels = [
                    l.get_text(strip=True)
                    for l in block.select("span.sd_label")
                    if l.get_text(strip=True)
                ]

                level = None
                for div in block.find_all("div"):
                    text = div.get_text(strip=True)
                    if "Lvl:" in text:
                        match = re.search(r"Lvl:\s*(\d+)", text)
                        if match:
                            level = int(match.group(1))
                            break

                link_tag = r.find("a", href=True)
                details_url = link_tag["href"] if link_tag else None

                page_data.append({
                    "game_mode": re.search(r"/s8/(\w+)_recipes", base_url).group(1),
                    "rcp_name": name,
                    "appl_name": appliance,
                    "rcp_cost": cost,
                    "rcp_servings": servings,
                    "rcp_time_hr": time_val,
                    "rcp_xp": xp,
                    "rcp_income": income,
                    "rcp_labels": ", ".join(labels),
                    "rcp_level": level,
                    "rcp_release_date": release_date,
                    "rcp_img_url": recipe_img,
                    "appl_img_url": appl_img,
                    "rcp_url": details_url
                })

            except Exception as e:
                print(f"⚠️ Error processing recipe on page {page}: {e}")

        all_data.extend(page_data)
        total_scraped += len(page_data)

        print(f"📦 Page {page} → {len(page_data)} records")
        print(f"📊 Total → {total_scraped}")

        page += 1
        time.sleep(1)

    print("\n🧱 Building DataFrame...")
    df = pd.DataFrame(all_data).drop_duplicates()

    print(f"🧹 Final rows → {len(df)}")

    df.to_csv(output_path, index=False)

    print("\n✅ EXTRACTION COMPLETE")
    print(f"📁 RAW saved → {output_path}")

    return df


# ================================
# TEST / RUN ENTRY POINT
# ================================
if __name__ == "__main__":

    RUN_MODE = "both"   # restaurant | bakery | both

    URLS = {
        "restaurant": "https://stm.gamerologizm.com/s8/restaurant_recipes_all.php?page={}",
        "bakery": "https://stm.gamerologizm.com/s8/bakery_recipes_all.php?page={}#content"
    }

    OUTPUTS = {
        "restaurant": "data_test/restaurant/01_recipes_all_raw.csv",
        "bakery": "data_test/bakery/01_recipes_all_raw.csv"
    }

    if RUN_MODE in ["restaurant", "both"]:
        extract_recipes(URLS["restaurant"], OUTPUTS["restaurant"])

    if RUN_MODE in ["bakery", "both"]:
        extract_recipes(URLS["bakery"], OUTPUTS["bakery"])