'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { CheckCircle } from 'lucide-react';
import { useSafeDateFormat } from '@/lib/utils/client-helpers';

interface ProcessedVideo {
  id: string;
  title: string;
  description: string;
  platforms: string[];
  created_at: string;
  status: string;
  thumbnail_url: string;
}

interface ResultCardProps {
  video: ProcessedVideo;
  isSelected: boolean;
  onClick: () => void;
}

export function ResultCard({ video, isSelected, onClick }: ResultCardProps) {
  // Hook is now properly called at the top level of this component
  const safeDateFormat = useSafeDateFormat;

  return (
    <Card 
      className={`cursor-pointer transition-all duration-200 hover:shadow-lg flex flex-col h-full ${
        isSelected 
          ? 'ring-2 ring-primary ring-offset-2' 
          : 'hover:shadow-md hover:border-primary/50'
      }`}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <div className="relative">
                <img 
                  src={video.thumbnail_url} 
                  alt={video.title}
                  className="w-16 h-16 object-cover rounded-lg"
                  onError={(e) => {
                    e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDQwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yMDAgMTUwQzE3Ny45MSAxNTAgMTYwIDE2Ny45MSAxNjAgMTkwQzE2MCAyMTIuMDkgMTc3LjkxIDIzMCAyMDAgMjMwQzIyMi4wOSAyMzAgMjQwIDIxMi4wOSAyNDAgMTkwQzI0MCAxNjcuOTEgMjIyLjA5IDE1MCAyMDAgMTUwWk0yMDAgMjYwQzE3Ny45MSAyNjAgMTYwIDI0Mi4wOSAxNjAgMjIwQzE2MCAxOTcuOTEgMTc3LjkxIDE4MCAyMDAgMTgwQzIyMi4wOSAxODAgMjQwIDE5Ny45MSAyNDAgMjIwQzI0MCAyNDIuMDkgMjIyLjA5IDI2MCAyMDAgMjYwWiIgZmlsbD0iI0QxRDVEQiIvPgo8L3N2Zz4K';
                  }}  
                />
                {video.status === 'processing' && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></div>
                  </div>
                )}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground line-clamp-2">{video.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{video.description}</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge 
              variant={video.status === 'completed' ? 'default' : 'secondary'}
              className="gap-1"
            >
              {video.status === 'processing' ? (
                <>
                  <div className="animate-pulse h-2 w-2 bg-primary rounded-full"></div>
                  Processing
                </>
              ) : video.status === 'completed' ? (
                <>
                  <CheckCircle className="h-3 w-3" />
                  Complete
                </>
              ) : (
                <>
                  <div className="h-2 w-2 bg-red-500 rounded-full"></div>
                  Failed
                </>
              )}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0 flex flex-col h-full justify-between">
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
          <span>{safeDateFormat(video.created_at)}</span>
          <div className="flex items-center gap-2">
            <span>{video.platforms.length} platforms</span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {video.platforms.map((platform, index) => (
            <Badge key={index} variant="outline" className="text-xs">
              {platform.charAt(0).toUpperCase() + platform.slice(1)}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
