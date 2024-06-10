'''
scans an organization for Web Maps and Web Mapping Applications for an input service or services
'''

from arcgis.gis import GIS
from arcgis.mapping import WebMap
import arcpy

gis = GIS('pro')


def web_map_search(services):
    # arcpy.AddMessage(f"Searching for {services}")
    matching_web_maps = []
    web_maps = gis.content.search(query=f"", item_type="Web Map", max_items=10000)
    for web_map in web_maps:
        # arcpy.AddMessage(WebMap(web_map).layers[0].url)
        layers = WebMap(web_map).layers
        for layer in layers:
            # arcpy.AddMessage(f"{web_map.title},{layer.url}")
            # loops through all input services
            for service in services:
                # arcpy.AddMessage(f"searching for {service.lower()}")
                try:
                    if layer['layerType'] == "VectorTileLayer":
                        if service.lower() in layer.styleUrl.lower():
                            arcpy.AddMessage(f"{web_map.title}, {web_map.owner}, {web_map.homepage}, {layer.styleUrl}")
                    elif service.lower() in layer.url.lower():
                        matching_web_maps.append(web_map)
                        if len(services)<2: # if only one service, output map properties
                            arcpy.AddMessage(f"{web_map.title}, {web_map.owner}, {web_map.homepage}")
                        else: # also output service
                            arcpy.AddMessage(f"{web_map.title}, {web_map.homepage}, {web_map.homepage}, {service}")
                except:
                    continue
    return matching_web_maps


def map_apps(web_maps):
    # Search for web apps that are related to the web maps
    web_apps = gis.content.search(query = '', item_type='Web Mapping Application', max_items=10000)
    for app in web_apps:
        data = app.get_data()
        if 'map' in data and data['map']['itemId'] in [web_map.id for web_map in web_maps]:
            arcpy.AddMessage(f"{app.title}, {app.owner}, {app.homepage}")


def search_widgets(widgets, app, service):
  for widget in widgets:
    if 'uri' in widget.keys() and widget['uri'] == 'widgets/Search/Widget':
      for source in widget['config']['sources']:
        if service.lower() in source['url'].lower() and 'searchFields' in source.keys():
          arcpy.AddMessage(f"{app.title} | {source['url']}")

def app_search(services): 
  web_apps = gis.content.search(query = '', item_type='Web Mapping Application', max_items=10000)
  if not web_apps:
    arcpy.AddMessage("No apps found!")
    return
  for app in web_apps:
    for service in services:
      try:
        search_widgets(app.get_data()['widgetOnScreen']['widgets'], app, service)
        search_widgets(app.get_data()['widgetPool']['widgets'], app, service)
      except:
        continue

def group_search(services):
    for service in services:
        groups = gis.groups.search(query=f"", max_groups=10000)
        if groups == []:
            arcpy.AddMessage("No groups found!")
        for group in groups:
            for web_map in group.content():
                if web_map.type == "Feature Service" and web_map.url.lower() == service.lower():
                    arcpy.AddMessage(f"{group.title}, {group.owner}, {group.homepage}")

def main():
    arcpy.AddMessage(f"{gis.properties['user']['username']}@{arcpy.GetActivePortalURL()}")
    services = arcpy.GetParameter(0)

    arcpy.AddMessage('Webmaps')
    maps = web_map_search(services)
    arcpy.AddMessage('Webapps')
    map_apps(maps)
    arcpy.AddMessage('Groups')
    group_search(services)

if __name__ == '__main__':
    main()
