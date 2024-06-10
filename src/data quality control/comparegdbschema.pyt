import arcpy
import csv
import os
import tempfile
import shutil
from datetime import datetime

from comparegdbschema_utils import generate_schema_report, compare_csv


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Compare GDB Schema"
        self.alias = "comparegdbschema"

        # List of tool classes associated with this toolbox
        self.tools = [SchemaComparisonTool]


class SchemaComparisonTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Compare GDB Schema"
        self.alias = "comparegdbschema"
        self.description = "Generates and compares schema reports for two geodatabases."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param0 = arcpy.Parameter(
            displayName="Geodatabase 1 (OEIS GDB template)",
            name="geodatabase1",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
            
        param0.value=r"P:\PROJECTS\Special_Projects\WSD_GIS_Schema\Draft_WSD_FGDB\Version6_2024_Q1\XXX_2024_QX.gdb"
        params.append(param0)

        param1 = arcpy.Parameter(
            displayName="Geodatabase 2 (The GDB you want to check)",
            name="geodatabase2",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1.value=r"P:\PROJECTS\Special_Projects\WSD_GIS_Schema\Tools\XXX_2024_QX_1.gdb"
        params.append(param1)

        param2 = arcpy.Parameter(
            displayName="Output CSV 1",
            name="output_csv1",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        param2.value=os.path.join(tempfile.gettempdir(), "gdb1.csv")
        params.append(param2)

        param3 = arcpy.Parameter(
            displayName="Output CSV 2",
            name="output_csv2",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")
        
        param3.value=os.path.join(tempfile.gettempdir(), "gdb2.csv")
        params.append(param3)

        param4 = arcpy.Parameter(
            displayName="Generate Detailed Report",
            name="detailed_report",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        
        param4.value=False
        params.append(param4)

        param5 = arcpy.Parameter(
        displayName="Feature Classes/Tables to Include",
        name="include_items",
        datatype="DEFeatureClass",
        parameterType="Optional",
        direction="Input",
        multiValue=True,
        category="Advanced Options",
        )
        params.append(param5)
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.
            This method is called whenever a parameter has been changed."""
        gdb_path = parameters[0].valueAsText  # Get the path of the first geodatabase
        
        if gdb_path:
            # Use arcpy.ListFeatureClasses and arcpy.ListTables to get feature classes and tables
            feature_classes = arcpy.ListFeatureClasses(gdb_path)
            tables = arcpy.ListTables(gdb_path)
            
            # Combine feature classes and tables into a single list
            if feature_classes and tables:
                all_items = feature_classes + tables
            
                # Set the value for the "Feature Classes/Tables to Include" parameter
                parameters[5].value = all_items
                parameters[5].value = ';'.join(all_items)
    
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.
           This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        gdb1_path = parameters[0].valueAsText
        gdb1_name = arcpy.Describe(gdb1_path).baseName
        gdb2_path = parameters[1].valueAsText
        gdb2_name = arcpy.Describe(gdb2_path).baseName
        output_csv1 = parameters[2].valueAsText
        output_csv2 = parameters[3].valueAsText
        detailed_report = parameters[4].value

        try:
            # Get the current timestamp with microsecond precision
            timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            temp_gdb1 = os.path.join(tempfile.gettempdir(), f"{gdb1_name}_{timestamp}.gdb")
            temp_gdb2 = os.path.join(tempfile.gettempdir(), f"{gdb2_name}_{timestamp}.gdb")

            # Copy the geodatabases to a temporary location
            arcpy.management.Copy(gdb1_path, temp_gdb1)
            arcpy.management.Copy(gdb2_path, temp_gdb2)

            generate_schema_report(temp_gdb1, output_csv1, detailed_report)
            generate_schema_report(temp_gdb2, output_csv2, detailed_report)
            diffs = compare_csv(gdb1_name, gdb2_name, output_csv1, output_csv2, detailed_report)

            if diffs:
                arcpy.AddError("Differences found")
                for diff in diffs:
                    arcpy.AddMessage(diff)
            else:
                arcpy.AddMessage("No differences found.")

        except Exception as e:
            arcpy.AddError(str(e))
            raise e
        finally:
            # Clean up the temporary geodatabases
            shutil.rmtree(temp_gdb1, ignore_errors=True)
            shutil.rmtree(temp_gdb2, ignore_errors=True)

        return
