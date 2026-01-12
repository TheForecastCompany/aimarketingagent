'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Video
} from 'lucide-react';

const navigation = [
  { 
    name: 'Dashboard', 
    href: '/', 
    icon: LayoutDashboard 
  },
  { 
    name: 'Video Processing', 
    href: '/process', 
    icon: Video 
  },
  // Settings removed - now handled by dedicated page
];

interface NavigationTabsProps {
  className?: string;
}

export function NavigationTabs({ className }: NavigationTabsProps) {
  const pathname = usePathname();

  return (
    <nav className={cn('nav-tabs', className)}>
      <div className="flex items-center justify-center px-4 lg:px-8 py-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                isActive 
                  ? 'tab-active bg-primary text-primary-foreground shadow-sm' 
                  : 'tab-inactive text-muted-foreground hover:bg-muted/50'
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
