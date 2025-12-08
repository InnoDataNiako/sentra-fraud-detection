// /**
//  * DashboardLayout - Layout principal de l'application
//  */

// import { useState } from 'react';
// import { Outlet } from 'react-router-dom';
// import { Navbar } from '@/components/layout/Navbar';
// import { Sidebar } from '@/components/layout/Sidebar';

// export function DashboardLayout() {
//   const [isSidebarOpen, setIsSidebarOpen] = useState(false);

//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* Navbar */}
//       <Navbar onMenuClick={() => setIsSidebarOpen(true)} />

//       <div className="flex">
//         {/* Sidebar */}
//         <Sidebar
//           isOpen={isSidebarOpen}
//           onClose={() => setIsSidebarOpen(false)}
//         />

//         {/* Main Content */}
//         <main className="flex-1 p-6 lg:p-8 overflow-auto">
//           <div className="max-w-7xl mx-auto">
//             <Outlet />
//           </div>
//         </main>
//       </div>
//     </div>
//   );
// }

/**
 * DashboardLayout - Layout principal de l'application
 */

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export function DashboardLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar fixe */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Container pour Navbar + Content avec margin-left pour la sidebar */}
      <div className="lg:ml-64">
        {/* Navbar */}
        <Navbar onMenuClick={() => setIsSidebarOpen(true)} />

        {/* Main Content */}
        <main className="p-6 lg:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}