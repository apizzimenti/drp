
from gerrytools.geometry import dualgraph
import geopandas as gpd

geometries = gpd.read_file("data/geometries/sc/VTD20-electoral.shp.zip")
dualgraph(geometries).to_json("data/graphs/sc/SC-VTD20.json")
