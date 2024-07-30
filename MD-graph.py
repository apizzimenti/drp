
from gerrytools.data import vtds20
from gerrytools.geometry import dualgraph
from us.states import MD
import geopandas as gpd

vtds20(MD, "MD_vtd20.zip")
geometries = gpd.read_file("zip://./MD_vtd20.zip!MD_vtd20.shp")
dualgraph(geometries).to_json("MD_vtd20.json")
