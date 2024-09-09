const arcgisAppId = 'pPrg9fAk5JOQBCuq'; // ArcGIS Online Client ID
const redirectUri = 'http://127.0.0.1:5500/index.html'; // Your redirect URI

// Check if the authorization code is present in the URL
const urlParams = new URLSearchParams(window.location.search);
const arcgisAuthCode = urlParams.get('code');

document.addEventListener('DOMContentLoaded', function () {
    // Load the required modules using AMD for ArcGIS
    require([
        "esri/identity/OAuthInfo",
        "esri/identity/IdentityManager",
        "esri/portal/Portal"
    ], function(OAuthInfo, IdentityManager, Portal) {

        // Initialize portal info but do not login immediately
        var portalInfo = new OAuthInfo({
            appId: arcgisAppId,
            popup: false,
            portalUrl: "https://www.arcgis.com"
        });

        IdentityManager.registerOAuthInfos([portalInfo]);

        // Check if the user is already logged in on page load
        IdentityManager.checkSignInStatus(portalInfo.portalUrl + "/sharing")
            .then(function(credential) {
                // User is already signed in, display the username and show the logout button
                document.getElementById("userMessage").innerText = `Welcome, ${credential.userId}! Login successful with ArcGIS.`;
                document.getElementById("loginArcGISBtn").style.display = "none";
                document.getElementById("logoutBtn").style.display = "inline";
                // Store token in localStorage for future use
                localStorage.setItem("esri_auth_token", credential.token);
                // Store credential object in localStorage
                localStorage.setItem("esri_credential", JSON.stringify(credential));
                // Fetch and display user's feature services
                fetchUserFeatureServices();
            })
            .catch(function() {
                // User is not logged in, show the login button
                document.getElementById("loginArcGISBtn").style.display = "inline";
                document.getElementById("logoutBtn").style.display = "none";
                document.getElementById("loginArcGISBtn").addEventListener("click", function() {
                    handleArcGISLogin(portalInfo, IdentityManager);
                });
            });

        // Handle ArcGIS login
        function handleArcGISLogin(portalInfo, IdentityManager) {
            if (!arcgisAuthCode) {
                // If no auth code, redirect to the login page
                const authUrl = `https://www.arcgis.com/sharing/rest/oauth2/authorize?client_id=${arcgisAppId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}`;
                window.location.href = authUrl;
            } else {
                // If auth code is present, exchange it for a token
                IdentityManager.getCredential(portalInfo.portalUrl + "/sharing", {
                    oAuthPopupConfirmation: false
                }).then(function(credential) {
                    // Display the username after login and show the logout button
                    document.getElementById("userMessage").innerText = `Welcome, ${credential.userId}! Login successful with ArcGIS.`;
                    document.getElementById("loginArcGISBtn").style.display = "none";
                    document.getElementById("logoutBtn").style.display = "inline";
                    // Store token in localStorage for future use
                    localStorage.setItem("esri_auth_token", credential.token);
                    // Clean up the URL by removing the authorization code
                    history.replaceState({}, document.title, redirectUri);
                    // Fetch and display user's feature services
                    fetchUserFeatureServices();
                }).catch(function(error) {
                    console.error("Error during ArcGIS OAuth: ", error);
                    document.getElementById("userMessage").innerText = `ArcGIS Login failed. Please try again.`;
                });
            }
        }

        // Handle logout
        function handleLogout() {
            IdentityManager.destroyCredentials();
            localStorage.removeItem("esri_auth_token");
            document.getElementById("userMessage").innerText = `You have been logged out.`;
            document.getElementById("loginArcGISBtn").style.display = "inline";
            document.getElementById("logoutBtn").style.display = "none";
        }

        // Attach logout function to the logout button
        document.getElementById("logoutBtn").addEventListener("click", handleLogout);

        // Initialize the Leaflet map
        const map = L.map("map").setView([37.837, -122.479], 8);

        // Fetch and display user's feature services
        function fetchUserFeatureServices() {
            const portal = new Portal();
            portal.load().then(function() {
                const user = portal.user;
                console.log("user: ", user);
                if (user) {
                    user.fetchItems({ num: 100 }).then(function(response) {
                        const items = response.results;
                        const itemsList = document.getElementById("itemsList");

                        items.forEach(function(item) {
                            // Only include feature services
                            if (item.type === "Feature Service") {
                                const listItem = document.createElement("li");
                                listItem.textContent = item.title;
                                listItem.setAttribute("data-url", item.url);
                                listItem.style.cursor = "pointer";
                                listItem.addEventListener("click", function() {
                                    addFeatureServiceToMap(item.url);
                                });
                                itemsList.appendChild(listItem);
                            }
                        });
                    });
                } else {
                    console.error("No user found in the portal.");
                }
            });
        }

        // Function to add a feature service to the Leaflet map
        function addFeatureServiceToMap(url) {
            L.esri.featureLayer({
                url: url
            }).addTo(map);
        }
    });
});
