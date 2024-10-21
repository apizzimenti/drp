
import pandas as pd
import geopandas as gpd
import json

# Import election and geometry data. Election and geometric data retrieved from
# Redistricting Data Hub.
elections = pd.read_csv("data/elections/sc/22G-raw.csv")
geometries = gpd.read_file("data/geometries/sc/22G-precincts.zip!22G-precincts")

# Set column names.
GEOID = "GEOID20"
COUNTY = "COUNTYFP20"

# Because this data has a super weird geometric identifier scheme, create a mapping
# from unique names to numbers. Why would anyone *ever* think this to be a good
# data practice???
identifiers = dict(zip(geometries["UNIQUE_ID"], [f"{t}".zfill(5) for t in range(len(geometries))]))
geometries[GEOID] = geometries["UNIQUE_ID"].map(identifiers)
elections[GEOID] = elections["UNIQUE_ID"].map(identifiers)

geometries = geometries.rename({ "COUNTYFP": COUNTY }, axis=1)
elections = elections.rename({ "COUNTYFP": COUNTY }, axis=1)

# Trim off all the unnecessary data from the precincts shapefile to make room
# for election data. Ensure that these identifier columns are formatted as
# zero-padded strings.
precincts = geometries[["geometry", GEOID, COUNTY]]
precincts[GEOID] = precincts[GEOID].astype(str)
precincts[COUNTY] = precincts[COUNTY].astype(str)

# We can throw away unnecessary columns (human-readable names for counties,
# precincts, etc.) and keep just the election data. Ensure that these identifier
# columns are formatted as zero-padded strings.
keep = list(set(list(elections)) - {"UNIQUE_ID", "Precinct", "County", "COUNTYFP", COUNTY, "Prec_Code"})
elections = elections[keep]

# Rename election columns and write the elections back to file.
with open("data/elections/sc/22G-codebook.json") as r: codebook = json.load(r)
elections = elections.rename(codebook, axis=1)
elections.to_csv("data/elections/sc/22G.csv", index=False)

# Keep only the statewide elections, since districted elections cannot be probative
# for the entire state.
keep = [e for e in list(elections) if all(n not in e for n in ["SLL"])]
elections = elections[keep]

# Merge election data.
precincts = gpd.GeoDataFrame(precincts.merge(elections, on=GEOID), geometry="geometry")
precincts.to_file("data/geometries/sc/22G-precincts-electoral/22G-precincts-electoral.shp")

# REMEMBER TO COMPRESS THE ABOVE FILE TO SAVE SPACE!!
