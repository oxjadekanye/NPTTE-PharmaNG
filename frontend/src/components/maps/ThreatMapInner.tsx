"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

type Point = { lat: number; lng: number; count: number };

export default function ThreatMapInner({ points }: { points: Point[] }) {
  const center: [number, number] = points[0]
    ? [points[0].lat, points[0].lng]
    : [9.082, 8.6753];

  return (
    <MapContainer center={center} zoom={6} className="h-full w-full" scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((p, i) => (
        <CircleMarker
          key={`${p.lat}-${p.lng}-${i}`}
          center={[p.lat, p.lng]}
          radius={Math.min(8 + p.count, 24)}
          pathOptions={{ color: "#ef4444", fillColor: "#dc2626", fillOpacity: 0.5 }}
        >
          <Popup>
            Counterfeit cluster · {p.count} signal{p.count > 1 ? "s" : ""}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
