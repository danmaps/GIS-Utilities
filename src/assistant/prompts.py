python_PROMPT = """
I have a map in ArcGIS Pro. I've gathered information about this map and will give it to you in JSON format containing information about the map, including the map name, title, description, spatial reference, layers, and properties.

Based on this information, Write Python code that performs the following tasks in ArcGIS Pro:

Selects features from a specified layer based on a given attribute query.
Zooms the map extent to the selected features.
Assume the following inputs:

- user prompt: "show me top 5 points by ID in MyLayer"

You will need to write a SQL query to select features based on an attribute. Remember that, for example, the ORDER BY clause is not supported in attribute queries for selection operations.
In ArcGIS Pro, SQL expressions have specific limitations and capabilities that vary depending on the underlying data source (e.g., file geodatabases, enterprise geodatabases). Notably, the ORDER BY clause is not supported in selection queries, and aggregate functions like SUM and COUNT have limited use outside definition queries. Subqueries and certain string functions may also face restrictions. Additionally, field names and values must match exactly in terms of case sensitivity. To handle these limitations, a combination of SQL expressions and ArcPy functions, such as using search cursors with sql_clause for sorting, can be employed to achieve desired results. Understanding these constraints is crucial for effective data querying and manipulation in ArcGIS Pro.

When using `arcpy.management.SelectLayerByAttribute(in_layer_or_view, {selection_type}, {where_clause}, {invert_where_clause})`, with the `selection_type` parameter should be set to `NEW_SELECTION`, the resulting selection will replace the current selection, so make sure your query contains all the information needed. For example, when trying to select the most populous counties in California, use a query like `"NAME in most_CA_populous_counties AND STATE_NAME = 'California'"`.

This will fail:
```python
# Get the current project and the active view
aprx = arcpy.mp.ArcGISProject("CURRENT")
active_map = aprx.activeMap
active_view = aprx.activeView

# Zoom to the extent of the selected features
active_view.camera.setExtent(active_view.getLayerExtent(counties_fc))
```

instead use:
```python
# Zoom to the selected counties
aprx = arcpy.mp.ArcGISProject("CURRENT")
active_map = aprx.activeMap
active_view = aprx.activeView
layer = active_map.listLayers(counties_fc)[0]
active_view.camera.setExtent(active_view.getLayerExtent(layer))
arcpy.AddMessage("Zoomed to selected counties")
```


The code should:

- Use the arcpy module.
- Select the features using arcpy.SelectLayerByAttribute_management.
- Zoom the map to the selected features using the arcpy.mapping module.
- Use arcpy.AddMessage to add messages to communicate with the user.

If the user asks about features with in a distance of another, use arcpy.SelectLayerByLocation_management in addition to arcpy.SelectLayerByAttribute_management.

Please provide the only the complete Python code with these requirements. Do not include any other text or comments.
"""

example_PROMPT = """
show me the largest polygon in states
"""

example_PYTHON = """
import arcpy

# User prompt: "show me the largest polygon in states"

# Inputs
layer_name = "states"
attribute_query = "shape_area = (SELECT MAX(shape_area) FROM states)"

# Get the current project and the active view
aprx = arcpy.mp.ArcGISProject("CURRENT")
active_map = aprx.activeMap
active_view = aprx.activeView

# Get the layer
layer = active_map.listLayers(layer_name)[0]

# Select features based on the attribute query
arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", attribute_query)

# Zoom to the extent of the selected features
active_view.camera.setExtent(active_view.getLayerExtent(layer))
"""

example_PROMPT2 = """
ca counties with the lowest population density
"""

example_PYTHON2 = """
import arcpy

# User prompt: "CA counties with the highest population"

# Define the name of the counties layer
counties_fc = "counties"

# Select counties in Nevada
query = "STATE_ABBR = 'NV'"
arcpy.management.SelectLayerByAttribute(counties_fc, "NEW_SELECTION", query)

# Create a list to store county names and population densities
county_density_list = []

# Use a search cursor to get the names and population densities of the counties
with arcpy.da.SearchCursor(counties_fc, ["NAME", "POPULATION", "SQMI"]) as cursor:
    for row in cursor:
        population_density = row[1] / row[2] if row[2] > 0 else 0  # Avoid division by zero
        county_density_list.append((row[0], population_density))

# Sort the list by population density in ascending order and get the top 3
lowest_density_counties = sorted(county_density_list, key=lambda x: x[1])[:3]
arcpy.AddMessage(f"Top 3 counties with the lowest population density: {lowest_density_counties}")

# Create a query to select the lowest density counties
lowest_density_names = [county[0] for county in lowest_density_counties]
print(lowest_density_names)
lowest_density_query = "NAME IN ({})".format(", ".join(["'{}'".format(name) for name in lowest_density_names]))

# Select the lowest density counties
arcpy.management.SelectLayerByAttribute(counties_fc, "NEW_SELECTION", lowest_density_query + " AND " + query)
# Zoom to the selected counties
aprx = arcpy.mp.ArcGISProject("CURRENT")
active_map = aprx.activeMap
active_view = aprx.activeView
layer = active_map.listLayers(counties_fc)[0]
active_view.camera.setExtent(active_view.getLayerExtent(layer))
arcpy.AddMessage("Zoomed to selected counties")
"""