import rasterio
import geopandas as gpd
from rasterstats import zonal_stats

raster_data = rasterio.open("C:/py_projects/NBRC2024_workshop/QuickTest_Data/classified_ortho_subset.tif")
polygon_data = gpd.read_file("C:/py_projects/NBRC2024_workshop/QuickTest_Data/encl_subset.shp")

# Set extent to match the extent of the polygon data
polygon_data = polygon_data.to_crs(raster_data.crs)
#raster_data = raster_data.read(1)

with rasterio.open("C:/py_projects/NBRC2024_workshop/QuickTest_Data/classified_ortho_subset.tif") as src:
    # Read the raster data and metadata
    data = src.read(1)
    metadata = src.meta.copy()

    # Set the nodata value to >blank<
    nodata_value = 0
    metadata.update(nodata=nodata_value)

# Define raster values for each attribute (50 cm resolution raster)
raster_values = {
    1: "Water",
    2: "Wetlands",
    3: "Tree_Canopy",
    5: "Meadow",
    6: "Barren",
    7: "Structures",
    8: "Imperv_Surf",
    9: "Imperv_Roads"
}


# Loop through polygons and assign attribute values
for i, polygon_feature in polygon_data.iterrows():
    stats = zonal_stats(
        polygon_feature.geometry,
        raster_data.read(1),
        affine=raster_data.transform,
        nodata=0,
        categorical=True,
        category_map=raster_values
    )

    # Access the zonal statistics result for the polygon
    polygon_stats = stats[0]

    # Loop through the raster_values dictionary and update the attributes
    for category, attribute in raster_values.items():
        # Check if the category is present in the polygon_stats dictionary
        if attribute in polygon_stats:
            value = polygon_stats[attribute]
            percent = (value * 0.25) / polygon_data.loc[i, "Shape_Area"] * 100 # percent = (value * 0.25) OR (value * 0.01)
            polygon_data.loc[i, attribute] = percent
        else:
            # If the category is not present, set the attribute value to 0
            polygon_data.loc[i, attribute] = 0

# Write the updated data to a new file
polygon_data.to_file("C:/py_projects/NBRC2024_workshop/QuickTest_Data/subset_lc.geojson") # "GeoJSON" ESRI Shapefile
