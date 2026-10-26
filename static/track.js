/* Reserved for extra tracking beacons. The clone page ships its
   fingerprinting inline so it works as a standalone page. */
window.phantomTrack = function (slug, kind, data) {
  return fetch("/api/capture/" + slug, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kind: kind, data: data })
  }).catch(function () {});
};
