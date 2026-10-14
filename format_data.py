"""Build app/<region>.json (income by tract) and app/<region>-zipcodes.json (GeoJSON) for each region.

Needs a Census API key in CENSUS_API_KEY (`make data` reads it from .env).
"""

import json
import os
import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

YEAR = 2024
ACS = f"https://api.census.gov/data/{YEAR}/acs/acs5/subject"
TRACTS = "https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state}_tract.zip"
# ZCTAs only change with the decennial census
ZCTAS = "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip"

# Region name -> state FIPS and county FIPS ("*" for the whole state). The page lists these too.
REGIONS = {
    "massachusetts": {"state": "25", "counties": "*"},
    "los-angeles": {"state": "06", "counties": "037,059"},  # Los Angeles and Orange counties
}

# ~5 m in degrees; keeps the files small enough to load in a browser
SIMPLIFY = 0.00005


def get_json(url):
    with urllib.request.urlopen(url) as resp:
        if "json" not in resp.headers.get("Content-Type", ""):
            raise RuntimeError(f"Non-JSON response from {resp.url} (CENSUS_API_KEY valid?)")
        return json.load(resp)


def column_name(label):
    """'Estimate!!Households!!Total!!$10,000 to $14,999' -> '10,000_to_14,999-households'.

    Returns None for columns the map doesn't use.
    """
    parts = label.split("!!")
    if parts[0] != "Estimate" or "PERCENT ALLOCATED" in parts:
        return None
    value = parts[-1].strip().lower().replace(" ", "_").replace("$", "")
    income_type = parts[1].lower().replace("-", "_").replace(" ", "_")
    return f"{value}-{income_type}"


def clean(value):
    # The API marks missing or unreliable estimates with large negative sentinels
    value = float(value)
    return np.nan if value < 0 else value


def income_table(key, state, counties):
    labels = get_json(f"{ACS}/groups/S1901.json")["variables"]
    # Sorted by variable ID so columns come out in table order (households first, brackets ascending)
    names = {var: column_name(v["label"]) for var, v in sorted(labels.items()) if var.endswith("E")}
    names = {var: name for var, name in names.items() if name}

    rows = get_json(f"{ACS}?get=group(S1901)&for=tract:*&in=state:{state}&in=county:{counties}&key={key}")
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df[["GEO_ID", *names]].rename(columns={"GEO_ID": "GEOIDFQ", **names})
    for name in names.values():
        df[name] = df[name].map(clean)
    return df


def download(url):
    path = Path("data") / url.rsplit("/", 1)[-1]
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def write(gdf, path):
    gdf = gdf.to_crs(4326)
    gdf["geometry"] = gdf.simplify(SIMPLIFY)
    gdf.to_file(path, driver="GeoJSON", COORDINATE_PRECISION=5)


def main():
    key = os.environ["CENSUS_API_KEY"]
    zctas = gpd.read_file(download(ZCTAS))[["geometry", "ZCTA5CE20"]].rename(columns={"ZCTA5CE20": "POSTCODE"})

    for region, r in REGIONS.items():
        print(region)
        tracts = gpd.read_file(TRACTS.format(year=YEAR, state=r["state"]))
        tracts = tracts[["geometry", "GEOIDFQ"]].merge(
            income_table(key, r["state"], r["counties"]), on="GEOIDFQ", how="inner"
        )
        write(tracts, f"app/{region}.json")

        zips = gpd.sjoin(zctas.to_crs(tracts.crs), tracts[["geometry"]], predicate="intersects")
        write(zips[~zips.index.duplicated()][["geometry", "POSTCODE"]], f"app/{region}-zipcodes.json")


if __name__ == "__main__":
    main()
