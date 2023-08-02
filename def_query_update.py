target_map = arcpy.mp.ArcGISProject("CURRENT").activeView.map

def update_dq(target_map,find,replace):
    for layer in target_map.listLayers():
        if layer.isFeatureLayer:
            dq = layer.definitionQuery
            if dq:
                new_dq = dq.replace(find, replace)
                layer.definitionQuery=new_dq

    print(f"{target_map.name} definition queries updated")
    
# update_dq(target_map, "Loc A", "Loc B")