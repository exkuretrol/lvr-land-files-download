import requests
import os

# Define the headers
headers = {
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "host": "plvr.land.moi.gov.tw",
    # seems don't need cookie
    # "Cookie": "",
}

# Define the range of years and seasons
years = range(100, 114)  # From year 100 to 113
years = [113]
seasons = {year: [1, 2, 3, 4] for year in range(100, 113)}
seasons[113] = [1, 2]  # Year 113 has only 2 seasons

# Create the 'plvr' directory if it doesn't exist
if not os.path.exists("plvr"):
    os.makedirs("plvr")

# Loop through each year and season
for year in years:
    for season in seasons[year]:
        season_str = f"{year}S{season}"
        url = f"https://plvr.land.moi.gov.tw//DownloadSeason?season={season_str}&type=zip&fileName=lvr_landcsv.zip"

        # Make the request
        response = requests.get(url, headers=headers)

        # Save the content to a file in the 'plvr' directory
        file_path = os.path.join("plvr", f"{season_str}_lvr_landcsv.zip")
        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded {file_path}")
