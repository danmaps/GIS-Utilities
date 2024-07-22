import requests
import time
import arcpy
import json
import os
import subprocess

import prompts
# import importLib


# TODO: add support for API key from Windows Credential Manager
# TODO: add option to use claude instead of openai
# TODO: reseach local llms and add support for them


def map_to_json(in_map=None, output_json_path=None):
    """
    Generates a JSON object containing information about a map.

    Args:
        in_map (str, optional): The name of the map to get information from. If not provided, the active map in the current project will be used. Defaults to None.
        output_json_path (str, optional): The path to the JSON file where the map information will be saved. If not provided, the map information will not be saved. Defaults to None.

    Returns:
        dict: A dictionary containing information about the map, including the map name, title, description, spatial reference, layers, and properties.

    Raises:
        ValueError: If no active map is found in the current project.

    Notes:
        - The function uses the `arcpy` module to interact with the ArcGIS Pro application.
        - The function collects information about the active map, including the map name, title, description, spatial reference, and layers.
        - For each layer, the function collects information such as the layer name, feature layer status, raster layer status, web layer status, visibility, metadata, spatial reference, extent, fields, record count, source type, geometry type, renderer, and labeling.
        - If `output_json_path` is provided, the map information will be saved to a JSON file at the specified path.

    Example:
        >>> map_info = map_to_json()
        >>> print(map_info)
        {
            "map_name": "MyMap",
            "title": "My Map",
            "description": "This is my map.",
            "spatial_reference": "WGS84",
            "layers": [
                {
                    "name": "MyLayer",
                    "feature_layer": True,
                    "raster_layer": False,
                    "web_layer": False,
                    "visible": True,
                    "metadata": {
                        "title": "My Layer",
                        "tags": ["Tag1", "Tag2"],
                        "summary": "This is my layer.",
                        "description": "This is a description of my layer.",
                        "credits": "Credits for the layer.",
                        "access_constraints": "Access constraints for the layer.",
                        "extent": {
                            "xmin": -180,
                            "ymin": -90,
                            "xmax": 180,
                            "ymax": 90
                        }
                    },
                    "spatial_reference": "WGS84",
                    "extent": {
                        "xmin": -180,
                        "ymin": -90,
                        "xmax": 180,
                        "ymax": 90
                    },
                    "fields": [
                        {
                            "name": "ID",
                            "type": "Integer",
                            "length": 10
                        },
                        {
                            "name": "Name",
                            "type": "String",
                            "length": 50
                        }
                    ],
                    "record_count": 100,
                    "source_type": "FeatureClass",
                    "geometry_type": "Point",
                    "renderer": "SimpleRenderer",
                    "labeling": True
                }
            ],
            "properties": {
                "rotation": 0,
                "units": "DecimalDegrees",
                "time_enabled": False,
                "metadata": {
                    "title": "My Map",
                    "tags": ["Tag1", "Tag2"],
                    "summary": "This is my map.",
                    "description": "This is a description of my map.",
                    "credits": "Credits for the map.",
                    "access_constraints": "Access constraints for the map.",
                    "extent": {
                        "xmin": -180,
                        "ymin": -90,
                        "xmax": 180,
                        "ymax": 90
                    }
                }
            }
        }
    """

    # Function to convert metadata to a dictionary
    def metadata_to_dict(metadata):
        """
        Convert the given metadata object to a dictionary.

        Parameters:
            metadata (object): The metadata object to be converted.

        Returns:
            dict: The dictionary representation of the metadata object.

        Raises:
            None.

        Example:
            >>> metadata = Metadata(title="My Map", tags=["Tag1", "Tag2"], summary="This is my map.", description="This is a description of my map.", credits="Credits for the map.", accessConstraints="Access constraints for the map.", XMax=180, XMin=-180, YMax=90, YMin=-90)
            >>> metadata_to_dict(metadata)
            {'title': 'My Map', 'tags': ['Tag1', 'Tag2'], 'summary': 'This is my map.', 'description': 'This is a description of my map.', 'credits': 'Credits for the map.', 'access_constraints': 'Access constraints for the map.', 'extent': {'xmax': 180, 'xmin': -180, 'ymax': 90, 'ymin': -90}}
        """
        if metadata is None:
            return "No metadata"

        extent_dict = {}
        if hasattr(metadata, "XMax"):
            extent_dict["xmax"] = metadata.XMax
        if hasattr(metadata, "XMin"):
            extent_dict["xmin"] = metadata.XMin
        if hasattr(metadata, "YMax"):
            extent_dict["ymax"] = metadata.YMax
        if hasattr(metadata, "YMin"):
            extent_dict["ymin"] = metadata.YMin

        meta_dict = {
            "title": metadata.title if hasattr(metadata, "title") else "No title",
            "tags": metadata.tags if hasattr(metadata, "tags") else "No tags",
            "summary": metadata.summary
            if hasattr(metadata, "summary")
            else "No summary",
            "description": metadata.description
            if hasattr(metadata, "description")
            else "No description",
            "credits": metadata.credits
            if hasattr(metadata, "credits")
            else "No credits",
            "access_constraints": metadata.accessConstraints
            if hasattr(metadata, "accessConstraints")
            else "No access constraints",
            "extent": extent_dict,
        }
        return meta_dict

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    if not in_map:
        active_map = aprx.activeMap
        if not active_map:
            raise ValueError("No active map found in the current project.")
    else:
        active_map = aprx.listMaps(in_map)[0]

    # Collect map information
    map_info = {
        "map_name": active_map.name,
        "title": active_map.title if hasattr(active_map, "title") else "No title",
        "description": active_map.description
        if hasattr(active_map, "description")
        else "No description",
        "spatial_reference": active_map.spatialReference.name,
        "layers": [],
        "properties": {
            "rotation": active_map.rotation
            if hasattr(active_map, "rotation")
            else "No rotation",
            "units": active_map.units if hasattr(active_map, "units") else "No units",
            "time_enabled": active_map.isTimeEnabled
            if hasattr(active_map, "isTimeEnabled")
            else "No time enabled",
            "metadata": metadata_to_dict(active_map.metadata)
            if hasattr(active_map, "metadata")
            else "No metadata",
        },
    }

    # Iterate through layers and collect information
    for layer in active_map.listLayers():
        layer_info = {
            "name": layer.name,
            "feature_layer": layer.isFeatureLayer,
            "raster_layer": layer.isRasterLayer,
            "web_layer": layer.isWebLayer,
            "visible": layer.visible,
            "metadata": metadata_to_dict(layer.metadata)
            if hasattr(layer, "metadata")
            else "No metadata",
        }

        if layer.isFeatureLayer:
            dataset = arcpy.Describe(layer.dataSource)
            layer_info.update(
                {
                    "spatial_reference": dataset.spatialReference.name
                    if hasattr(dataset, "spatialReference")
                    else "Unknown",
                    "extent": {
                        "xmin": dataset.extent.XMin,
                        "ymin": dataset.extent.YMin,
                        "xmax": dataset.extent.XMax,
                        "ymax": dataset.extent.YMax,
                    }
                    if hasattr(dataset, "extent")
                    else "Unknown",
                    "fields": [],
                    "record_count": 0,
                    "source_type": dataset.dataType
                    if hasattr(dataset, "dataType")
                    else "Unknown",
                    "geometry_type": dataset.shapeType
                    if hasattr(dataset, "shapeType")
                    else "Unknown",
                    "renderer": layer.symbology.renderer.type
                    if hasattr(layer, "symbology")
                    and hasattr(layer.symbology, "renderer")
                    else "Unknown",
                    "labeling": layer.showLabels
                    if hasattr(layer, "showLabels")
                    else "Unknown",
                }
            )

            # Get fields information
            if hasattr(dataset, "fields"):
                for field in dataset.fields:
                    field_info = {
                        "name": field.name,
                        "type": field.type,
                        "length": field.length,
                    }
                    layer_info["fields"].append(field_info)

            # Get record count if the layer has records
            if dataset.dataType in ["FeatureClass", "Table"]:
                layer_info["record_count"] = int(
                    arcpy.management.GetCount(layer.dataSource)[0]
                )

        map_info["layers"].append(layer_info)

    if output_json_path:
        # Write the map information to a JSON file
        with open(output_json_path, "w") as json_file:
            json.dump(map_info, json_file, indent=4)

        print(f"Map information has been written to {output_json_path}")

    return map_info


def get_ai_response(api_key, messages):
    """
    Generates an AI response for a given set of messages using the chat completions endpoint.

    Parameters:
    api_key (str): API key for OpenAI.
    messages (list): List of message dictionaries for the AI chat.

    Returns:
    str: AI response.
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.5,  # be more predictable, less creative
        "max_tokens": 500,
    }

    for _ in range(3):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                verify=False,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying AI response generation due to: {e}")
            time.sleep(1)
    raise Exception("Failed to get AI response after retries")


def generate_python(api_key, map_info, prompt, explain=False):
    """
    Generate python using AI response for a given API key, JSON data, and a question.

    Parameters:
    api_key (str): API key for OpenAI.
    json_data (dict): JSON data containing map information.
    prompt (str): A prompt for the AI referring to a certain selection in the map.

    Returns:
    str: AI-generated insights.
    """
    if prompt:
        messages = [
            {"role": "system", "content": prompts.python_PROMPT},
            {"role": "user", "content": f"{prompts.example_PROMPT}"},
            {"role": "assistant", "content": f"{prompts.example_PYTHON}"},
            {"role": "user", "content": f"{prompts.example_PROMPT2}"},
            {"role": "assistant", "content": f"{prompts.example_PYTHON2}"},
            {"role": "system", "content": json.dumps(map_info, indent=4)},
            {"role": "user", "content": f"{prompt}"},
        ]

    try:
        code_snippet = get_ai_response(api_key, messages)

        def trim_code_block(code_block):
            # Remove the ```python from the beginning and ``` from the end
            if code_block.startswith("```python"):
                code_block = code_block[len("```python") :].strip()
            if code_block.endswith("```"):
                code_block = code_block[: -len("```")].strip()
            return code_block

        # trim response and show to user through message
        code_snippet = trim_code_block(code_snippet)
        line = f"<html><hr></html>"
        arcpy.AddMessage("AI generated code:")
        arcpy.AddMessage(line)
        arcpy.AddMessage(code_snippet)
        arcpy.AddMessage(line)

    except Exception as e:
        arcpy.AddError(str(e))
        return

    return code_snippet


def get_top_n_records(feature_class, fields, n):
    """
    Retrieves the top 5 records from a feature class.
    
    Parameters:
    feature_class (str): Path to the feature class.
    fields (list): List of fields to retrieve.

    Returns:
    list: A list of dictionaries containing the top 5 records.
    """
    records = []

    try:
        with arcpy.da.SearchCursor(feature_class, fields) as cursor:
            for i, row in enumerate(cursor):
                if i >= n:
                    break
                record = {field: value for field, value in zip(fields, row)}
                records.append(record)
                
    except Exception as e:
        arcpy.AddError(f"Error retrieving records: {e}")
    
    return records

def get_layer_info(input_layers):
    """
    Gathers layer information, including data records, for the selected layer.
    This is for context for the AI response. Keeping this separate from the map
    information might make users feel more comfortable sharing data with the AI.
    They can easily control, and see/edit, what data is passed to the AI.

    Returns:
    dict: JSON object representing the layer.
    """
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap
    layers_info = {}
        
    if input_layers:
        for l in input_layers:
            layer = active_map.listLayers(l)[0]
            if layer.isFeatureLayer:
                layers_info[layer.name] = {"name": layer.name, "path": layer.dataSource}
                dataset = arcpy.Describe(layer.dataSource)
                layers_info[layer.name]["data"] = get_top_n_records(layer, [f.name for f in dataset.fields], 5)
    
    return layers_info


def combine_map_and_layer_info(map_info, layer_info=None):
    """
    Combines the map and layer information into a single JSON object.

    Returns:
    dict: JSON object representing the map and layer information.
    """
    return {"map": map_info, "layer": layer_info}

def get_env_var(var_name="OPENAI_API_KEY"):
    arcpy.AddMessage(f"Fetching API key from {var_name} environment variable.")
    return os.environ.get(var_name, "")

def get_api_key_from_credential_manager():
    try:
        # Use PowerShell to retrieve the credential
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-StoredCredential -Target 'OpenAI_API_Key' | Select-Object -Property UserName, Password | ConvertTo-Json"],
            capture_output=True, text=True, check=True
        )
        
        # Parse the JSON output
        credential = json.loads(result.stdout)
        
        # The Password property contains the API key
        return credential['Password']
    except subprocess.CalledProcessError:
        print("Error retrieving the API key from Windows Credential Manager.")
        return None
    except json.JSONDecodeError:
        print("Error parsing the credential information.")
        return None
    except KeyError:
        print("API key not found in the credential.")
        return None

def add_ai_response_to_feature_layer(api_key, in_layer, out_layer, field_name, prompt_template, sql_query=None):
    """
    Enriches an existing feature layer by adding a new field with AI-generated responses.

    Parameters:
    api_key (str): API key for OpenAI.
    in_layer (str): Path to the input feature layer.
    out_layer (str): Path to the output feature layer. If None, in_layer will be updated.
    field_name (str): Name of the field to add the AI responses.
    prompt_template (str): Template for the prompt to be used by AI.
    sql_query (str, optional): Optional SQL query to filter the features.
    """
    if out_layer:
        arcpy.CopyFeatures_management(in_layer, out_layer)
        layer_to_use = out_layer
    else:
        layer_to_use = in_layer

    arcpy.AddMessage(layer_to_use)

    # Add new field for AI responses
    if field_name not in [f.name for f in arcpy.ListFields(layer_to_use)]:
        arcpy.management.AddField(layer_to_use, field_name, "TEXT")
    else:
        arcpy.management.AddField(layer_to_use, field_name + "_AI", "TEXT")
        field_name += "_AI"

    def generate_ai_responses_for_feature_class(feature_class, field_name, prompt_template):
        """
        Generates AI responses for each feature in the feature class and updates the new field with these responses.

        Parameters:
        api_key (str): API key for OpenAI.
        feature_class (str): Path to the feature class.
        field_name (str): Name of the field to add the AI responses.
        prompt_template (str): Template for the prompt to be used by AI.
        """
        # Get the OID field name
        desc = arcpy.Describe(feature_class)
        oid_field_name = desc.OIDFieldName

        # Define the fields to be included in the cursor
        fields = [field.name for field in arcpy.ListFields(feature_class)]
        
        # Ensure the new field exists
        if field_name not in fields:
            arcpy.AddField_management(feature_class, field_name, "TEXT")
        
        fields.append(field_name)  # Add the new field to the fields list

        # Store prompts and their corresponding OIDs in a dictionary
        prompts_dict = {}

        # Use a SearchCursor to iterate over the rows in the feature class and generate prompts
        with arcpy.da.SearchCursor(feature_class, fields[:-1], sql_query) as cursor:  # Exclude the new field
            for row in cursor:
                row_dict = {field: value for field, value in zip(fields[:-1], row)}
                formatted_prompt = prompt_template.format(**row_dict)
                oid = row_dict[oid_field_name]
                prompts_dict[oid] = formatted_prompt

        # Debug: Check a sample record from prompts_dict
        if prompts_dict:
            # Get the first key-value pair from the dictionary
            sample_oid, sample_prompt = next(iter(prompts_dict.items()))
            arcpy.AddMessage(f"{oid_field_name} {sample_oid}: {sample_prompt}")
        else:
            arcpy.AddMessage("prompts_dict is empty.")

        # Get AI responses for each prompt
        role = "You are a helpful assistant. Respond in one simple sentence without preamble or extra context."
        responses_dict = {
            oid: get_ai_response(api_key, [{"role": "system", "content": role}, {"role": "user", "content": prompt}])
            for oid, prompt in prompts_dict.items()
        }

        # Use an UpdateCursor to write the AI responses back to the feature class
        with arcpy.da.UpdateCursor(feature_class, [oid_field_name, field_name]) as cursor:
            for row in cursor:
                oid = row[0]
                if oid in responses_dict:
                    row[1] = responses_dict[oid]
                    cursor.updateRow(row)
    
    generate_ai_responses_for_feature_class(layer_to_use, field_name, prompt_template)


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Assist"
        self.alias = "Assist"

        # List of tool classes associated with this toolbox
        self.tools = [GenerateAIFeatureLayer,
                      GenerateAIField,
                      GenerateAIMapInsights,
                      GenerateAIPythonCode]


class GenerateAIFeatureLayer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate AI Feature Layer"
        self.description = "Generate AI Feature Layer"

    def getParameterInfo(self):
        """Define the tool parameters."""

        params = None
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
class GenerateAIField(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate AI Field"
        self.description = "Adds a new attribute field to feature layers with AI-generated text. It uses the OpenAI API to create responses based on user-defined prompts that can reference existing attributes. Users provide the input layer, output layer, field name, prompt template, and an optional SQL query. The tool enriches datasets but may produce inconsistent or unexpected AI responses, reflecting the nature of AI text generation."
        self.getParameterInfo()

    def getParameterInfo(self):
        """Define the tool parameters."""
        in_layer = arcpy.Parameter(
            displayName="Input Layer",
            name="in_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        out_layer = arcpy.Parameter(
            displayName="Output Layer",
            name="out_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        field_name = arcpy.Parameter(
            displayName="Field Name",
            name="field_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        prompt = arcpy.Parameter(
            displayName="Prompt",
            name="prompt",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        sql = arcpy.Parameter(
            displayName="SQL Query",
            name="sql",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )

        params = [in_layer, out_layer, field_name, prompt, sql]
        # params = None
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Get the API key from the environment variable
        api_key = get_env_var()
        add_ai_response_to_feature_layer(api_key,
                                         parameters[0].valueAsText,
                                         parameters[1].valueAsText,
                                         parameters[2].valueAsText,
                                         parameters[3].valueAsText,
                                         parameters[4].valueAsText)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
class GenerateAIMapInsights(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate AI Map Insights"
        self.description = "Generate AI Map Insights"

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = None
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
class GenerateAIPythonCode(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate AI Python Code"
        self.description = "Generate AI Python Code"
        self.params = arcpy.GetParameterInfo()
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define the tool parameters."""
        layers = arcpy.Parameter(
            displayName="Layers for context",
            name="layers_for_context",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Optional",
            direction="Input",
            multiValue=True,
        )
        # layers.controlCLSID = '{60061247-BCA8-473E-A7AF-A2026DDE1C2D}'

        prompt = arcpy.Parameter(
            displayName="Prompt",
            name="prompt",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        eval = arcpy.Parameter(
            displayName="Run the code (not a good idea!)",
            name="eval",
            datatype="Boolean",
            parameterType="Required",
            direction="Input",
        )
        
        eval.value = False # default value False

        context = arcpy.Parameter(
            displayName="Context (this will be passed to the AI)",
            name="context",
            datatype="GPstring",
            parameterType="Optional",
            direction="Input",
            category="Context",
        )
        context.controlCLSID = '{E5456E51-0C41-4797-9EE4-5269820C6F0E}'

        params = [layers,prompt,eval,context]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        layers = parameters[0].values
        context_json = combine_map_and_layer_info(map_to_json(),get_layer_info(layers))
        parameters[3].value = json.dumps(context_json, indent=2)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):

        # importLib.reload(prompts)

        # Get the API key from the environment variable
        api_key = get_env_var()
        layers = parameters[0].values # feature layer (multiple)
        prompt = parameters[1].value  # string
        eval = parameters[2].value  # boolean
        # if layers:
        #     derived_context = combine_map_and_layer_info(map_to_json(),get_layer_info(layers))
        # else:
        #     derived_context = ""
        derived_context = parameters[3]
        # parameters[3].SetParameterAsText(derived_context)

        #debug
        # arcpy.AddMessage("api_key: {}".format(api_key))
        # arcpy.AddMessage("feature_layer: {}".format(layers))
        # arcpy.AddMessage("prompt: {}".format(prompt))
        # arcpy.AddMessage("eval: {}".format(eval))

        code_snippet = generate_python(
            api_key,
            derived_context.value,
            prompt.strip(),
        )

        if eval == True:
            try:
                if code_snippet:
                    # execute the code
                    arcpy.AddMessage("Executing code... fingers crossed!")
                    exec(code_snippet)
                else:
                    raise Exception("No code generated. Please try again.")

            # catch AttributeError: 'NoneType' object has no attribute 'camera'
            except AttributeError as e:
                arcpy.AddError(f"{e}\n\nMake sure a map view is active.")
            except Exception as e:
                arcpy.AddError(
                    f"{e}\n\nThe code may be invalid. Please check the code and try again."
                )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return