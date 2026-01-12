'use client';

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export function Skeleton({ 
  className, 
  variant = 'default',
  width,
  height,
  lines = 1
}: SkeletonProps) {
  const baseClasses = 'skeleton';
  
  if (variant === 'text') {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              baseClasses,
              i === lines - 1 ? 'w-3/4' : 'w-full'
            )}
            style={{ height: height || '1rem' }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circular') {
    return (
      <div
        className={cn(baseClasses, 'rounded-full', className)}
        style={{ 
          width: width || '2.5rem', 
          height: height || '2.5rem' 
        }}
      />
    );
  }

  return (
    <div
      className={cn(baseClasses, 'rounded-lg', className)}
      style={{ 
        width: width || '100%', 
        height: height || '1.5rem' 
      }}
    />
  );
}

interface CardSkeletonProps {
  className?: string;
}

export function CardSkeleton({ className }: CardSkeletonProps) {
  return (
    <div className={cn('card-elevated p-6 space-y-4', className)}>
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="circular" width={40} height={40} />
      </div>
      <Skeleton variant="text" lines={2} />
      <div className="flex items-center space-x-2">
        <Skeleton width="4rem" height="0.75rem" />
        <Skeleton width="2rem" height="0.75rem" />
      </div>
    </div>
  );
}

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function TableSkeleton({ 
  rows = 5, 
  columns = 4,
  className 
}: TableSkeletonProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex space-x-4 p-4 border-b">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} width="8rem" height="1rem" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4 p-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} width="6rem" height="0.875rem" />
          ))}
        </div>
      ))}
    </div>
  );
}
