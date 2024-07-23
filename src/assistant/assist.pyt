from assist import *

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
        source = arcpy.Parameter(
            displayName="Source",
            name="source",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            # multiValue=True
        )
        # source.controlCLSID = '{172840BF-D385-4F83-80E8-2AC3B79EB0E0}'
        source.filter.type = "ValueList"
        source.filter.list = ["OpenAI", "Wolfram Alpha"]
        source.value = "OpenAI"

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

        params = [source, in_layer, out_layer, field_name, prompt, sql]
        # params = None
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        source = parameters[0].value

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # associate the source with the api key variable name
        api_key_name = {"OpenAI": "OPENAI_API_KEY", "Wolfram Alpha": "WOLFRAM_ALPHA_API_KEY"}[parameters[0].valueAsText]
        # Get the API key from the environment variable
        api_key = get_env_var(api_key_name)
        # arcpy.AddMessage(f"api_key: {api_key}")
        add_ai_response_to_feature_layer(api_key,
                                         parameters[0].valueAsText,
                                         parameters[1].valueAsText,
                                         parameters[2].valueAsText,
                                         parameters[3].valueAsText,
                                         parameters[4].valueAsText,
                                         parameters[5].valueAsText)
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
        # combine map and layer data into one JSON
        context_json = {"map": map_to_json(), "layers": get_layer_info(layers)}
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