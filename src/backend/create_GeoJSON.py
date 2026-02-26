import geopandas as gpd

SHAPE_FILES = {
    "county": "../data/shape-files/USA_Counties/USA_Counties.shp",
    "ecoregion": "../data/shape-files/Level_IV_Ecoregions/US_Ecoregions_Level_IV.shp",
    "national-forest": "../data/shape-files/NFS_Forest_Boundaries/Forest_Service_National_Forest_Boundaries.shp"
}

FRONTEND_PATHS = {
    "county": "../frontend/public/GeoJSON/county.json",
    "ecoregion": "../frontend/public/GeoJSON/l4_ecoregion.json",
    "national-forest": "../frontend/public/GeoJSON/national-forest.json"
}

REGIONTYPE_LIST = ["county", "ecoregion", "national-forest"]

def create_l3_ecoregion(gdf):
    output_path = "../frontend/public/GeoJSON/ecoregion.json"
    
    # Columns to remove: L4 specific identifiers and shape stats
    cols_to_drop = ['US_L4CODE', 'US_L4NAME', 'L4_KEY', 'Shape_Leng', 'Shape_Area']
    
    # Drop columns if they exist
    gdf_l3 = gdf.drop(columns=[c for c in cols_to_drop if c in gdf.columns])
    
    # Dissolve by US_L3CODE
    gdf_dissolved = gdf_l3.dissolve(by='US_L3CODE', as_index=False)
    
    gdf_dissolved.to_file(output_path, driver='GeoJSON')

def createGeoJson ():

    for region_type in REGIONTYPE_LIST:
        shape_file_path = SHAPE_FILES[region_type]
        public_frontend_path = FRONTEND_PATHS[region_type]

        # Load your shapefile
        gdf = gpd.read_file(shape_file_path)

        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)

        if region_type in ["county", "ecoregion"]:
            gdf = gdf[gdf["STATE_NAME"] == "Oregon"]
        elif region_type == "national-forest":
            gdf = gdf[gdf["REGION"] == "06"]

        # # Keep only the features that intersect with Oregon
        # oregon_gdf = gpd.sjoin(gdf, oregon_boundary, how="inner", predicate="intersects")

        # Export to your project's public directory
        gdf.to_file(public_frontend_path, driver='GeoJSON')

        if region_type == "ecoregion":
            create_l3_ecoregion(gdf)


if __name__ == "__main__":
    createGeoJson()
    # use https://mapshaper.org/ to simplify for efficiency (15%)
