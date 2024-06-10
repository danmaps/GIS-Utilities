import pandas as pd
from arcgis.gis import GIS

# Connect to ArcGIS Online
gis = GIS('Pro')  

# Function to extract user items
def get_item(user):

  # Get all items from root and folders
  items = get_all_items(user)
  
  # Convert to DataFrame
  df = items_to_df(items)

  # Format last viewed date 
  format_date(df)

  # Output to Excel
  df.to_excel(user.username + '.xlsx')
  
# Helper functions
def get_all_items(user):
  content_item = user.items()
  folders = user.folders
  list_items = {}
  for item in content_item:
    list_items[item.itemid] = item
  for folder in folders:
    folder_items = user.items(folder=folder['title'])
    for item in folder_items:
      list_items[item.itemid] = item
  return list_items

def items_to_df(items):
  return pd.DataFrame.from_dict(items, orient='index')

def format_date(df):
  df['lastViewed'] = pd.to_datetime(df['lastViewed'], unit='ms')
  df['lastViewed'] = df['lastViewed'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Get items for a user  
get_item(gis.users.search(gis.properties['user']['username'])[0])