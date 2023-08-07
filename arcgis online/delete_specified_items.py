import pandas as pd
from arcgis.gis import GIS

def delete_items_by_id(gis, item_ids):
    for item_id in item_ids:
        try:
            item = gis.content.get(item_id)
            if item:
                item.delete()
                print(f"Item with ID '{item_id}' has been deleted.")
            else:
                print(f"Item with ID '{item_id}' does not exist.")
        except Exception as e:
            print(f"Failed to delete item with ID '{item_id}': {e}")

if __name__ == "__main__":
    # Load the Excel file data into a Pandas DataFrame
    data = pd.read_excel(r"P:\AGOL_HOSTED_SERVICES\Items Report\SCE_RP_GIS.xlsx")

    # Filter items with 'Proposed Action' set to 'Delete'
    items_to_delete = data[data['Proposed Action'] == 'Delete']
    print(f"{len(items_to_delete)} \n{items_to_delete['id'].tolist()}")

    # Call the delete_items_by_id function to delete the items from ArcGIS Online
    delete_items_by_id(GIS("Pro"), items_to_delete['id'].tolist())
