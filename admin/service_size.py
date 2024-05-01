import arcgis
from IPython.display import display

def show_size(service_item):
    # Convert bytes to a human-readable format (optional)
    size_bytes = service_item.size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    size_gb = size_mb / 1024

    print(f"Service '{service_item.title}' size: {size_bytes} bytes")
    print(f"{size_kb:.2f} KB, {size_mb:.2f} MB, {size_gb:.2f} GB")
    print(service_item.content_status)
    display(service_item)

# Establish connection to AGOL
gis = arcgis.gis.GIS("pro")

title = "cGIS Transmission Lines GG Concat" # part or complete title
itemid = "859d1e7b97bc4ddeb3e3556063fe63e4"

# Get the service item
service_item = gis.content.get(itemid)
search_results = gis.content.search(query=f"title:{title}*",item_type="Feature Layer")

if len(search_results)>1:
    service_item = search_results[0]
    for service_item in search_results:
        show_size(service_item)
elif len(search_results)==0:
    print(f"no results found for title:{title}*... getting size using {itemid} instead.")
    show_size(service_item)
else: # 1 result
    show_size(search_results[0])




