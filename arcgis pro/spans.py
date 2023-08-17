import arcpy

def flip_lines_near_points(input_lines, points, distance, bearing_field='BEARING_FIELD', line_bearing='LINE_BEARING'):
    # Step 1: find eligible lines
    duplicate_dict = {}

    with arcpy.da.SearchCursor(input_lines, ['OID@','SHAPE@']) as line_cur:
        for oid, line in line_cur:
            start_pt, end_pt = arcpy.PointGeometry(line.firstPoint), arcpy.PointGeometry(line.lastPoint)
            
            start_near, end_near = False, False
            startfloc, endfloc = None, None
            
            with arcpy.da.SearchCursor(points, ['SHAPE@','FLOC']) as pt_cur:
                for pt in pt_cur:
                    dist_start = start_pt.distanceTo(pt[0]) 
                    if dist_start <= distance:
                        start_near = True
                        startfloc = pt[1]
                        
                with arcpy.da.SearchCursor(points, ['SHAPE@','FLOC']) as pt_cur:
                    for pt in pt_cur:
                        if end_pt.distanceTo(pt[0]) <= distance:
                            end_near = True
                            endfloc = pt[1]
                            
            if start_near and end_near: 
                duplicate_dict[oid] = (startfloc, endfloc)
        
    # Step 2: Add record with reverse line directions
    with arcpy.da.SearchCursor(input_lines, ['OID@','SHAPE@']) as line_cur:
        for line_oid, line in line_cur:
            if line_oid in duplicate_dict:
                start_floc, end_floc = duplicate_dict[line_oid]
                rev_line = arcpy.Polyline(line.getPart(0)[::-1])
                start_floc, end_floc = end_floc, start_floc
                
                # Use InsertCursor for new rows
                with arcpy.da.InsertCursor(input_lines, ['SHAPE@','floc','adjacent']) as ins_cur:
                    ins_cur.insertRow([rev_line, start_floc, end_floc])
                    
    # Step 3: Recalculate line directions
    arcpy.CalculateGeometryAttributes_management(
        input_lines, geometry_property=[[bearing_field, line_bearing]])
        
# Example Usage
input_lines = r"spans"
points = r"poles"
distance = 20 # unit based on Map's coordinate system linear unit value, usually US Survey Feet (0.3048006096012192)

flip_lines_near_points(input_lines, points, distance)



def degrees_to_cardinal(d):
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[int((d + 11.25)/22.5) % 16]

arcpy.management.CalculateField(
    in_table="Spans",
    field="Dir",
    expression="degrees_to_cardinal(!bearing!)",
    expression_type="PYTHON3",
    code_block="""
    def degrees_to_cardinal(d):
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return dirs[int((d + 11.25)/22.5) % 16]""",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)