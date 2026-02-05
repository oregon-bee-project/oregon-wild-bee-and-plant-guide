import geopandas as gpd

index = 2

shape_files = ["../data/shape-files/USA_Counties/USA_Counties.shp",
               "../data/shape-files/Level_IV_Ecoregions/US_Ecoregions_Level_IV.shp",
               "../data/shape-files/National_Wildlife_Refuge_Boundaries/National_Wildlife_Refuge_Boundaries.shp",
               "../data/shape-files/NFS_Forest_Boundaries/Forest_Service_National_Forest_Boundaries.shp",
               "../data/shape-files/State_Park_Boundaries/Oregon_State_Parks.shp"]

frontend_paths = ["../frontend/public/GeoJSON/counties.json",
                 "../frontend/public/GeoJSON/ecoregions.json",
                 "../frontend/public/GeoJSON/refuges.json",
                 "../frontend/public/GeoJSON/forests.json",
                 "../frontend/public/GeoJSON/parks.json"]

shape_file_path = shape_files[index]
public_frontend_path = frontend_paths[index]

# Load your already-filtered Oregon counties
oregon_boundary = gpd.read_file("../frontend/public/GeoJSON/counties.json")

# Load your shapefile
gdf = gpd.read_file(shape_file_path)

if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

# Filter for Oregon only 
# Note: 'STATEFP' is standard for Census data; check your column names with gdf.columns
# oregon_gdf = gdf[gdf['STATE_NAME'] == 'Oregon'].copy()
# Keep only the features that intersect with Oregon
oregon_gdf = gpd.sjoin(gdf, oregon_boundary, how="inner", predicate="intersects")

# Crucial: Ensure the projection is WGS84 (Lng/Lat) for MapLibre
# if oregon_gdf.crs != "EPSG:4326":
#     oregon_gdf = oregon_gdf.to_crs(epsg=4326)

# Export to your project's public directory
oregon_gdf.to_file(public_frontend_path, driver='GeoJSON')