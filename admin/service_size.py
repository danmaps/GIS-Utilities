import arcgis

# Establish connection to AGOL
gis = arcgis.gis.GIS("pro")

query = "title:AOC*"
itemid = "59636e7f1c6f48099d43af47cab757e7"

# Get the service item
service_item = gis.content.get(itemid)
search_results = gis.content.search(query=query,item_type="Feature Layer")

if len(search_results) >0:
    service_item = search_result[0]
else:
    print(f"no results found for {query}! getting size of {itemid} instead.")

# Check if it's a feature service
if service_item.type != "Feature Service":
    print(f"Service '{service_item.title}' is not a feature service. Size information unavailable.")
else:

    # Convert bytes to a human-readable format (optional)
    size_bytes = service_item.size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    size_gb = size_mb / 1024

    print(f"Service '{service_item.title}' size: {size_bytes} bytes")
#     print(f"ItemID '{service_item.id}'")
    print(f"{size_kb:.2f} KB, {size_mb:.2f} MB, {size_gb:.2f} GB")

