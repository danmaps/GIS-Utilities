'''
given an existing feature layer in arcgis pro, add a column that holds the response from an ai assistant

parameters:
    in layer
    out layer
    field
    prompt (with ability to refer to existing fields)
    sql query (only operate on matching records)
    
steps:
    convert feature layer to dataframe
    add the new text field
    parse fields and look for them in the prompt
    filter the data based on the sql query (if supplied)
    hit the openai assistant api for each prompt
    store the result in the new field
    convert the dataframe back to a feature layer

usage:
    if the prompt contains no field information, the AI will attempt to infer what you mean based on the geometry information

examples:
    given a feature class containing a list of US state capital cities and a prompt "a fun fact about this city"
    the "capital" column is assumed to be the target, so the query that's submitted is "a fun fact about {capital}"
    does this logic take a separate assistant?
    a simpler but less robust method might be to cram the whole row into the message, like "6 california sacramento, a fun fact about this city"
    or even "here is the subject of my query below: "OID: 6 state: california capital: sacramento" \n here is my query: "a fun fact about this city"

'''