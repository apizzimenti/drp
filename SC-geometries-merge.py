
from gerrytools.geometry import unitmap
from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
import maup

# Set the column name on which merges take place.
MERGECOLUMN = "GEOID20"
COUNTY = "COUNTYFP20"
DISAGGREGATOR = "PRECINCT"
AGGREGATOR = "VTD20"
CRS = "EPSG:6569"
TOTPOP = "TOTPOP20"
VAP = "VAP20"
WEIGHT = "WEIGHT"

# Load demographic data on 2020 Census blocks.
demographics = pd.read_csv("data/demographics/sc/block20-pared.csv")
demographics[MERGECOLUMN] = demographics[MERGECOLUMN].astype(int).astype(str)

# Load VTDs; drop unnecessary columns; change CRS.
vtds = gpd.read_file("data/geometries/sc/VTD20.zip!VTD20")
vtds[MERGECOLUMN] = vtds[MERGECOLUMN].astype(int).astype(str)
vtds = vtds[["geometry", MERGECOLUMN, COUNTY]]
vtds = vtds.to_crs(CRS)

# Load precincts; drop unnecessary columns; change CRS.
precincts = gpd.read_file("data/geometries/sc/22G-precincts-repaired.shp.zip")
precincts[MERGECOLUMN] = precincts[MERGECOLUMN].astype(int).astype(str).str.zfill(5)
precincts = precincts.to_crs(CRS)

# Create mappings from election names to { <precinct identifier>: <vote total> }
# mappings.
ELECTIONS = list(set(list(precincts)) - {MERGECOLUMN, COUNTY, TOTPOP, VAP, "geometry"})
ELECTIONMAPS = {
    ELECTION: dict(zip(precincts[MERGECOLUMN], precincts[ELECTION]))
    for ELECTION in ELECTIONS
}

# If the file of assigned blocks does *not* exist, create it; otherwise, use the
# existing one.
if not Path("data/geometries/sc/block20-assigned.shp.zip").exists():
    # Load blocks; drop unnecessary columns; merge with demographic data; change CRS.
    blocks = gpd.read_file("data/geometries/sc/block20.zip!block20")
    blocks[MERGECOLUMN] = blocks[MERGECOLUMN].astype(int).astype(str)
    blocks = blocks[["geometry", MERGECOLUMN, COUNTY]].merge(demographics, on=MERGECOLUMN)
    blocks = blocks.to_crs(CRS)

    # Map blocks to precincts; we have to create "special" mappings here to ensure
    # that we capture all the population. Individual entries were done by hand.
    blocksToPrecincts = unitmap((blocks, MERGECOLUMN), (precincts, MERGECOLUMN))
    blocksToPrecincts["450439205101027"] = "01231"
    blocks[DISAGGREGATOR] = blocks[MERGECOLUMN].map(blocksToPrecincts)

    # Drop unnecessary columns and do some basic sanity-checking.
    dropped = blocks[blocks[MERGECOLUMN].notna()]

    assert dropped[TOTPOP].sum() == blocks[TOTPOP].sum()
    assert dropped[VAP].sum() == blocks[VAP].sum()

    # Write to file.
    blocks = blocks[blocks[MERGECOLUMN].notna()]
    blocks.to_file("data/geometries/sc/block20-assigned.shp.zip")
else:
    blocks = gpd.read_file("data/geometries/sc/block20-assigned.shp.zip")

# Group blocks by their precincts, and sum. Always, always always enforce the
# columns-as-strings standard, otherwise things can get frustrating.
blocks[DISAGGREGATOR] = blocks[DISAGGREGATOR].astype(str).str.zfill(5)
grouped = blocks[[TOTPOP, DISAGGREGATOR]].groupby(by=DISAGGREGATOR).sum()
grouped = grouped.reset_index()
grouped[DISAGGREGATOR] = grouped[DISAGGREGATOR].astype(str).str.zfill(5)

# Create a mapping from precinct identifiers to their 2020 Census total population.
# Because the precincts only have election data and not population data, we
# disaggregate the election data from precincts down to blocks: we first assign
# blocks to precincts, and then award each block a vote total according to the
# fraction of people living in the block relative to the block's precinct. For
# example, if block A has 10% of the population of precinct B, A is awarded 10% of
# the votes cast (in every election) in precinct B.
popmap = dict(zip(grouped[DISAGGREGATOR], grouped[TOTPOP]))
blocks[WEIGHT] = blocks[TOTPOP]/blocks[DISAGGREGATOR].map(popmap)

for ELECTION, ELECTIONMAP in ELECTIONMAPS.items():
    blocks[ELECTION] = blocks[WEIGHT]*blocks[DISAGGREGATOR].map(ELECTIONMAP)

# More basic sanity-checking: the election totals on the blocks should match the
# election totals on the precincts.
for ELECTION in ELECTIONS:
    try:
        assert np.isclose(blocks[ELECTION].sum(), precincts[ELECTION].sum())
    except:
        print(ELECTION)
        print(blocks[ELECTION].sum(), precincts[ELECTION].sum())
        print()


# Assign blocks to VTDs.
blocksToVTDs = unitmap((blocks, MERGECOLUMN), (vtds, MERGECOLUMN))
blocks[AGGREGATOR] = blocks[MERGECOLUMN].map(blocksToVTDs)
blocks = blocks.drop([MERGECOLUMN, COUNTY, DISAGGREGATOR, "BLOCKGROUP", "geometry"], axis=1)

# Again, group according to VTD assignment, sum, and merge.
grouped = blocks.groupby(by=AGGREGATOR).sum()
grouped = grouped.reset_index()
grouped[AGGREGATOR] = grouped[AGGREGATOR].astype(int).astype(str)
grouped = grouped.rename({ AGGREGATOR: MERGECOLUMN }, axis=1)

COLUMNS = set(grouped) - {"geometry", MERGECOLUMN }
vtds = vtds.merge(grouped, on=MERGECOLUMN)

# More basic sanity-checking: the VTD totals should match the block totals (which
# we know to match the precinct totals).
for COLUMN in COLUMNS:
    try:
        assert np.isclose(blocks[COLUMN].sum(), vtds[COLUMN].sum())
    except:
        print(COLUMN)
        print(blocks[COLUMN].sum(), vtds[COLUMN].sum())
        print()

# Write to file.
vtds.to_file("data/geometries/sc/VTD20-electoral.shp.zip")
