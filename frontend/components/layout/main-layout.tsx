'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Sidebar } from './sidebar';
import { useUI } from '@/hooks/use-app-store';
import { useDarkModeInitialization } from '@/hooks/use-app-store';

interface MainLayoutProps {
  children: ReactNode;
  className?: string;
}

export function MainLayout({ children, className }: MainLayoutProps) {
  const { sidebarOpen } = useUI();
  
  // Initialize dark mode from persisted state
  useDarkModeInitialization();

  return (
    <div className="flex h-screen bg-zinc-50">
      {/* Sidebar - Fixed width 250px, always visible on desktop */}
      <div className="w-64 flex-shrink-0 hidden lg:block">
        <Sidebar />
      </div>
      
      {/* Mobile Sidebar Toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button className="p-2 bg-white rounded-md shadow-md">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7-6h7a2 2 0 01-2 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 01-2-2h7a2 2 0 012 2v6a2 2 0 012-2H6a2 2 0 00-2-2V6a2 2 0 00-2-2h7a2 2 0 012 2v6a2 2 0 012-2H6a2 2 0 00-2-2z" />
          </svg>
        </button>
      </div>
      
      {/* Main Content Area - Takes remaining space */}
      <div className="flex-1 h-full overflow-hidden lg:ml-0">
        {/* Main Content - Scrollable */}
        <main className={cn(
          'h-full overflow-y-auto',
          className
        )}>
          <div className="max-w-7xl mx-auto p-4 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
