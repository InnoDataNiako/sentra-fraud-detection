import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix pour les icônes Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface LeafletMapProps {
  center?: [number, number];
  zoom?: number;
}

export const LeafletMap: React.FC<LeafletMapProps> = ({
  center = [14.7167, -17.4677], // Dakar
  zoom = 5
}) => {
  return (
    <div className="h-full w-full">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[14.7167, -17.4677]}>
          <Popup>
            Dakar, Sénégal<br />
            Taux de fraude: 2.8%
          </Popup>
        </Marker>
        <Marker position={[5.3599, -4.0083]}>
          <Popup>
            Abidjan, Côte d'Ivoire<br />
            Taux de fraude: 2.85%
          </Popup>
        </Marker>
        <Marker position={[12.6392, -8.0029]}>
          <Popup>
            Bamako, Mali<br />
            Taux de fraude: 2.93%
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};