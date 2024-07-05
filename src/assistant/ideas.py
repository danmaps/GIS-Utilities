''' ideas for additional assistant geoprocessing tools
- provide AI access to underlying data, currently only looking at fields and metadata
- generate insights about the underlying data
  - what kind of statistics do i want? I think i wrote about this elsewhere...

  What is notable about this data?

    Are there "data smells"?

    For example: 
        - it is the largest value in the dataset
        - This point is close to 3 lines in this other layer you have open in the map
        - This field value matches all the other records in the layer.
        - This field value is null, which is only the case for 0.4% of the records.
        - This point is far away from all the other geometry you're working with.
        - This point is coincident with a point from this other layer.

    A casual data exploration tool.

    Works with data schema, ranges, time series data

    Inspired by agol assistant and smashrun

    What's cool about smashrun, is that the runs are uploaded automatically. I'm imagining the same type of thing, but for geodatabases or feature services.

    Further design idea: select related records from other layers, generate a report based on this observation.

'''