Interestingly, this project was created with a special constraint. I did not use any 3rd party libraries that aren't included by default with ArcGIS Pro. Instead of the openai python package, I create and send `POST` requests to the OpenAI API using the `requests` library. A somewhat tricky endeavor, but worth it to be able to skip the cloning step. My coworkers all have ArcGIS Pro installed, and they don't have experience cloning conda environments, so it was important to consider this potential road-block and avoid it.


