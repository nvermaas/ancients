const copy =
  "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>";
const url =
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const layer = L.tileLayer(url, {
  attribution: copy,
});
const map = L.map("map", {
  layers: [layer]
});


const markers = JSON.parse(
  document.getElementById(
    "markers-data"
  ).textContent
);

const coordinates = JSON.parse(
  document.getElementById(
    "coordinates-data"
  ).textContent
);

let feature = L.geoJSON(markers)
  .bindPopup(function (layer) {
    return layer.feature.properties.name;
  }).addTo(map);

/*
L.geoJSON(markers, {
    pointToLayer: function (feature, latlng) {
        return new L.circleMarker(latlng, {
            radius: feature.properties.radius,
            fillColor: feature.properties.color,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        });
    },
}).addTo(map);
*/



// Fit the map to the markers' bounds
const bounds = feature.getBounds();
if (bounds.isValid()) {
  map.fitBounds(bounds, { padding: [10, 10] });

}

// if 'coordinate-data' is passed to the 'context' of the MapView then use them to set the map view
if (coordinates) {
  map.setView(new L.LatLng(coordinates['latitude'], coordinates['longtitude']), 15);
}

// Function to locate user
function locateUser() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;

                // Set map view
                map.setView([lat, lon], 14);

                // Add marker
                L.marker([lat, lon]).addTo(map)
                    .bindPopup("You are here!").openPopup();
            },
            function (error) {
                alert("Geolocation failed: " + error.message);
            }
        );
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

// Attach event listener to button
document.getElementById("locate-btn").addEventListener("click", locateUser);