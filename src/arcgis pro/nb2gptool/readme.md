# nb2gptool

The .atbx format makes this theoretically possible.

see `\WSD_GIS_Schema\Tools\OEIS QDR Geodatabase Quality Control\CABoundary.tool\tool.content`

It is possible to programmatically create tools inside toolboxes. I can see the "params" json node.

Steps:
	1. User prototypes a workflow by adding geoprocessing tools to notebook cells until desired output is acheived.
		a. Go ahead and turn in this deliverable. After all, you've got work to do!
		b. Optionally, the following steps encapsulate the process into a reusable, shareable GP tool.
	2. Add parameter cells up at the top of the notebook. (tag that cell, papermill style)
	3. Run a custom python function which outputs a .py file and a corresponding .atbx
		a. This tool could also write and run tests, to increase confidence in the output
		b. Avoids skeptical users feeling obligation to run the output tool over and over again
        c. Create a well formatted (very readable) report about how to tool functions. Proof that this is working.
    4. Use openai api for automatic documentation generation
        a. create prompts that extract and provide descriptions for parameters and tool usage information from the parsed notebook

Idea:
	Use textual as UI for configuration steps. List parameters, data types, geoprocessing tools, etc? Allow renaming of parameters and editing of ai generated documentation.

	