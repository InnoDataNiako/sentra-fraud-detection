// src/utils/leaflet-fix.ts
import L from 'leaflet';

export const fixLeafletIcons = () => {
  try {
    // Supprime la méthode par défaut
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    
    // Configure les chemins des icônes
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: '/leaflet/images/marker-icon-2x.png',
      iconUrl: '/leaflet/images/marker-icon.png',
      shadowUrl: '/leaflet/images/marker-shadow.png',
    });
    
    console.log('✅ Leaflet icons fixed successfully');
  } catch (error) {
    console.warn('⚠️ Could not fix Leaflet icons (maybe not installed yet):', error);
  }
};