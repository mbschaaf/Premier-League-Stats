from bs4 import BeautifulSoup
import pandas as pd
import requests
from pprint import pprint
import os
from datetime import datetime
import logging

# Target directory where my files will be saved
one_drive_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Premier League Stats", "Team Statistics")
debug_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Premier League Stats", "Debug Log")

today = datetime.now().strftime("%Y%m%d")
now = datetime.now()

# Set up logging
log_filename = os.path.join(debug_path, f"script_log_{datetime.now().strftime("%Y%m%d")}.txt")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info(f"{now} Script started.")

os.chdir(one_drive_path)

# Range of years for report data
current_years = list(range(2018, 2024))

# previous_years = 2023
# current_years = 2024

all_data = []

# Iterate over current_years range to return 10 years of data for team stats
for year in current_years:
    try:
        url = f"https://www.fbref.com/en/comps/9/{year - 1}-{year}/stats/{year - 1}-{year}-Premier-League-Stats"

        # Return html from website
        response = requests.get(url)
        response.raise_for_status() # Raise an error

        # Parse through the HTML
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            logging.warning(f"{now} No table found for {year - 1} / {year}. Skipping.")
            continue

        # Extract the header from the table
        rows = table.find_all("tr")
        header = [th.get_text(strip=True) for th in rows[1].find_all("th")]

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            cell_values = [cell.get_text(strip=True) for cell in cells]

            # Skip any cell that is a duplicate of the header
            if cell_values == header:
                continue
            cell_values.append(f"{year - 1} / {year}")
            all_data.append(cell_values)

    except Exception as e:
        logging.error(f"{now} Error processing {year - 1} / {year} season: {e}")

# Save all data to an excel sheet
try:
    if all_data:
        # Add "Season" to the header
        header.append("Season")
        df = pd.DataFrame(all_data, columns=header)
        file_name = "Premier League Stats Last 5 Years.xlsx"
        df.to_excel(file_name, index=False)
        logging.info(f"{now} Data saved successfully to {file_name}")
    else:
        logging.warning(f"{now} No data was collected")
except Exception as e:
    logging.error(f"{now} Error during file export: {e}")

logging.info(f"{now} Script finished.")