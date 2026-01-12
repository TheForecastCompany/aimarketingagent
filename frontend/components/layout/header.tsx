'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Bell, 
  Search, 
  User, 
  LogOut,
  HelpCircle,
  Sun,
  Moon
} from 'lucide-react';
import { useUI, useProcessing } from '@/hooks/use-app-store';

interface HeaderProps {
  className?: string;
}

export function Header({ className }: HeaderProps) {
  const { darkMode, toggleDarkMode } = useUI();
  const { isProcessing, currentStep, progress } = useProcessing();
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header className={cn('sticky top-0 z-40 glass border-b border-border/50', className)}>
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <div className="hidden lg:flex lg:items-center lg:space-x-2">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search results..."
                className="h-10 w-80 rounded-xl border border-input bg-background/50 backdrop-blur-sm pl-10 pr-4 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-all duration-200"
              />
            </div>
          </div>
        </div>

        {/* Center - Processing Status */}
        {isProcessing && (
          <div className="hidden md:flex items-center space-x-3 px-4 py-2 glass rounded-xl">
            <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-primary-foreground">
                {currentStep}
              </span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-24 h-1 bg-primary/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <span className="text-xs text-primary-foreground/80">
                  {progress}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Right side */}
        <div className="flex items-center space-x-2">
          {/* Dark mode toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleDarkMode}
            className="h-9 w-9 hover:bg-muted/50 transition-colors duration-200"
          >
            {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* Notifications */}
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowNotifications(!showNotifications)}
              className="h-9 w-9 hover:bg-muted/50 transition-colors duration-200"
            >
              <Bell className="h-4 w-4" />
              <Badge className="absolute -top-1 -right-1 h-4 w-4 rounded-full p-0 text-xs">
                3
              </Badge>
            </Button>
            
            {showNotifications && (
              <div className="absolute right-0 top-12 w-80 glass rounded-xl border border-border/50 shadow-xl p-4 z-50">
                <h3 className="font-semibold mb-3">Notifications</h3>
                <div className="space-y-2">
                  <div className="flex items-start space-x-2 p-3 glass rounded-lg hover:bg-accent/50 transition-colors duration-200">
                    <div className="h-2 w-2 bg-primary rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Processing complete</p>
                      <p className="text-xs text-muted-foreground">Your video has been processed</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-2 p-3 glass rounded-lg hover:bg-accent/50 transition-colors duration-200">
                    <div className="h-2 w-2 bg-green-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">New features available</p>
                      <p className="text-xs text-muted-foreground">Check out the latest updates</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 hover:bg-muted/50 transition-colors duration-200"
            >
              <User className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile processing status */}
      {isProcessing && (
        <div className="md:hidden px-6 pb-3">
          <div className="flex items-center space-x-3 px-3 py-2 glass rounded-xl">
            <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-primary-foreground">
                {currentStep}
              </span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-24 h-1 bg-primary/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <span className="text-xs text-primary-foreground/80">
                  {progress}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
