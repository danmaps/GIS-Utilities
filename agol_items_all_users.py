import pandas as pd
import arcgis
from arcgis.gis import GIS

# Connect to AGOL
gis = GIS()

# Empty dataframe 
full_df = pd.DataFrame()

# Function to extract user items
def get_items(user):

  # Dictionary to store items
  items = {}

  # Get root items
  for item in user.items():
    items[item.itemid] = item

  # Get items in folders
  for folder in user.folders:
    for item in user.items(folder=folder['title']):
      items[item.itemid] = item

  # Create dataframe
  df = pd.DataFrame.from_dict(items, orient='index')

  # Format dates
  df['lastViewed'] = pd.to_datetime(df['lastViewed'], unit='ms')
  df['lastViewed'] = df['lastViewed'].dt.strftime('%Y-%m-%d %H:%M:%S')

  # Append to full df
  global full_df
  full_df = full_df.append(df)

# Loop through users  
for user in gis.users.search():
  print(f"Extracting {user.username}")
  get_items(user)

# Sort by last viewed
full_df = full_df.sort_values('lastViewed', ascending=False)

# Export to Excel
full_df.to_excel('all_users.xlsx', index=False)

print("Done!")