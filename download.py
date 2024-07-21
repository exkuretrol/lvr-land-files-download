import requests
import os
import zipfile
import pathlib
from time import sleep

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


def get_proper_file_name(file_name: str):
    # filename example: E_lvr_land_A, E_lvr_land_A_park, E_lvr_land_A_land, E_lvr_land_A_build
    # extra first character, and last A, B or C using re
    import re

    code_county_dict = {
        "a": "台北市",
        "b": "台中市",
        "c": "基隆市",
        "d": "台南市",
        "e": "高雄市",
        "f": "台北縣",
        "g": "宜蘭縣",
        "h": "桃園縣",
        "i": "嘉義市",
        "j": "新竹縣",
        "k": "苗栗縣",
        "l": "台中縣",
        "m": "南投縣",
        "n": "彰化縣",
        "o": "新竹市",
        "p": "雲林縣",
        "q": "嘉義縣",
        "r": "台南縣",
        "s": "高雄縣",
        "t": "屏東縣",
        "u": "花蓮縣",
        "v": "台東縣",
        "w": "金門縣",
        "x": "澎湖縣",
        "y": "陽明山",
        "z": "連江縣",
    }

    pattern = re.compile(
        r"(?P<county>[a-z])_lvr_land_(?P<type>[abc])(?P<object>_park|_build|_land|)?"
    )
    match_groups = re.match(pattern, file_name)
    if not match_groups:
        raise ValueError(f"Invalid file name: {file_name}")

    county = code_county_dict.get(match_groups.group("county"))
    if not county:
        raise ValueError(f"Invalid county code: {match_groups.group('county')}")

    type_dict = {
        "a": "買賣",
        "b": "預售屋",
        "c": "租賃",
    }
    typo = type_dict.get(str(match_groups.group("type")))
    if not typo:
        raise ValueError(f"Invalid type code: {typo}")
    object_dict = {"_park": "停車位", "_build": "建物", "_land": "土地", "": "主檔"}
    obj = object_dict.get(str(match_groups.group("object")))
    if not obj:
        raise ValueError(f"Invalid object code: {obj}")

    return (
        county,
        typo,
        obj,
    )


# Define the range of years and seasons
years = range(101, 114)  # From year 101 to 113
seasons = {year: [1, 2, 3, 4] for year in range(100, 113)}
seasons[113] = [1, 2]  # Year 113 has only 2 seasons

BASE_DIR = pathlib.Path(__file__).parent.resolve()
UNZIP_DIR = BASE_DIR / "lvr_lands"
ZIP_DIR = BASE_DIR / "lvr_lands_zip"

# Create the 'lvr_lands' directory if it doesn't exist
if not UNZIP_DIR.exists():
    UNZIP_DIR.mkdir()

# Create the 'lvr_lands' directory if it doesn't exist
if not ZIP_DIR.exists():
    ZIP_DIR.mkdir()

# Loop through each year and season
for year in years:
    for season in seasons[year]:
        season_str = f"{year}S{season}"
        url = f"https://plvr.land.moi.gov.tw//DownloadSeason?season={season_str}&type=zip&fileName=lvr_landcsv.zip"

        # Make the request
        # you can get without headers
        response = requests.get(url, headers=headers)

        # Save the content to a file in the 'plvr' directory
        file_path = ZIP_DIR / f"{season_str}_lvr_landcsv.zip"
        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded {file_path.name}")

        # Unarchive the zip file
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            # Extract all files to the 'lvr_lands' directory
            zip_ref.extractall(ZIP_DIR)

        sleep(2.5)

        # Move the extracted files to the year directory
        extracted_files = ZIP_DIR.rglob("*.csv")
        for extracted_file in extracted_files:
            file_name = extracted_file.name
            try:
                county, typo, obj = get_proper_file_name(file_name.removesuffix(".csv"))
            except ValueError as e:
                if "Invalid file name" in str(e):
                    print(f"Skipping schema or manifest file: {file_name}")
                    continue
            NEW_FILE_DIR = UNZIP_DIR / county
            if not NEW_FILE_DIR.exists():
                NEW_FILE_DIR.mkdir(parents=True)
            new_file = NEW_FILE_DIR / f"{year}_{season}_{typo}_{obj}.csv"
            print(
                f"Moving {extracted_file.relative_to(BASE_DIR)} to {new_file.relative_to(BASE_DIR)}"
            )
            os.rename(extracted_file, new_file)
