// /**
//  * Sidebar - Menu latéral de navigation
//  */

// import { NavLink } from 'react-router-dom';
// import {
//   LayoutDashboard,
//   Search,
//   History,
//   BarChart3,
//   Settings,
//   X,
// } from 'lucide-react';
// import { Button } from '@/components/ui/button';
// import { cn } from '@/lib/utils';

// interface SidebarProps {
//   isOpen: boolean;
//   onClose: () => void;
// }

// const menuItems = [
//   {
//     title: 'Dashboard',
//     icon: LayoutDashboard,
//     path: '/',
//   },
//   {
//     title: 'Détection',
//     icon: Search,
//     path: '/detection',
//   },
//   {
//     title: 'Historique',
//     icon: History,
//     path: '/history',
//   },
//   {
//     title: 'Analytics',
//     icon: BarChart3,
//     path: '/analytics',
//   },
//   {
//     title: 'Paramètres',
//     icon: Settings,
//     path: '/settings',
//   },
// ];

// export function Sidebar({ isOpen, onClose }: SidebarProps) {
//   return (
//     <>
//       {/* Overlay mobile */}
//       {isOpen && (
//         <div
//           className="fixed inset-0 bg-black/50 z-40 lg:hidden"
//           onClick={onClose}
//         />
//       )}

//       {/* Sidebar */}
//       <aside
//         className={cn(
//           'fixed top-0 left-0 z-50 h-screen w-64 bg-white border-r border-gray-200',
//           'transform transition-transform duration-300 ease-in-out',
//           'lg:translate-x-0 lg:static',
//           isOpen ? 'translate-x-0' : '-translate-x-full'
//         )}
//       >
//         {/* Close button mobile */}
//         <div className="flex items-center justify-between p-4 border-b lg:hidden">
//           <span className="font-semibold text-gray-900">Menu</span>
//           <Button variant="ghost" size="icon" onClick={onClose}>
//             <X className="h-5 w-5" />
//           </Button>
//         </div>

//         {/* Navigation */}
//         <nav className="p-4 space-y-1">
//           {menuItems.map((item) => (
//             <NavLink
//               key={item.path}
//               to={item.path}
//               onClick={onClose}
//               className={({ isActive }) =>
//                 cn(
//                   'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
//                   'hover:bg-gray-100',
//                   isActive
//                     ? 'bg-primary-50 text-primary-700'
//                     : 'text-gray-700'
//                 )
//               }
//             >
//               <item.icon className="h-5 w-5" />
//               {item.title}
//             </NavLink>
//           ))}
//         </nav>

//         {/* Footer */}
//         <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
//           <div className="bg-gray-50 rounded-lg p-3">
//             <p className="text-xs text-gray-600">Version 1.0.0</p>
//             <p className="text-xs text-gray-500 mt-1">
//               © 2025 SÉNTRA
//             </p>
//           </div>
//         </div>
//       </aside>
//     </>
//   );
// }


/**
 * Sidebar - Menu latéral de navigation (VERSION FIXE)
 */

// import { NavLink } from 'react-router-dom';
// import {
//   LayoutDashboard,
//   Search,
//   History,
//   BarChart3,
//   Settings,
//   X,
//   Shield,
// } from 'lucide-react';
// import { Button } from '@/components/ui/button';
// import { cn } from '@/lib/utils';

// interface SidebarProps {
//   isOpen: boolean;
//   onClose: () => void;
// }

// const menuItems = [
//   {
//     title: 'Dashboard',
//     icon: LayoutDashboard,
//     path: '/',
//   },
//   {
//     title: 'Détection',
//     icon: Search,
//     path: '/detection',
//   },
//   {
//     title: 'Historique',
//     icon: History,
//     path: '/history',
//   },
//   {
//     title: 'Analytics',
//     icon: BarChart3,
//     path: '/analytics',
//   },
//   {
//     title: 'Paramètres',
//     icon: Settings,
//     path: '/settings',
//   },
// ];

// export function Sidebar({ isOpen, onClose }: SidebarProps) {
//   return (
//     <>
//       {/* Overlay mobile */}
//       {isOpen && (
//         <div
//           className="fixed inset-0 bg-black/50 z-40 lg:hidden"
//           onClick={onClose}
//         />
//       )}

//       {/* Sidebar - TOUJOURS FIXE */}
//       <aside
//         className={cn(
//           // ✅ FIXED sur tous les écrans
//           'fixed top-0 left-0 z-50 h-screen w-64 bg-white border-r border-gray-200',
//           'transform transition-transform duration-300 ease-in-out',
//           'overflow-y-auto', // Scroll si contenu trop long
//           // Mobile: slide in/out
//           'lg:translate-x-0',
//           isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
//         )}
//       >
//         {/* Header avec logo */}
//         <div className="flex items-center justify-between p-4 border-b">
//           <div className="flex items-center gap-2">
//             <Shield className="h-6 w-6 text-blue-600" />
//             <span className="font-bold text-gray-900">SÉNTRA</span>
//           </div>
//           {/* Close button mobile uniquement */}
//           <Button variant="ghost" size="icon" onClick={onClose} className="lg:hidden">
//             <X className="h-5 w-5" />
//           </Button>
//         </div>

//         {/* Navigation */}
//         <nav className="p-4 space-y-1">
//           {menuItems.map((item) => (
//             <NavLink
//               key={item.path}
//               to={item.path}
//               onClick={onClose}
//               className={({ isActive }) =>
//                 cn(
//                   'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
//                   'hover:bg-gray-100',
//                   isActive
//                     ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-600'
//                     : 'text-gray-700'
//                 )
//               }
//             >
//               <item.icon className="h-5 w-5" />
//               {item.title}
//             </NavLink>
//           ))}
//         </nav>

//         {/* Footer */}
//         <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-white">
//           <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3">
//             <p className="text-xs font-semibold text-gray-700">SÉNTRA v1.0.0</p>
//             <p className="text-xs text-gray-500 mt-1">
//               Système de détection de fraude
//             </p>
//             <p className="text-xs text-gray-400 mt-1">
//               © 2025 BCEAO
//             </p>
//           </div>
//         </div>
//       </aside>
//     </>
//   );
// }


/**
 * Sidebar - Menu latéral de navigation AVEC logo (VERSION PRO)
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  History,
  BarChart3,
  Settings,
  X,
  Shield,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  {
    title: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
  },
  {
    title: 'Détection',
    icon: Search,
    path: '/detection',
  },
  {
    title: 'Historique',
    icon: History,
    path: '/history',
  },
  {
    title: 'Analytics',
    icon: BarChart3,
    path: '/analytics',
  },
  {
    title: 'Paramètres',
    icon: Settings,
    path: '/settings',
  },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Overlay mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar - TOUJOURS FIXE */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-screen w-64 bg-white border-r border-gray-200',
          'transform transition-transform duration-300 ease-in-out',
          'overflow-y-auto flex flex-col',
          // Mobile: slide in/out
          'lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Header avec LOGO SÉNTRA */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-gray-900">SÉNTRA</h1>
              <p className="text-xs text-gray-500">Détection de fraude</p>
            </div>
          </div>
          
          {/* Close button mobile uniquement */}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onClose} 
            className="lg:hidden hover:bg-blue-100"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation - flex-1 pour prendre l'espace disponible */}
        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
                  'hover:bg-gray-100 hover:translate-x-1',
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-600 shadow-sm'
                    : 'text-gray-700'
                )
              }
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {item.title}
            </NavLink>
          ))}
        </nav>

        {/* Footer - Informations système */}
        <div className="p-4 border-t bg-gray-50">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-3 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <p className="text-xs font-semibold text-gray-700">Système actif</p>
            </div>
            <p className="text-xs text-gray-600">Version 1.0.0</p>
            <p className="text-xs text-gray-500 mt-1">© 2025 BCEAO</p>
          </div>
        </div>
      </aside>
    </>
  );
}