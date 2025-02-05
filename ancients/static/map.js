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
// map.fitWorld();


const markers = JSON.parse(
  document.getElementById(
    "markers-data"
  ).textContent
);
let feature = L.geoJSON(markers)
  .bindPopup(function (layer) {
    return layer
      .feature.properties.name;
  })
  .addTo(map);
map.fitBounds(feature.getBounds(), {
  padding: [100, 100],
});

map.setZoom(3)