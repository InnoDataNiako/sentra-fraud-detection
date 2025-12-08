// import React, { useState, useEffect, useRef, useCallback } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
// import L from 'leaflet';
// import 'leaflet/dist/leaflet.css';
// import 'leaflet.heat';
// import { 
//   MapContainer, 
//   TileLayer, 
//   Marker, 
//   Popup, 
//   Circle, 
//   Polygon, 
//   LayersControl,
//   ZoomControl,
//   ScaleControl,
//   useMap,
//   useMapEvents
// } from 'react-leaflet';
// import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
// import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Slider } from '@/components/ui/slider';
// import { Switch } from '@/components/ui/switch';
// import { 
//   MapPin, 
//   Filter, 
//   ZoomIn, 
//   ZoomOut, 
//   Layers, 
//   Target, 
//   AlertTriangle, 
//   Shield,
//   TrendingUp,
//   Globe,
//   Crosshair,
//   Eye,
//   EyeOff,
//   Download,
//   Maximize2,
//   Minimize2
// } from 'lucide-react';
// import { format } from 'date-fns';
// import { fr } from 'date-fns/locale';

// // ============================================================================
// // TYPES ET DONNÉES
// // ============================================================================

// interface Transaction {
//   id: string;
//   amount: number;
//   location: string;
//   lat: number;
//   lng: number;
//   risk_score: number;
//   customer_id: string;
//   timestamp: string;
//   type: 'payment' | 'transfer' | 'withdrawal' | 'cash_in' | 'bill_payment';
//   status: 'approved' | 'blocked' | 'pending';
// }

// interface CityData {
//   name: string;
//   lat: number;
//   lng: number;
//   transactions: number;
//   frauds: number;
//   fraudRate: number;
//   avgAmount: number;
// }

// interface RiskMapProps {
//   transactions?: Transaction[];
//   timeRange?: '24h' | '7d' | '30d';
//   onCityClick?: (city: CityData) => void;
//   loading?: boolean;
// }

// // Données des principales villes UEMOA
// const UEMOA_CITIES: CityData[] = [
//   {
//     name: 'Dakar, Sénégal',
//     lat: 14.7167,
//     lng: -17.4677,
//     transactions: 1250,
//     frauds: 35,
//     fraudRate: 2.8,
//     avgAmount: 45000
//   },
//   {
//     name: 'Abidjan, Côte d\'Ivoire',
//     lat: 5.3599,
//     lng: -4.0083,
//     transactions: 980,
//     frauds: 28,
//     fraudRate: 2.85,
//     avgAmount: 52000
//   },
//   {
//     name: 'Bamako, Mali',
//     lat: 12.6392,
//     lng: -8.0029,
//     transactions: 750,
//     frauds: 22,
//     fraudRate: 2.93,
//     avgAmount: 38000
//   },
//   {
//     name: 'Ouagadougou, Burkina Faso',
//     lat: 12.3714,
//     lng: -1.5197,
//     transactions: 620,
//     frauds: 18,
//     fraudRate: 2.9,
//     avgAmount: 41000
//   },
//   {
//     name: 'Lomé, Togo',
//     lat: 6.1725,
//     lng: 1.2314,
//     transactions: 540,
//     frauds: 16,
//     fraudRate: 2.96,
//     avgAmount: 37000
//   },
//   {
//     name: 'Cotonou, Bénin',
//     lat: 6.3703,
//     lng: 2.3912,
//     transactions: 480,
//     frauds: 14,
//     fraudRate: 2.91,
//     avgAmount: 39000
//   },
//   {
//     name: 'Niamey, Niger',
//     lat: 13.5127,
//     lng: 2.1125,
//     transactions: 420,
//     frauds: 13,
//     fraudRate: 3.1,
//     avgAmount: 35000
//   },
//   {
//     name: 'Conakry, Guinée',
//     lat: 9.6412,
//     lng: -13.5784,
//     transactions: 380,
//     frauds: 11,
//     fraudRate: 2.89,
//     avgAmount: 32000
//   }
// ];

// // ============================================================================
// // COMPOSANTS LEAFLET PERSONNALISÉS
// // ============================================================================

// // Composant pour centrer la carte sur une position
// function CenterMap({ lat, lng }: { lat: number; lng: number }) {
//   const map = useMap();
  
//   useEffect(() => {
//     map.setView([lat, lng], map.getZoom());
//   }, [lat, lng, map]);
  
//   return null;
// }

// // Composant pour les contrôles personnalisés
// function CustomControls({ onToggleHeatmap, showHeatmap }: { 
//   onToggleHeatmap: () => void; 
//   showHeatmap: boolean;
// }) {
//   const map = useMap();
  
//   return (
//     <div className="leaflet-top leaflet-right">
//       <div className="leaflet-control leaflet-bar bg-white rounded-lg shadow-lg p-2 space-y-2">
//         <button
//           className="p-2 hover:bg-gray-100 rounded"
//           onClick={() => map.zoomIn()}
//           title="Zoom in"
//         >
//           <ZoomIn className="h-4 w-4" />
//         </button>
//         <button
//           className="p-2 hover:bg-gray-100 rounded"
//           onClick={() => map.zoomOut()}
//           title="Zoom out"
//         >
//           <ZoomOut className="h-4 w-4" />
//         </button>
//         <button
//           className="p-2 hover:bg-gray-100 rounded"
//           onClick={() => map.locate({setView: true})}
//           title="Localiser"
//         >
//           <Crosshair className="h-4 w-4" />
//         </button>
//         <button
//           className={`p-2 rounded ${showHeatmap ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'}`}
//           onClick={onToggleHeatmap}
//           title="Heatmap"
//         >
//           <Layers className="h-4 w-4" />
//         </button>
//       </div>
//     </div>
//   );
// }

// // Heatmap Layer
// function HeatmapLayer({ transactions, show }: { transactions: Transaction[]; show: boolean }) {
//   const map = useMap();
  
//   useEffect(() => {
//     if (!show || !transactions.length) return;
    
//     // @ts-ignore - leaflet.heat n'a pas de types officiels
//     const heatLayer = L.heatLayer(
//       transactions.map(tx => [tx.lat, tx.lng, tx.risk_score / 100]),
//       {
//         radius: 25,
//         blur: 15,
//         maxZoom: 17,
//         gradient: {
//           0.1: '#00ff00',
//           0.3: '#ffff00',
//           0.6: '#ffa500',
//           0.8: '#ff4500',
//           1.0: '#ff0000'
//         }
//       }
//     ).addTo(map);
    
//     return () => {
//       map.removeLayer(heatLayer);
//     };
//   }, [transactions, show, map]);
  
//   return null;
// }

// // ============================================================================
// // ICÔNES PERSONNALISÉES POUR LES MARQUEURS
// // ============================================================================

// const createCustomIcon = (riskScore: number) => {
//   const size = 32;
//   const color = riskScore > 70 ? '#ef4444' : riskScore > 30 ? '#f59e0b' : '#10b981';
  
//   return L.divIcon({
//     html: `
//       <div style="
//         width: ${size}px;
//         height: ${size}px;
//         background: ${color};
//         border: 2px solid white;
//         border-radius: 50%;
//         display: flex;
//         align-items: center;
//         justify-content: center;
//         color: white;
//         font-weight: bold;
//         font-size: 12px;
//         box-shadow: 0 2px 8px rgba(0,0,0,0.3);
//         cursor: pointer;
//       ">
//         ${Math.round(riskScore)}%
//       </div>
//     `,
//     className: 'custom-marker',
//     iconSize: [size, size],
//     iconAnchor: [size / 2, size / 2],
//     popupAnchor: [0, -size / 2]
//   });
// };

// // ============================================================================
// // COMPOSANT PRINCIPAL
// // ============================================================================

// export const RiskMap: React.FC<RiskMapProps> = ({
//   transactions = [],
//   timeRange = '7d',
//   onCityClick,
//   loading = false
// }) => {
//   const [selectedCity, setSelectedCity] = useState<CityData | null>(null);
//   const [showHeatmap, setShowHeatmap] = useState(true);
//   const [showMarkers, setShowMarkers] = useState(true);
//   const [showClusters, setShowClusters] = useState(true);
//   const [riskThreshold, setRiskThreshold] = useState([30]);
//   const [mapView, setMapView] = useState<'streets' | 'satellite' | 'light'>('streets');
//   const [isFullscreen, setIsFullscreen] = useState(false);
//   const mapRef = useRef<any>(null);
  
//   // Position initiale (centre de l'UEMOA)
//   const centerPosition: [number, number] = [10.0, -5.0];
//   const defaultZoom = 5;
  
//   // Générer des transactions simulées si pas de données
//   const displayTransactions = transactions.length > 0 ? transactions : generateMockTransactions();
  
//   // Filtrer par seuil de risque
//   const filteredTransactions = displayTransactions.filter(
//     tx => tx.risk_score >= riskThreshold[0]
//   );
  
//   // Gestion du clic sur une ville
//   const handleCityClick = useCallback((city: CityData) => {
//     setSelectedCity(city);
//     onCityClick?.(city);
    
//     if (mapRef.current) {
//       mapRef.current.setView([city.lat, city.lng], 10);
//     }
//   }, [onCityClick]);
  
//   // Toggle fullscreen
//   const toggleFullscreen = () => {
//     setIsFullscreen(!isFullscreen);
//   };
  
//   // Exporter la carte
//   const exportMap = () => {
//     if (mapRef.current) {
//       mapRef.current.exportToPng().then((dataUrl: string) => {
//         const link = document.createElement('a');
//         link.href = dataUrl;
//         link.download = `sentra-risk-map-${format(new Date(), 'yyyy-MM-dd')}.png`;
//         link.click();
//       });
//     }
//   };
  
//   // Calculer les statistiques
//   const stats = {
//     totalTransactions: displayTransactions.length,
//     highRiskTransactions: displayTransactions.filter(tx => tx.risk_score > 70).length,
//     totalAmount: displayTransactions.reduce((sum, tx) => sum + tx.amount, 0),
//     avgRiskScore: displayTransactions.reduce((sum, tx) => sum + tx.risk_score, 0) / displayTransactions.length,
//     fraudHotspots: UEMOA_CITIES.filter(city => city.fraudRate > 3).length
//   };
  
//   if (loading) {
//     return (
//       <Card className="h-[500px]">
//         <CardContent className="flex items-center justify-center h-full">
//           <div className="text-center space-y-4">
//             <div className="animate-spin">
//               <Globe className="h-12 w-12 text-blue-500" />
//             </div>
//             <p className="text-gray-600">Chargement de la carte...</p>
//           </div>
//         </CardContent>
//       </Card>
//     );
//   }
  
//   return (
//     <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white p-4' : ''}`}>
//       <Card className={`${isFullscreen ? 'h-full' : 'h-[500px]'}`}>
//         <CardHeader className="pb-3">
//           <div className="flex justify-between items-center">
//             <div>
//               <CardTitle className="flex items-center gap-2">
//                 <MapPin className="h-5 w-5 text-red-500" />
//                 Carte des Risques Géographiques
//               </CardTitle>
//               <CardDescription>
//                 Visualisation des hotspots de fraude dans la zone UEMOA
//               </CardDescription>
//             </div>
            
//             <div className="flex items-center gap-2">
//               <Button 
//                 variant="outline" 
//                 size="sm"
//                 onClick={toggleFullscreen}
//               >
//                 {isFullscreen ? (
//                   <Minimize2 className="h-4 w-4 mr-2" />
//                 ) : (
//                   <Maximize2 className="h-4 w-4 mr-2" />
//                 )}
//                 {isFullscreen ? 'Réduire' : 'Plein écran'}
//               </Button>
//               <Button 
//                 variant="outline" 
//                 size="sm"
//                 onClick={exportMap}
//               >
//                 <Download className="h-4 w-4 mr-2" />
//                 Exporter
//               </Button>
//             </div>
//           </div>
//         </CardHeader>
        
//         <CardContent className="h-[calc(100%-80px)] p-0">
//           <div className="flex h-full">
//             {/* Carte Leaflet */}
//             <div className="flex-1 relative">
//               <MapContainer
//                 center={centerPosition}
//                 zoom={defaultZoom}
//                 style={{ height: '100%', width: '100%' }}
//                 zoomControl={false}
//                 ref={mapRef}
//                 className="rounded-lg"
//               >
//                 <TileLayer
//                   attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//                   url={
//                     mapView === 'satellite' 
//                       ? 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
//                       : mapView === 'light'
//                       ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
//                       : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
//                   }
//                 />
                
//                 {/* Heatmap */}
//                 <HeatmapLayer 
//                   transactions={filteredTransactions} 
//                   show={showHeatmap} 
//                 />
                
//                 {/* Marqueurs pour les villes */}
//                 {showMarkers && UEMOA_CITIES.map((city, index) => {
//                   const icon = createCustomIcon(city.fraudRate * 25); // Convertir taux en score
                  
//                   return (
//                     <Marker
//                       key={`city-${index}`}
//                       position={[city.lat, city.lng]}
//                       icon={icon}
//                       eventHandlers={{
//                         click: () => handleCityClick(city)
//                       }}
//                     >
//                       <Popup>
//                         <div className="p-2 min-w-[200px]">
//                           <h3 className="font-bold text-lg mb-2">{city.name}</h3>
//                           <div className="space-y-1">
//                             <div className="flex justify-between">
//                               <span className="text-gray-600">Transactions:</span>
//                               <span className="font-semibold">{city.transactions}</span>
//                             </div>
//                             <div className="flex justify-between">
//                               <span className="text-gray-600">Fraudes:</span>
//                               <span className="font-semibold text-red-600">{city.frauds}</span>
//                             </div>
//                             <div className="flex justify-between">
//                               <span className="text-gray-600">Taux de fraude:</span>
//                               <span className="font-semibold">{city.fraudRate.toFixed(2)}%</span>
//                             </div>
//                             <div className="flex justify-between">
//                               <span className="text-gray-600">Montant moyen:</span>
//                               <span className="font-semibold">
//                                 {new Intl.NumberFormat('fr-FR').format(city.avgAmount)} XOF
//                               </span>
//                             </div>
//                           </div>
//                           <Button 
//                             size="sm" 
//                             className="w-full mt-3"
//                             onClick={() => handleCityClick(city)}
//                           >
//                             Voir les détails
//                           </Button>
//                         </div>
//                       </Popup>
//                     </Marker>
//                   );
//                 })}
                
//                 {/* Contrôles personnalisés */}
//                 <CustomControls 
//                   onToggleHeatmap={() => setShowHeatmap(!showHeatmap)} 
//                   showHeatmap={showHeatmap}
//                 />
//                 <ZoomControl position="bottomright" />
//                 <ScaleControl position="bottomleft" />
//               </MapContainer>
              
//               {/* Légende */}
//               <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-xs">
//                 <h4 className="font-semibold mb-2 flex items-center gap-2">
//                   <Layers className="h-4 w-4" />
//                   Légende
//                 </h4>
//                 <div className="space-y-2">
//                   <div className="flex items-center gap-2">
//                     <div className="w-4 h-4 rounded-full bg-red-500"></div>
//                     <span className="text-sm">Risque élevé (&gt; 70%)</span>
//                   </div>
//                   <div className="flex items-center gap-2">
//                     <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
//                     <span className="text-sm">Risque moyen (30-70%)</span>
//                   </div>
//                   <div className="flex items-center gap-2">
//                     <div className="w-4 h-4 rounded-full bg-green-500"></div>
//                     <span className="text-sm">Risque faible (&lt; 30%)</span>
//                   </div>
//                   {showHeatmap && (
//                     <div className="mt-2 pt-2 border-t">
//                       <div className="flex items-center justify-between">
//                         <span className="text-sm">Intensité heatmap:</span>
//                         <span className="text-xs text-gray-500">Risque ↑</span>
//                       </div>
//                       <div className="h-2 w-full rounded-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 mt-1"></div>
//                     </div>
//                   )}
//                 </div>
//               </div>
//             </div>
            
//             {/* Panneau de contrôle */}
//             <div className="w-80 border-l p-4 overflow-y-auto">
//               <Tabs defaultValue="controls">
//                 <TabsList className="grid grid-cols-3 mb-4">
//                   <TabsTrigger value="controls">
//                     <Layers className="h-4 w-4 mr-2" />
//                     Contrôles
//                   </TabsTrigger>
//                   <TabsTrigger value="stats">
//                     <TrendingUp className="h-4 w-4 mr-2" />
//                     Stats
//                   </TabsTrigger>
//                   <TabsTrigger value="hotspots">
//                     <AlertTriangle className="h-4 w-4 mr-2" />
//                     Hotspots
//                   </TabsTrigger>
//                 </TabsList>
                
//                 <TabsContent value="controls" className="space-y-4">
//                   <div>
//                     <h4 className="font-semibold mb-2 flex items-center gap-2">
//                       <Filter className="h-4 w-4" />
//                       Filtres
//                     </h4>
//                     <div className="space-y-3">
//                       <div>
//                         <label className="text-sm font-medium mb-2 block">
//                           Seuil de risque: {riskThreshold[0]}%
//                         </label>
//                         <Slider
//                           value={riskThreshold}
//                           onValueChange={setRiskThreshold}
//                           min={0}
//                           max={100}
//                           step={5}
//                         />
//                       </div>
                      
//                       <div className="space-y-2">
//                         <div className="flex items-center justify-between">
//                           <label className="text-sm">Heatmap</label>
//                           <Switch
//                             checked={showHeatmap}
//                             onCheckedChange={setShowHeatmap}
//                           />
//                         </div>
//                         <div className="flex items-center justify-between">
//                           <label className="text-sm">Marqueurs</label>
//                           <Switch
//                             checked={showMarkers}
//                             onCheckedChange={setShowMarkers}
//                           />
//                         </div>
//                         <div className="flex items-center justify-between">
//                           <label className="text-sm">Clusters</label>
//                           <Switch
//                             checked={showClusters}
//                             onCheckedChange={setShowClusters}
//                           />
//                         </div>
//                       </div>
//                     </div>
//                   </div>
                  
//                   <div>
//                     <h4 className="font-semibold mb-2">Vue de la carte</h4>
//                     <div className="grid grid-cols-3 gap-2">
//                       <Button
//                         variant={mapView === 'streets' ? 'default' : 'outline'}
//                         size="sm"
//                         onClick={() => setMapView('streets')}
//                       >
//                         Rues
//                       </Button>
//                       <Button
//                         variant={mapView === 'satellite' ? 'default' : 'outline'}
//                         size="sm"
//                         onClick={() => setMapView('satellite')}
//                       >
//                         Satellite
//                       </Button>
//                       <Button
//                         variant={mapView === 'light' ? 'default' : 'outline'}
//                         size="sm"
//                         onClick={() => setMapView('light')}
//                       >
//                         Clair
//                       </Button>
//                     </div>
//                   </div>
                  
//                   <div>
//                     <h4 className="font-semibold mb-2">Centrer sur</h4>
//                     <div className="space-y-2">
//                       {UEMOA_CITIES.slice(0, 4).map(city => (
//                         <Button
//                           key={city.name}
//                           variant="outline"
//                           size="sm"
//                           className="w-full justify-start"
//                           onClick={() => handleCityClick(city)}
//                         >
//                           <MapPin className="h-4 w-4 mr-2" />
//                           {city.name.split(',')[0]}
//                         </Button>
//                       ))}
//                     </div>
//                   </div>
//                 </TabsContent>
                
//                 <TabsContent value="stats" className="space-y-4">
//                   <div className="grid grid-cols-2 gap-3">
//                     <div className="bg-blue-50 p-3 rounded-lg">
//                       <div className="text-2xl font-bold text-blue-700">
//                         {stats.totalTransactions.toLocaleString('fr-FR')}
//                       </div>
//                       <div className="text-sm text-blue-600">Transactions</div>
//                     </div>
//                     <div className="bg-red-50 p-3 rounded-lg">
//                       <div className="text-2xl font-bold text-red-700">
//                         {stats.highRiskTransactions}
//                       </div>
//                       <div className="text-sm text-red-600">À haut risque</div>
//                     </div>
//                     <div className="bg-green-50 p-3 rounded-lg">
//                       <div className="text-2xl font-bold text-green-700">
//                         {Math.round(stats.totalAmount / 1000)}k XOF
//                       </div>
//                       <div className="text-sm text-green-600">Montant total</div>
//                     </div>
//                     <div className="bg-purple-50 p-3 rounded-lg">
//                       <div className="text-2xl font-bold text-purple-700">
//                         {stats.avgRiskScore.toFixed(1)}%
//                       </div>
//                       <div className="text-sm text-purple-600">Risque moyen</div>
//                     </div>
//                   </div>
                  
//                   <div>
//                     <h4 className="font-semibold mb-2">Top villes à risque</h4>
//                     <div className="space-y-2">
//                       {UEMOA_CITIES
//                         .sort((a, b) => b.fraudRate - a.fraudRate)
//                         .slice(0, 3)
//                         .map(city => (
//                           <div 
//                             key={city.name}
//                             className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
//                             onClick={() => handleCityClick(city)}
//                           >
//                             <div>
//                               <div className="font-medium">{city.name.split(',')[0]}</div>
//                               <div className="text-sm text-gray-500">
//                                 {city.frauds} fraudes
//                               </div>
//                             </div>
//                             <Badge variant={
//                               city.fraudRate > 3 ? 'destructive' : 
//                               city.fraudRate > 2.8 ? 'outline' : 'secondary'
//                             }>
//                               {city.fraudRate.toFixed(1)}%
//                             </Badge>
//                           </div>
//                         ))}
//                     </div>
//                   </div>
//                 </TabsContent>
                
//                 <TabsContent value="hotspots" className="space-y-4">
//                   {selectedCity ? (
//                     <div>
//                       <div className="flex items-center justify-between mb-3">
//                         <h4 className="font-semibold">{selectedCity.name}</h4>
//                         <Button 
//                           variant="ghost" 
//                           size="sm"
//                           onClick={() => setSelectedCity(null)}
//                         >
//                           <EyeOff className="h-4 w-4" />
//                         </Button>
//                       </div>
                      
//                       <div className="space-y-3">
//                         <div className="p-3 bg-red-50 rounded-lg">
//                           <div className="text-lg font-bold text-red-700">
//                             Niveau d'alerte: {selectedCity.fraudRate > 3 ? 'ÉLEVÉ' : 'NORMAL'}
//                           </div>
//                           <div className="text-sm text-red-600">
//                             Taux supérieur de {Math.abs(selectedCity.fraudRate - 2.8).toFixed(2)}% à la moyenne
//                           </div>
//                         </div>
                        
//                         <div className="grid grid-cols-2 gap-2">
//                           <div className="p-2 bg-gray-50 rounded">
//                             <div className="font-semibold">{selectedCity.transactions}</div>
//                             <div className="text-xs text-gray-600">Transactions</div>
//                           </div>
//                           <div className="p-2 bg-red-50 rounded">
//                             <div className="font-semibold text-red-700">{selectedCity.frauds}</div>
//                             <div className="text-xs text-red-600">Fraudes</div>
//                           </div>
//                         </div>
                        
//                         <div className="pt-3 border-t">
//                           <h5 className="font-medium mb-2">Recommandations</h5>
//                           <ul className="text-sm space-y-1 text-gray-700">
//                             <li>• Renforcer la vérification KYC</li>
//                             <li>• Surveiller les transactions nocturnes</li>
//                             <li>• Implémenter 2FA pour les montants élevés</li>
//                             <li>• Analyser les patterns de cette région</li>
//                           </ul>
//                         </div>
//                       </div>
//                     </div>
//                   ) : (
//                     <div className="text-center py-8">
//                       <Target className="h-12 w-12 text-gray-300 mx-auto mb-4" />
//                       <p className="text-gray-600">Cliquez sur une ville pour voir les détails</p>
//                       <p className="text-sm text-gray-500 mt-2">
//                         Les hotspots sont mis en évidence en rouge
//                       </p>
//                     </div>
//                   )}
//                 </TabsContent>
//               </Tabs>
//             </div>
//           </div>
//         </CardContent>
//       </Card>
//     </div>
//   );
// };

// // ============================================================================
// // FONCTIONS UTILITAIRES
// // ============================================================================

// function generateMockTransactions(): Transaction[] {
//   const transactions: Transaction[] = [];
//   const types: Transaction['type'][] = ['payment', 'transfer', 'withdrawal', 'cash_in', 'bill_payment'];
//   const statuses: Transaction['status'][] = ['approved', 'blocked', 'pending'];
  
//   // Générer des transactions autour des principales villes
//   UEMOA_CITIES.forEach(city => {
//     for (let i = 0; i < city.transactions; i++) {
//       // Ajouter un peu de variation autour des coordonnées de la ville
//       const lat = city.lat + (Math.random() - 0.5) * 0.5;
//       const lng = city.lng + (Math.random() - 0.5) * 0.5;
      
//       // Générer un score de risque basé sur le taux de fraude de la ville
//       const baseRisk = city.fraudRate * 25; // Convertir taux en score
//       const riskScore = Math.min(100, Math.max(1, baseRisk + (Math.random() - 0.5) * 20));
      
//       transactions.push({
//         id: `mock_${city.name.replace(/\s+/g, '_')}_${i}`,
//         amount: Math.floor(Math.random() * 200000) + 1000,
//         location: city.name,
//         lat,
//         lng,
//         risk_score: riskScore,
//         customer_id: `cust_${Math.floor(Math.random() * 1000)}`,
//         timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
//         type: types[Math.floor(Math.random() * types.length)],
//         status: riskScore > 70 ? 'pending' : statuses[Math.floor(Math.random() * statuses.length)]
//       });
//     }
//   });
  
//   return transactions;
// }

// // Fonction pour corriger les icônes Leaflet (à appeler dans le composant parent)
// export const fixLeafletIcons = () => {
//   // @ts-ignore
//   delete L.Icon.Default.prototype._getIconUrl;
  
//   L.Icon.Default.mergeOptions({
//     iconRetinaUrl: '/leaflet/images/marker-icon-2x.png',
//     iconUrl: '/leaflet/images/marker-icon.png',
//     shadowUrl: '/leaflet/images/marker-shadow.png',
//   });
// };


// import React, { useState, useEffect } from 'react';
// import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
// import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { 
//   MapPin, 
//   Filter, 
//   Target, 
//   AlertTriangle, 
//   TrendingUp,
//   Globe,
//   Eye,
//   Download
// } from 'lucide-react';
// import { fraudService } from '@/services/fraudService';

// // Types pour les données réelles
// interface Transaction {
//   id: string;
//   amount: number;
//   location: string;
//   risk_score: number;
//   customer_id: string;
//   timestamp: string;
//   type: string;
//   status: string;
// }

// interface CityStats {
//   name: string;
//   transactions: number;
//   frauds: number;
//   fraudRate: number;
//   avgAmount: number;
//   totalAmount: number;
// }

// interface RiskMapProps {
//   timeRange?: '24h' | '7d' | '30d';
// }

// export const RiskMap: React.FC<RiskMapProps> = ({ timeRange = '7d' }) => {
//   const [selectedCity, setSelectedCity] = useState<string | null>(null);
//   const [cityStats, setCityStats] = useState<CityStats[]>([]);
//   const [loading, setLoading] = useState(true);
//   const [transactions, setTransactions] = useState<Transaction[]>([]);
  
//   // Villes UEMOA principales avec coordonnées
//   const UEMOA_CITIES = [
//     { name: 'Dakar, Sénégal', lat: 14.7167, lng: -17.4677 },
//     { name: 'Abidjan, Côte d\'Ivoire', lat: 5.3599, lng: -4.0083 },
//     { name: 'Bamako, Mali', lat: 12.6392, lng: -8.0029 },
//     { name: 'Ouagadougou, Burkina Faso', lat: 12.3714, lng: -1.5197 },
//     { name: 'Lomé, Togo', lat: 6.1725, lng: 1.2314 },
//     { name: 'Cotonou, Bénin', lat: 6.3703, lng: 2.3912 },
//     { name: 'Niamey, Niger', lat: 13.5127, lng: 2.1125 },
//     { name: 'Conakry, Guinée', lat: 9.6412, lng: -13.5784 },
//   ];

//   // Charger les transactions depuis l'API
//   useEffect(() => {
//     const loadTransactions = async () => {
//       try {
//         setLoading(true);
        
//         // Appel API pour récupérer les transactions
//         const response = await fraudService.getTransactions({}, { page_size: 1000 });
//         const allTransactions: Transaction[] = response.items || [];
//         setTransactions(allTransactions);
        
//         // Calculer les statistiques par ville
//         const stats = calculateCityStats(allTransactions);
//         setCityStats(stats);
        
//       } catch (error) {
//         console.error('Erreur chargement transactions:', error);
//       } finally {
//         setLoading(false);
//       }
//     };
    
//     loadTransactions();
//   }, [timeRange]);

//   // Calculer les statistiques par ville
//   const calculateCityStats = (transactions: Transaction[]): CityStats[] => {
//     const cityMap = new Map<string, { 
//       transactions: number, 
//       frauds: number, 
//       totalAmount: number,
//       locations: Set<string>
//     }>();
    
//     // Initialiser toutes les villes UEMOA
//     UEMOA_CITIES.forEach(city => {
//       cityMap.set(city.name, { 
//         transactions: 0, 
//         frauds: 0, 
//         totalAmount: 0,
//         locations: new Set()
//       });
//     });
    
//     // Parcourir les transactions
//     transactions.forEach(transaction => {
//       // Trouver la ville correspondante
//       const city = UEMOA_CITIES.find(c => 
//         transaction.location?.toLowerCase().includes(c.name.toLowerCase().split(',')[0]) ||
//         (c.name.toLowerCase().includes('dakar') && transaction.location?.toLowerCase().includes('senegal')) ||
//         (c.name.toLowerCase().includes('abidjan') && transaction.location?.toLowerCase().includes('côte'))
//       );
      
//       if (city) {
//         const cityData = cityMap.get(city.name)!;
//         cityData.transactions++;
//         cityData.totalAmount += transaction.amount;
        
//         // Compter comme fraude si risque élevé
//         if (transaction.risk_score > 70) {
//           cityData.frauds++;
//         }
        
//         cityMap.set(city.name, cityData);
//       }
//     });
    
//     // Convertir en tableau
//     return Array.from(cityMap.entries()).map(([name, data]) => ({
//       name,
//       transactions: data.transactions,
//       frauds: data.frauds,
//       fraudRate: data.transactions > 0 ? (data.frauds / data.transactions) * 100 : 0,
//       avgAmount: data.transactions > 0 ? data.totalAmount / data.transactions : 0,
//       totalAmount: data.totalAmount
//     })).sort((a, b) => b.fraudRate - a.fraudRate);
//   };

//   // Formatage
//   const formatNumber = (num: number) => {
//     return new Intl.NumberFormat('fr-FR').format(num);
//   };

//   const formatCurrency = (amount: number) => {
//     return new Intl.NumberFormat('fr-FR').format(amount) + ' F CFA';
//   };

//   if (loading) {
//     return (
//       <Card className="h-[500px]">
//         <CardContent className="flex items-center justify-center h-full">
//           <div className="text-center space-y-4">
//             <Globe className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
//             <p className="text-gray-600">Chargement des données géographiques...</p>
//           </div>
//         </CardContent>
//       </Card>
//     );
//   }

//   const selectedCityData = selectedCity ? 
//     cityStats.find(city => city.name === selectedCity) : null;

//   // Statistiques globales
//   const totalTransactions = cityStats.reduce((sum, city) => sum + city.transactions, 0);
//   const totalFrauds = cityStats.reduce((sum, city) => sum + city.frauds, 0);
//   const overallFraudRate = totalTransactions > 0 ? (totalFrauds / totalTransactions) * 100 : 0;

//   return (
//     <Card className="h-[500px]">
//       <CardHeader className="pb-3">
//         <div className="flex justify-between items-center">
//           <div>
//             <CardTitle className="flex items-center gap-2">
//               <MapPin className="h-5 w-5 text-red-500" />
//               Carte des Risques Géographiques - Données Réelles
//             </CardTitle>
//             <CardDescription>
//               Analyse des fraudes par ville dans la zone UEMOA
//             </CardDescription>
//           </div>
          
//           <div className="flex items-center gap-2">
//             <Button variant="outline" size="sm">
//               <Download className="h-4 w-4 mr-2" />
//               Exporter
//             </Button>
//           </div>
//         </div>
//       </CardHeader>
      
//       <CardContent className="h-[calc(100%-80px)]">
//         <div className="flex h-full gap-6">
//           {/* Carte simulée avec statistiques */}
//           <div className="flex-1">
//             <div className="h-full bg-gradient-to-br from-blue-50 to-white rounded-lg border p-4">
//               <div className="text-center mb-6">
//                 <Globe className="h-12 w-12 text-blue-500 mx-auto mb-2" />
//                 <h3 className="font-semibold">Répartition Géographique des Risques</h3>
//                 <p className="text-sm text-gray-500">
//                   {totalTransactions} transactions analysées sur {cityStats.length} villes
//                 </p>
//               </div>
              
//               {/* Statistiques principales */}
//               <div className="grid grid-cols-2 gap-3 mb-6">
//                 <div className="bg-blue-50 p-3 rounded-lg">
//                   <div className="text-xl font-bold text-blue-700">
//                     {formatNumber(totalTransactions)}
//                   </div>
//                   <div className="text-sm text-blue-600">Transactions</div>
//                 </div>
//                 <div className="bg-red-50 p-3 rounded-lg">
//                   <div className="text-xl font-bold text-red-700">
//                     {formatNumber(totalFrauds)}
//                   </div>
//                   <div className="text-sm text-red-600">Fraudes détectées</div>
//                 </div>
//                 <div className="bg-orange-50 p-3 rounded-lg">
//                   <div className="text-xl font-bold text-orange-700">
//                     {overallFraudRate.toFixed(2)}%
//                   </div>
//                   <div className="text-sm text-orange-600">Taux global</div>
//                 </div>
//                 <div className="bg-green-50 p-3 rounded-lg">
//                   <div className="text-xl font-bold text-green-700">
//                     {formatCurrency(cityStats.reduce((sum, city) => sum + city.totalAmount, 0))}
//                   </div>
//                   <div className="text-sm text-green-600">Montant total</div>
//                 </div>
//               </div>
              
//               {/* Légende */}
//               <div className="mb-4">
//                 <h4 className="font-semibold mb-2 flex items-center gap-2">
//                   <AlertTriangle className="h-4 w-4" />
//                   Légende des niveaux de risque
//                 </h4>
//                 <div className="flex items-center gap-4 text-sm">
//                   <div className="flex items-center gap-1">
//                     <div className="h-3 w-3 rounded-full bg-red-500"></div>
//                     <span>Élevé (&gt; 3%)</span>
//                   </div>
//                   <div className="flex items-center gap-1">
//                     <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
//                     <span>Moyen (2-3%)</span>
//                   </div>
//                   <div className="flex items-center gap-1">
//                     <div className="h-3 w-3 rounded-full bg-green-500"></div>
//                     <span>Faible (&lt; 2%)</span>
//                   </div>
//                 </div>
//               </div>
              
//               <Button className="w-full" variant="outline">
//                 <Target className="h-4 w-4 mr-2" />
//                 Activer la carte interactive
//               </Button>
//             </div>
//           </div>
          
//           {/* Panneau des villes */}
//           <div className="w-80">
//             <Tabs defaultValue="cities">
//               <TabsList className="grid grid-cols-2 mb-4">
//                 <TabsTrigger value="cities">
//                   <MapPin className="h-4 w-4 mr-2" />
//                   Villes
//                 </TabsTrigger>
//                 <TabsTrigger value="stats">
//                   <TrendingUp className="h-4 w-4 mr-2" />
//                   Statistiques
//                 </TabsTrigger>
//               </TabsList>
              
//               <TabsContent value="cities" className="h-[350px] overflow-y-auto">
//                 <div className="space-y-3">
//                   {cityStats.map((city, index) => (
//                     <div 
//                       key={city.name}
//                       className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
//                         selectedCity === city.name 
//                           ? 'bg-blue-50 border-blue-200' 
//                           : 'bg-white hover:bg-gray-50'
//                       }`}
//                       onClick={() => setSelectedCity(city.name)}
//                     >
//                       <div className="flex justify-between items-start">
//                         <div>
//                           <div className="font-semibold">{city.name.split(',')[0]}</div>
//                           <div className="text-sm text-gray-500">
//                             {city.transactions} transactions
//                           </div>
//                         </div>
//                         <Badge variant={
//                           city.fraudRate > 3 ? "destructive" : 
//                           city.fraudRate > 2 ? "outline" : "secondary"
//                         }>
//                           {city.fraudRate.toFixed(2)}%
//                         </Badge>
//                       </div>
                      
//                       <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
//                         <div className="text-center p-1 bg-gray-50 rounded">
//                           <div className="font-semibold">{city.frauds}</div>
//                           <div className="text-gray-500">Fraudes</div>
//                         </div>
//                         <div className="text-center p-1 bg-gray-50 rounded">
//                           <div className="font-semibold">
//                             {formatCurrency(city.avgAmount)}
//                           </div>
//                           <div className="text-gray-500">Moyenne</div>
//                         </div>
//                         <div className="text-center p-1 bg-gray-50 rounded">
//                           <div className="font-semibold">
//                             {formatNumber(city.totalAmount / 1000)}k
//                           </div>
//                           <div className="text-gray-500">Total</div>
//                         </div>
//                       </div>
//                     </div>
//                   ))}
//                 </div>
//               </TabsContent>
              
//               <TabsContent value="stats" className="space-y-4">
//                 {selectedCityData ? (
//                   <div>
//                     <div className="flex items-center justify-between mb-4">
//                       <h4 className="font-semibold">{selectedCityData.name}</h4>
//                       <Button 
//                         variant="ghost" 
//                         size="sm"
//                         onClick={() => setSelectedCity(null)}
//                       >
//                         <Eye className="h-4 w-4" />
//                       </Button>
//                     </div>
                    
//                     <div className="space-y-3">
//                       <div className="p-3 bg-red-50 rounded-lg">
//                         <div className="text-lg font-bold text-red-700">
//                           {selectedCityData.fraudRate.toFixed(2)}% de fraude
//                         </div>
//                         <div className="text-sm text-red-600">
//                           {selectedCityData.frauds} fraudes sur {selectedCityData.transactions} transactions
//                         </div>
//                       </div>
                      
//                       <div className="grid grid-cols-2 gap-2">
//                         <div className="p-2 bg-blue-50 rounded">
//                           <div className="font-semibold text-blue-700">
//                             {formatCurrency(selectedCityData.avgAmount)}
//                           </div>
//                           <div className="text-xs text-blue-600">Montant moyen</div>
//                         </div>
//                         <div className="p-2 bg-green-50 rounded">
//                           <div className="font-semibold text-green-700">
//                             {formatCurrency(selectedCityData.totalAmount)}
//                           </div>
//                           <div className="text-xs text-green-600">Volume total</div>
//                         </div>
//                       </div>
                      
//                       <div className="pt-3 border-t">
//                         <h5 className="font-medium mb-2">Recommandations</h5>
//                         <ul className="text-sm space-y-1 text-gray-700">
//                           <li>• {selectedCityData.fraudRate > 3 ? 'Renforcer la vérification KYC' : 'Maintenir la surveillance actuelle'}</li>
//                           <li>• Analyser les transactions nocturnes</li>
//                           <li>• Vérifier les changements d'appareil</li>
//                           <li>• Surveiller les montants inhabituels</li>
//                         </ul>
//                       </div>
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="text-center py-8">
//                     <Target className="h-12 w-12 text-gray-300 mx-auto mb-4" />
//                     <p className="text-gray-600">Sélectionnez une ville pour voir les détails</p>
//                     <p className="text-sm text-gray-500 mt-2">
//                       Cliquez sur une ville dans la liste
//                     </p>
//                   </div>
//                 )}
//               </TabsContent>
//             </Tabs>
            
//             {/* Filtres */}
//             <div className="mt-4 pt-4 border-t">
//               <div className="flex items-center justify-between mb-2">
//                 <h4 className="font-semibold flex items-center gap-2">
//                   <Filter className="h-4 w-4" />
//                   Filtres
//                 </h4>
//                 <span className="text-sm text-gray-500">
//                   {transactions.length} transactions
//                 </span>
//               </div>
              
//               <div className="space-y-2">
//                 <Button variant="outline" size="sm" className="w-full justify-start">
//                   <AlertTriangle className="h-4 w-4 mr-2" />
//                   Voir les alertes critiques
//                 </Button>
//                 <Button variant="outline" size="sm" className="w-full justify-start">
//                   <TrendingUp className="h-4 w-4 mr-2" />
//                   Tendances 30 jours
//                 </Button>
//               </div>
//             </div>
//           </div>
//         </div>
//       </CardContent>
//     </Card>
//   );
// };

// // Fonction pour extraire le nom de ville de la localisation
// const extractCityFromLocation = (location: string): string => {
//   if (!location) return 'Inconnue';
  
//   const cityPatterns = [
//     'Dakar', 'Abidjan', 'Bamako', 'Ouagadougou', 
//     'Lomé', 'Cotonou', 'Niamey', 'Conakry',
//     'Accra', 'Lagos', 'Accra', 'Nairobi'
//   ];
  
//   for (const pattern of cityPatterns) {
//     if (location.toLowerCase().includes(pattern.toLowerCase())) {
//       return pattern;
//     }
//   }
  
//   return location.split(',')[0] || 'Autre';
// };


import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import { 
  MapContainer, 
  TileLayer, 
  Marker, 
  Popup, 
  Circle, 
  Polygon, 
  LayersControl,
  ZoomControl,
  ScaleControl,
  useMap,
  useMapEvents
} from 'react-leaflet';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { 
  MapPin, 
  Filter, 
  ZoomIn, 
  ZoomOut, 
  Layers, 
  Target, 
  AlertTriangle, 
  Shield,
  TrendingUp,
  Globe,
  Crosshair,
  Eye,
  EyeOff,
  Download,
  Maximize2,
  Minimize2,
  Database,
  RefreshCw
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

// ============================================================================
// TYPES ET DONNÉES
// ============================================================================

interface Transaction {
  id: string;
  amount: number;
  location: string;
  lat: number;
  lng: number;
  risk_score: number;
  customer_id: string;
  timestamp: string;
  type: 'payment' | 'transfer' | 'withdrawal' | 'cash_in' | 'bill_payment';
  status: 'approved' | 'blocked' | 'pending';
}

interface CityData {
  name: string;
  lat: number;
  lng: number;
  transactions: number;
  frauds: number;
  fraudRate: number;
  avgAmount: number;
  totalAmount: number;
  highRiskTransactions: number;
}

interface RiskMapProps {
  transactions?: Transaction[];
  timeRange?: '24h' | '7d' | '30d';
  onCityClick?: (city: CityData) => void;
  loading?: boolean;
}

// Données par défaut pour les villes UEMOA (utilisées uniquement si pas de données)
const UEMOA_CITIES_DEFAULT: CityData[] = [
  {
    name: 'Dakar, Sénégal',
    lat: 14.7167,
    lng: -17.4677,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Abidjan, Côte d\'Ivoire',
    lat: 5.3599,
    lng: -4.0083,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Bamako, Mali',
    lat: 12.6392,
    lng: -8.0029,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Ouagadougou, Burkina Faso',
    lat: 12.3714,
    lng: -1.5197,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Lomé, Togo',
    lat: 6.1725,
    lng: 1.2314,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Cotonou, Bénin',
    lat: 6.3703,
    lng: 2.3912,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Niamey, Niger',
    lat: 13.5127,
    lng: 2.1125,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  },
  {
    name: 'Conakry, Guinée',
    lat: 9.6412,
    lng: -13.5784,
    transactions: 0,
    frauds: 0,
    fraudRate: 0,
    avgAmount: 0,
    totalAmount: 0,
    highRiskTransactions: 0
  }
];

// ============================================================================
// FONCTIONS UTILITAIRES POUR LES DONNÉES
// ============================================================================

// Fonction pour trouver la ville la plus proche
const findNearestCity = (lat: number, lng: number): string => {
  const cities = UEMOA_CITIES_DEFAULT;
  let nearestCity = cities[0];
  let minDistance = Infinity;
  
  cities.forEach(city => {
    const distance = Math.sqrt(
      Math.pow(lat - city.lat, 2) + Math.pow(lng - city.lng, 2)
    );
    if (distance < minDistance) {
      minDistance = distance;
      nearestCity = city;
    }
  });
  
  return nearestCity.name;
};

// Fonction pour calculer les statistiques par ville à partir des transactions
const calculateCityStats = (transactions: Transaction[]): CityData[] => {
  if (!transactions.length) {
    console.log("Aucune transaction disponible");
    return UEMOA_CITIES_DEFAULT;
  }
  
  console.log(`Calcul des stats pour ${transactions.length} transactions`);
  
  // Grouper les transactions par localisation
  const locationMap = new Map<string, Transaction[]>();
  
  transactions.forEach(tx => {
    // Nettoyer et normaliser le nom de la localisation
    let locationName = tx.location || 'Localisation inconnue';
    
    // Si la localisation contient des coordonnées, utiliser une clé générique
    if (locationName.includes(',') && !isNaN(parseFloat(locationName.split(',')[0]))) {
      // C'est probablement des coordonnées, utiliser une ville proche
      locationName = findNearestCity(tx.lat, tx.lng);
    }
    
    if (!locationMap.has(locationName)) {
      locationMap.set(locationName, []);
    }
    locationMap.get(locationName)!.push(tx);
  });
  
  console.log(`${locationMap.size} localisations trouvées`);
  
  // Calculer les statistiques pour chaque localisation
  const cityStats: CityData[] = [];
  
  locationMap.forEach((cityTransactions, locationName) => {
    if (cityTransactions.length === 0) return;
    
    // Utiliser les coordonnées de la première transaction
    const firstTx = cityTransactions[0];
    let avgLat = firstTx.lat || 0;
    let avgLng = firstTx.lng || 0;
    
    // Si plusieurs transactions, calculer la moyenne
    if (cityTransactions.length > 1) {
      avgLat = cityTransactions.reduce((sum, tx) => sum + (tx.lat || 0), 0) / cityTransactions.length;
      avgLng = cityTransactions.reduce((sum, tx) => sum + (tx.lng || 0), 0) / cityTransactions.length;
    }
    
    // Compter les fraudes (risque > 70)
    const frauds = cityTransactions.filter(tx => tx.risk_score > 70).length;
    const highRiskTransactions = cityTransactions.filter(tx => tx.risk_score > 70).length;
    
    // Calculer les montants
    const totalAmount = cityTransactions.reduce((sum, tx) => sum + tx.amount, 0);
    const avgAmount = totalAmount / cityTransactions.length;
    
    // Calculer le taux de fraude
    const fraudRate = cityTransactions.length > 0 ? (frauds / cityTransactions.length) * 100 : 0;
    
    cityStats.push({
      name: locationName,
      lat: avgLat,
      lng: avgLng,
      transactions: cityTransactions.length,
      frauds,
      fraudRate,
      avgAmount,
      totalAmount,
      highRiskTransactions
    });
  });
  
  // Trier par nombre de transactions (décroissant)
  const sortedStats = cityStats.sort((a, b) => b.transactions - a.transactions);
  
  console.log(`Stats calculées: ${sortedStats.length} villes`);
  sortedStats.forEach(city => {
    console.log(`${city.name}: ${city.transactions} tx, ${city.frauds} fraudes, ${city.fraudRate.toFixed(2)}%`);
  });
  
  return sortedStats;
};

// Fonction pour calculer les statistiques globales
const calculateGlobalStats = (transactions: Transaction[]) => {
  const totalTransactions = transactions.length;
  const highRiskTransactions = transactions.filter(tx => tx.risk_score > 70).length;
  const totalAmount = transactions.reduce((sum, tx) => sum + tx.amount, 0);
  const avgRiskScore = totalTransactions > 0 
    ? transactions.reduce((sum, tx) => sum + tx.risk_score, 0) / totalTransactions
    : 0;
  
  return {
    totalTransactions,
    highRiskTransactions,
    totalAmount,
    avgRiskScore
  };
};

// ============================================================================
// COMPOSANTS LEAFLET PERSONNALISÉS
// ============================================================================

// Composant pour centrer la carte sur une position
function CenterMap({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView([lat, lng], map.getZoom());
  }, [lat, lng, map]);
  
  return null;
}

// Composant pour les contrôles personnalisés
function CustomControls({ 
  onToggleHeatmap, 
  showHeatmap,
  onRefresh,
  isLoading 
}: { 
  onToggleHeatmap: () => void; 
  showHeatmap: boolean;
  onRefresh: () => void;
  isLoading: boolean;
}) {
  const map = useMap();
  
  return (
    <div className="leaflet-top leaflet-right">
      <div className="leaflet-control leaflet-bar bg-white rounded-lg shadow-lg p-2 space-y-2">
        <button
          className="p-2 hover:bg-gray-100 rounded"
          onClick={() => map.zoomIn()}
          title="Zoom in"
          disabled={isLoading}
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          className="p-2 hover:bg-gray-100 rounded"
          onClick={() => map.zoomOut()}
          title="Zoom out"
          disabled={isLoading}
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <button
          className="p-2 hover:bg-gray-100 rounded"
          onClick={() => map.locate({setView: true})}
          title="Localiser"
          disabled={isLoading}
        >
          <Crosshair className="h-4 w-4" />
        </button>
        <button
          className={`p-2 rounded ${showHeatmap ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'}`}
          onClick={onToggleHeatmap}
          title="Heatmap"
          disabled={isLoading}
        >
          <Layers className="h-4 w-4" />
        </button>
        <button
          className="p-2 hover:bg-gray-100 rounded"
          onClick={onRefresh}
          title="Actualiser les données"
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </div>
  );
}

// Heatmap Layer
function HeatmapLayer({ transactions, show }: { transactions: Transaction[]; show: boolean }) {
  const map = useMap();
  
  useEffect(() => {
    if (!show || !transactions.length) return;
    
    // Filtrer les transactions à risque pour la heatmap
    const highRiskTransactions = transactions.filter(tx => tx.risk_score > 30);
    
    if (highRiskTransactions.length === 0) return;
    
    // @ts-ignore - leaflet.heat n'a pas de types officiels
    const heatLayer = L.heatLayer(
      highRiskTransactions.map(tx => [tx.lat || 0, tx.lng || 0, tx.risk_score / 100]),
      {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        gradient: {
          0.1: '#00ff00',
          0.3: '#ffff00',
          0.6: '#ffa500',
          0.8: '#ff4500',
          1.0: '#ff0000'
        }
      }
    ).addTo(map);
    
    return () => {
      map.removeLayer(heatLayer);
    };
  }, [transactions, show, map]);
  
  return null;
}

// ============================================================================
// ICÔNES PERSONNALISÉES POUR LES MARQUEURS
// ============================================================================

const createCustomIcon = (riskScore: number) => {
  const size = 32;
  const color = riskScore > 70 ? '#ef4444' : riskScore > 30 ? '#f59e0b' : '#10b981';
  
  return L.divIcon({
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border: 2px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        cursor: pointer;
      ">
        ${Math.round(riskScore)}%
      </div>
    `,
    className: 'custom-marker',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

// ============================================================================
// COMPOSANT PRINCIPAL
// ============================================================================

export const RiskMap: React.FC<RiskMapProps> = ({
  transactions = [],
  timeRange = '7d',
  onCityClick,
  loading = false
}) => {
  const [selectedCity, setSelectedCity] = useState<CityData | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showMarkers, setShowMarkers] = useState(true);
  const [showClusters, setShowClusters] = useState(true);
  const [riskThreshold, setRiskThreshold] = useState([30]);
  const [mapView, setMapView] = useState<'streets' | 'satellite' | 'light'>('streets');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const mapRef = useRef<any>(null);
  
  // Position initiale (centre de l'UEMOA)
  const centerPosition: [number, number] = [10.0, -5.0];
  const defaultZoom = 5;
  
  // DEBUG: Afficher les informations sur les données
  useEffect(() => {
    console.log("RiskMap - Données reçues:", {
      totalTransactions: transactions.length,
      hasCoords: transactions.filter(t => t.lat && t.lng).length,
      riskScores: transactions.map(t => t.risk_score),
      locations: [...new Set(transactions.map(t => t.location || 'Inconnu'))]
    });
  }, [transactions]);
  
  // Calculer les statistiques des villes
  const displayCities = useMemo(() => {
    const cities = calculateCityStats(transactions);
    console.log("Villes calculées:", cities);
    return cities;
  }, [transactions]);
  
  // Filtrer les transactions par seuil de risque
  const filteredTransactions = useMemo(() => {
    return transactions.filter(tx => tx.risk_score >= riskThreshold[0]);
  }, [transactions, riskThreshold]);
  
  // Calculer les statistiques globales
  const stats = useMemo(() => {
    return calculateGlobalStats(transactions);
  }, [transactions]);
  
  // Gestion du clic sur une ville
  const handleCityClick = useCallback((city: CityData) => {
    setSelectedCity(city);
    onCityClick?.(city);
    
    if (mapRef.current) {
      mapRef.current.setView([city.lat, city.lng], 10);
    }
  }, [onCityClick]);
  
  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  // Exporter la carte
  const exportMap = () => {
    const data = {
      cities: displayCities,
      stats,
      timestamp: new Date().toISOString(),
      transactionCount: transactions.length
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentra-risk-map-${format(new Date(), 'yyyy-MM-dd')}.json`;
    a.click();
  };
  
  // Rafraîchir les données
  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simuler un rafraîchissement
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };
  
  // Afficher le chargement
  if (loading || isRefreshing) {
    return (
      <Card className="h-[500px]">
        <CardContent className="flex flex-col items-center justify-center h-full">
          <div className="text-center space-y-4">
            <div className="animate-spin">
              <RefreshCw className="h-12 w-12 text-blue-500" />
            </div>
            <p className="text-gray-600">Chargement des données de la base...</p>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Database className="h-4 w-4" />
              <span>{transactions.length} transactions chargées</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white p-4' : ''}`}>
      <Card className={`${isFullscreen ? 'h-full' : 'h-full min-h-[450px]'}`}>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-red-500" />
                Carte des Risques Géographiques
              </CardTitle>
              <CardDescription className="flex items-center gap-2">
                <Database className="h-4 w-4 text-green-600" />
                Données en direct de la base - {transactions.length} transactions analysées
              </CardDescription>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={toggleFullscreen}
              >
                {isFullscreen ? (
                  <Minimize2 className="h-4 w-4 mr-2" />
                ) : (
                  <Maximize2 className="h-4 w-4 mr-2" />
                )}
                {isFullscreen ? 'Réduire' : 'Plein écran'}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={exportMap}
              >
                <Download className="h-4 w-4 mr-2" />
                Exporter
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="h-[calc(100%-80px)] p-0">
          <div className="flex h-full">
            {/* Carte Leaflet */}
            <div className="flex-1 relative">
              <MapContainer
                center={centerPosition}
                zoom={defaultZoom}
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
                ref={mapRef}
                className="rounded-lg"
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url={
                    mapView === 'satellite' 
                      ? 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
                      : mapView === 'light'
                      ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
                      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                  }
                />
                
                {/* Heatmap des transactions */}
                <HeatmapLayer 
                  transactions={filteredTransactions} 
                  show={showHeatmap} 
                />
                
                {/* Marqueurs pour les villes */}
                {showMarkers && displayCities.length > 0 ? (
                  displayCities.map((city, index) => {
                    // S'assurer que les coordonnées sont valides
                    if (isNaN(city.lat) || isNaN(city.lng) || city.lat === 0 || city.lng === 0) {
                      console.warn(`Coordonnées invalides pour ${city.name}:`, city.lat, city.lng);
                      return null;
                    }
                    
                    // Calculer le score de risque basé sur le taux de fraude
                    const riskScore = Math.min(100, Math.max(1, city.fraudRate * 10));
                    const icon = createCustomIcon(riskScore);
                    
                    return (
                      <Marker
                        key={`city-${index}`}
                        position={[city.lat, city.lng]}
                        icon={icon}
                        eventHandlers={{
                          click: () => handleCityClick(city)
                        }}
                      >
                        <Popup>
                          <div className="p-2 min-w-[220px]">
                            <h3 className="font-bold text-lg mb-2">{city.name}</h3>
                            <div className="space-y-2">
                              <div className="flex justify-between items-center">
                                <span className="text-gray-600">Transactions:</span>
                                <span className="font-semibold">{city.transactions.toLocaleString('fr-FR')}</span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-gray-600">Fraudes détectées:</span>
                                <Badge variant={city.frauds > 0 ? "destructive" : "outline"}>
                                  {city.frauds}
                                </Badge>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-gray-600">Taux de fraude:</span>
                                <span className={`font-semibold ${city.fraudRate > 3 ? 'text-red-600' : 'text-green-600'}`}>
                                  {city.fraudRate.toFixed(2)}%
                                </span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-gray-600">Montant total:</span>
                                <span className="font-semibold">
                                  {new Intl.NumberFormat('fr-FR').format(city.totalAmount)} XOF
                                </span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-gray-600">Montant moyen:</span>
                                <span className="font-semibold">
                                  {new Intl.NumberFormat('fr-FR').format(Math.round(city.avgAmount))} XOF
                                </span>
                              </div>
                            </div>
                            <Button 
                              size="sm" 
                              className="w-full mt-4"
                              onClick={() => handleCityClick(city)}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              Voir les détails
                            </Button>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }).filter(Boolean)
                ) : (
                  // Message si pas de marqueurs
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center z-10">
                    <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                    <div className="bg-white/90 backdrop-blur-sm p-4 rounded-lg shadow-lg">
                      <p className="text-gray-700">Aucune donnée géographique disponible</p>
                      <p className="text-sm text-gray-500 mt-2">
                        {transactions.length} transactions sans coordonnées précises
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Contrôles personnalisés */}
                <CustomControls 
                  onToggleHeatmap={() => setShowHeatmap(!showHeatmap)} 
                  showHeatmap={showHeatmap}
                  onRefresh={handleRefresh}
                  isLoading={isRefreshing}
                />
                <ZoomControl position="bottomright" />
                <ScaleControl position="bottomleft" />
              </MapContainer>
              
              {/* Légende */}
              <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-xs">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <Layers className="h-4 w-4" />
                  Légende
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-red-500"></div>
                    <span className="text-sm">Risque élevé (&gt; 70%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                    <span className="text-sm">Risque moyen (30-70%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-green-500"></div>
                    <span className="text-sm">Risque faible (&lt; 30%)</span>
                  </div>
                  {showHeatmap && (
                    <div className="mt-2 pt-2 border-t">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Intensité heatmap:</span>
                        <span className="text-xs text-gray-500">Risque ↑</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 mt-1"></div>
                    </div>
                  )}
                  <div className="mt-2 pt-2 border-t text-xs text-gray-500">
                    <div className="flex items-center justify-between">
                      <span>Villes: {displayCities.length}</span>
                      <span>Tx: {stats.totalTransactions.toLocaleString('fr-FR')}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Panneau de contrôle */}
            <div className="w-80 border-l p-4 overflow-y-auto">
              <Tabs defaultValue="controls">
                <TabsList className="grid grid-cols-3 mb-4">
                  <TabsTrigger value="controls">
                    <Layers className="h-4 w-4 mr-2" />
                    Contrôles
                  </TabsTrigger>
                  <TabsTrigger value="stats">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Stats
                  </TabsTrigger>
                  <TabsTrigger value="hotspots">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Hotspots
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="controls" className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <Filter className="h-4 w-4" />
                      Filtres
                    </h4>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Seuil de risque: {riskThreshold[0]}%
                        </label>
                        <Slider
                          value={riskThreshold}
                          onValueChange={setRiskThreshold}
                          min={0}
                          max={100}
                          step={5}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="text-sm">Heatmap</label>
                          <Switch
                            checked={showHeatmap}
                            onCheckedChange={setShowHeatmap}
                          />
                        </div>
                        <div className="flex items-center justify-between">
                          <label className="text-sm">Marqueurs</label>
                          <Switch
                            checked={showMarkers}
                            onCheckedChange={setShowMarkers}
                          />
                        </div>
                        <div className="flex items-center justify-between">
                          <label className="text-sm">Clusters</label>
                          <Switch
                            checked={showClusters}
                            onCheckedChange={setShowClusters}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Vue de la carte</h4>
                    <div className="grid grid-cols-3 gap-2">
                      <Button
                        variant={mapView === 'streets' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setMapView('streets')}
                      >
                        Rues
                      </Button>
                      <Button
                        variant={mapView === 'satellite' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setMapView('satellite')}
                      >
                        Satellite
                      </Button>
                      <Button
                        variant={mapView === 'light' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setMapView('light')}
                      >
                        Clair
                      </Button>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Centrer sur</h4>
                    <div className="space-y-2">
                      {displayCities.slice(0, 4).map(city => (
                        <Button
                          key={city.name}
                          variant="outline"
                          size="sm"
                          className="w-full justify-start"
                          onClick={() => handleCityClick(city)}
                        >
                          <MapPin className="h-4 w-4 mr-2" />
                          {city.name.split(',')[0]}
                          <Badge className="ml-auto" variant={
                            city.fraudRate > 3 ? 'destructive' : 'outline'
                          }>
                            {city.transactions}
                          </Badge>
                        </Button>
                      ))}
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="stats" className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-blue-700">
                        {stats.totalTransactions.toLocaleString('fr-FR')}
                      </div>
                      <div className="text-sm text-blue-600">Transactions</div>
                    </div>
                    <div className="bg-red-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-red-700">
                        {stats.highRiskTransactions}
                      </div>
                      <div className="text-sm text-red-600">À haut risque</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-green-700">
                        {Math.round(stats.totalAmount / 1000)}k XOF
                      </div>
                      <div className="text-sm text-green-600">Montant total</div>
                    </div>
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-purple-700">
                        {stats.avgRiskScore.toFixed(1)}%
                      </div>
                      <div className="text-sm text-purple-600">Risque moyen</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Top villes à risque</h4>
                    <div className="space-y-2">
                      {displayCities
                        .sort((a, b) => b.fraudRate - a.fraudRate)
                        .slice(0, 3)
                        .map(city => (
                          <div 
                            key={city.name}
                            className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
                            onClick={() => handleCityClick(city)}
                          >
                            <div>
                              <div className="font-medium">{city.name.split(',')[0]}</div>
                              <div className="text-sm text-gray-500">
                                {city.transactions} transactions
                              </div>
                            </div>
                            <div className="flex flex-col items-end">
                              <Badge variant={
                                city.fraudRate > 3 ? 'destructive' : 
                                city.fraudRate > 2.5 ? 'outline' : 'secondary'
                              }>
                                {city.fraudRate.toFixed(1)}%
                              </Badge>
                              <div className="text-xs text-gray-500 mt-1">
                                {city.frauds} fraudes
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Données source:</span>
                      <span className="font-medium">Base de données</span>
                    </div>
                    <div className="flex items-center justify-between text-sm mt-1">
                      <span className="text-gray-600">Dernière mise à jour:</span>
                      <span>{format(new Date(), 'HH:mm', { locale: fr })}</span>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="hotspots" className="space-y-4">
                  {selectedCity ? (
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold">{selectedCity.name}</h4>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => setSelectedCity(null)}
                        >
                          <EyeOff className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <div className="space-y-3">
                        <div className={`p-3 rounded-lg ${
                          selectedCity.fraudRate > 3 
                            ? 'bg-red-50 border border-red-200' 
                            : selectedCity.fraudRate > 2.5
                            ? 'bg-orange-50 border border-orange-200'
                            : 'bg-green-50 border border-green-200'
                        }`}>
                          <div className={`text-lg font-bold ${
                            selectedCity.fraudRate > 3 
                              ? 'text-red-700' 
                              : selectedCity.fraudRate > 2.5
                              ? 'text-orange-700'
                              : 'text-green-700'
                          }`}>
                            Niveau d'alerte: {selectedCity.fraudRate > 3 ? 'ÉLEVÉ' : selectedCity.fraudRate > 2.5 ? 'MOYEN' : 'FAIBLE'}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {selectedCity.fraudRate > 2.5 ? (
                              `Taux supérieur de ${Math.abs(selectedCity.fraudRate - 2.5).toFixed(2)}% à la moyenne`
                            ) : (
                              "Taux dans la normale"
                            )}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2">
                          <div className="p-2 bg-gray-50 rounded">
                            <div className="font-semibold">{selectedCity.transactions}</div>
                            <div className="text-xs text-gray-600">Transactions</div>
                          </div>
                          <div className="p-2 bg-red-50 rounded">
                            <div className="font-semibold text-red-700">{selectedCity.frauds}</div>
                            <div className="text-xs text-red-600">Fraudes</div>
                          </div>
                          <div className="p-2 bg-blue-50 rounded">
                            <div className="font-semibold text-blue-700">
                              {Math.round(selectedCity.totalAmount / 1000)}k XOF
                            </div>
                            <div className="text-xs text-blue-600">Montant total</div>
                          </div>
                          <div className="p-2 bg-green-50 rounded">
                            <div className="font-semibold text-green-700">
                              {Math.round(selectedCity.avgAmount).toLocaleString('fr-FR')}
                            </div>
                            <div className="text-xs text-green-600">Moyenne/tx</div>
                          </div>
                        </div>
                        
                        <div className="pt-3 border-t">
                          <h5 className="font-medium mb-2 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            Recommandations
                          </h5>
                          <ul className="text-sm space-y-1 text-gray-700">
                            {selectedCity.fraudRate > 3 ? (
                              <>
                                <li>• 🔴 Renforcer la vérification KYC immédiatement</li>
                                <li>• 🔴 Mettre en place une surveillance 24/7</li>
                                <li>• 🔴 Analyser tous les clients de cette région</li>
                                <li>• 🔴 Contacter les autorités locales</li>
                              </>
                            ) : selectedCity.fraudRate > 2.5 ? (
                              <>
                                <li>• 🟡 Augmenter les vérifications aléatoires</li>
                                <li>• 🟡 Surveiller les transactions nocturnes</li>
                                <li>• 🟡 Implémenter 2FA pour les montants élevés</li>
                                <li>• 🟡 Analyser les patterns spécifiques</li>
                              </>
                            ) : (
                              <>
                                <li>• 🟢 Maintenir la surveillance actuelle</li>
                                <li>• 🟢 Continuer les vérifications standards</li>
                                <li>• 🟢 Surveiller les tendances émergentes</li>
                                <li>• 🟢 Documenter les bonnes pratiques</li>
                              </>
                            )}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Target className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-600">Cliquez sur une ville pour voir les détails</p>
                      <p className="text-sm text-gray-500 mt-2">
                        {displayCities.length} villes analysées
                      </p>
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center gap-2 text-sm">
                          <Database className="h-4 w-4 text-blue-600" />
                          <span>Données en temps réel de la base</span>
                        </div>
                      </div>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Fonction pour corriger les icônes Leaflet
export const fixLeafletIcons = () => {
  // @ts-ignore
  delete L.Icon.Default.prototype._getIconUrl;
  
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: '/leaflet/images/marker-icon-2x.png',
    iconUrl: '/leaflet/images/marker-icon.png',
    shadowUrl: '/leaflet/images/marker-shadow.png',
  });
};
