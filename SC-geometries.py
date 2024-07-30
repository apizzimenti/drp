
from gerrytools.geometry import unitmap
import geopandas as gpd
import pandas as pd

# Set the column name on which merges take place.
MERGE = "GEOID20"
COUNTY = "COUNTYFP20"
AGGREGATOR = "PRECINCT"

# Get demographic data, do some joins, etc. etc.
demographics = pd.read_csv("data/demographics/sc/block20-pared.csv")
demographics[MERGE] = demographics[MERGE].astype(str)

blocks = gpd.read_file("data/geometries/sc/block20.zip!block20")
blocks[MERGE] = blocks[MERGE].astype(str)
blocks = blocks[["geometry", MERGE, COUNTY]].merge(demographics, on=MERGE)

# Create the unit map and aggregate.
precincts = gpd.read_file("data/geometries/sc/22G-precincts-electoral.zip!22G-precincts-electoral")
precincts[MERGE] = precincts[MERGE].astype(str)

blocksToPrecincts = unitmap((blocks, MERGE), (precincts, MERGE))
blocks[AGGREGATOR] = blocks[MERGE].map(blocksToPrecincts)
blocks.to_file("data/geometries/sc/block20-assigned.shp.zip")

grouped = blocks.groupby(by=AGGREGATOR).sum()
grouped = grouped.reset_index()
grouped[AGGREGATOR] = grouped[AGGREGATOR].astype(int).astype(str).str.zfill(5)
grouped = grouped.rename({ AGGREGATOR: MERGE }, axis=1)

# Join the aggregated data to the geometries, save the data as a .csv for easier
# spot-checking, and leave.
precincts = gpd.GeoDataFrame(precincts.merge(grouped, on=MERGE), geometry="geometry")
precincts.to_file("data/geometries/sc/22G-precincts-electoral-demographic")
data = precincts.drop("geometry", axis=1)
data.to_csv("data/demographics/sc/precinct20-aggregated.csv", index=False)
