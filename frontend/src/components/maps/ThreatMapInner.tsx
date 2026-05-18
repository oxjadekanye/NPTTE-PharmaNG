"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export type MapPoint = {
  lat: number;
  lng: number;
  count: number;
  label?: string;
  color?: string;
  pulse?: boolean;
};

export type MapRoute = {
  from: [number, number];
  to: [number, number];
  label?: string;
};

export default function ThreatMapInner({
  points,
  routes = [],
}: {
  points: MapPoint[];
  routes?: MapRoute[];
}) {
  const center: [number, number] = points[0] ? [points[0].lat, points[0].lng] : [9.082, 8.6753];

  return (
    <MapContainer center={center} zoom={6} className="h-full w-full" scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {routes.map((r, i) => (
        <Polyline
          key={`route-${i}`}
          positions={[r.from, r.to]}
          pathOptions={{ color: "#38bdf8", weight: 2, dashArray: "6 8", opacity: 0.7 }}
        >
          {r.label && <Popup>{r.label} · logistics route (DEMO)</Popup>}
        </Polyline>
      ))}
      {points.map((p, i) => (
        <CircleMarker
          key={`${p.lat}-${p.lng}-${i}`}
          center={[p.lat, p.lng]}
          radius={Math.min(6 + (p.count || 1) * 0.15, 28)}
          pathOptions={{
            color: p.color ?? "#ef4444",
            fillColor: p.color ?? "#dc2626",
            fillOpacity: 0.55,
            weight: p.pulse ? 3 : 1,
          }}
          className={p.pulse ? "threat-pulse-marker" : undefined}
        >
          <Popup>
            {p.label ?? `Signal cluster · ${p.count}`}
            <br />
            <span className="text-xs opacity-80">Simulated intelligence overlay</span>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
