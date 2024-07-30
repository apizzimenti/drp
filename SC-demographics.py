
from gerrytools.data import census20, geometries20
from us.states import SC

tot = census20(SC, table="P1", geometry="block")
vap = census20(SC, table="P3", geometry="block")
demographics = tot.merge(vap, on="GEOID20")
demographics.to_csv("data/demographics/sc/block20.csv", index=False)
# geometries = geometries20(SC, "data/geometries/sc/block20.zip", geometry="block")
