
import geopandas as gpd
import maup


# Repairs SC precincts, because whoever uploaded this shapefile didn't check
# FOR GAPS OR HOLES??? ?WTF ARE YOU DOING
garbage = gpd.read_file("data/geometries/sc/22G-precincts-electoral.zip!22G-precincts-electoral")
repairedGarbage = maup.smart_repair(garbage)
maup.doctor(repairedGarbage)
repairedGarbage.to_file("data/geometries/sc/22G-precincts-repaired.shp.zip")
