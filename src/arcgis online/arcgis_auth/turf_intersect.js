
document.addEventListener('DOMContentLoaded', function() {
// Retrieve the existing token from localStorage
const accessToken = localStorage.getItem("esri_auth_token");

    console.log("token found!", accessToken);
    // Define the GeoJSON bounding boxes
    const boundingBoxes = {
        type: "FeatureCollection",
        features: [
            {
                type: "Feature",
                properties: { color: "orange" },
                geometry: {
                    type: "Polygon",
                    coordinates: [[
                        [-84.39010620117188, 33.747965492070236],
                        [-84.39010620117188, 33.75431694675655],
                        [-84.37311172485352, 33.75431694675655],
                        [-84.37311172485352, 33.747965492070236],
                        [-84.39010620117188, 33.747965492070236]
                    ]]
                }
            },
            {
                type: "Feature",
                properties: { color: "#0ceb70" },
                geometry: {
                    type: "Polygon",
                    coordinates: [[
                        [-84.39963340759277, 33.744254312044156],
                        [-84.39963340759277, 33.75817040902938],
                        [-84.38444137573242, 33.75817040902938],
                        [-84.38444137573242, 33.744254312044156],
                        [-84.39963340759277, 33.744254312044156]
                    ]]
                }
            }
        ]
    };

    // Initialize the map
    const map = L.map("map").setView([33.752, -84.385], 14.5);

    // Add the Esri vector basemap layer
    L.esri.Vector.vectorBasemapLayer("arcgis/imagery/standard", {
        token: accessToken
    }).addTo(map);

    // Display the bounding boxes on the map
    L.geoJSON(boundingBoxes, {
        style: function (feature) {
            return { color: feature.properties.color };
        }
    }).addTo(map);

    // Create a query to a feature layer
    const query = L.esri.query({
        url: "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/0"
    });

    // Perform a spatial query that intersects with the first bounding box
    query.intersects(boundingBoxes.features[0]);

    // Run the query
    query.run(function (err, censusCollection, raw) {
        if (err) {
            console.error("Query error: ", err);
            return;
        }

        const features = censusCollection.features;

        for (let i = 0; i < features.length; i++) {
            // Check if the feature is inside the second bounding box
            if (turf.booleanPointInPolygon(features[i], boundingBoxes.features[1])) {
                L.geoJSON(features[i], {
                    pointToLayer: function (geoJsonPoint, latlng) {
                        return L.circleMarker(latlng, {
                            color: "#ff0066"
                        });
                    }
                }).addTo(map);
            } else {
                L.geoJSON(features[i], {
                    pointToLayer: function (geoJsonPoint, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 10,
                            color: "gray",
                            opacity: 0.2
                        });
                    }
                }).addTo(map);
            }
        }
    });

});

