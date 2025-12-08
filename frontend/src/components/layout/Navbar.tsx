/**
 * Navbar - Barre de navigation supérieure
 */

import { Shield, Bell, User, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <nav className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-4 h-16">
        {/* Left: Logo + Menu Button */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuClick}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* <div className="flex items-center gap-2">
            <div className="p-2 bg-primary-600 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            {/* <div className="hidden sm:block"> */}
              {/* <h1 className="text-lg font-bold text-gray-900">SÉNTRA</h1>
              <p className="text-xs text-gray-500">Fraud Detection</p> */}
            {/* </div> */}
          {/* </div> */} 
        </div>

        {/* Right: Notifications + User */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              3
            </Badge>
          </Button>

          {/* User Menu */}
          <Button variant="ghost" className="gap-2">
            <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
              <User className="h-4 w-4 text-primary-600" />
            </div>
            <span className="hidden md:inline text-sm font-medium">Admin</span>
          </Button>
        </div>
      </div>
    </nav>
  );
}
