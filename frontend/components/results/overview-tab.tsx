'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, Target, DollarSign, RefreshCw } from 'lucide-react';
import { useSafeDateFormat } from '@/lib/utils/client-helpers';
import { CostDisplay } from '@/components/display/cost-display';
import { CritiqueLoopDisplay } from '@/components/display/critique-loop-display';
import { useAppStore } from '@/hooks/use-app-store';

interface ProcessedVideo {
  id: string;
  title: string;
  description: string;
  platforms: string[];
  created_at: string;
  status: string;
  thumbnail_url: string;
  content_snippets?: Record<string, string>;
  cost_metrics?: {
    total_cost: number;
    total_tokens: number;
    total_calls: number;
    session_duration: number;
    agents_count: number;
    video_count: number;
    content_pieces_generated: number;
    current_metrics: {
      video_count: number;
      content_pieces_generated: number;
      total_cost: number;
      total_tokens: number;
      total_calls: number;
    };
    cost_breakdown?: Record<string, {
      total_cost: number;
      total_tokens: number;
      total_calls: number;
      avg_cost_per_call: number;
      avg_tokens_per_call: number;
    }>;
  };
  critique_loop?: {
    linkedin: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
    twitter: {
      original_content: string;
      improved_content: string;
      iterations: number;
      final_score: number;
      critique_history: any[];
      improvement_summary: string;
      quality_metrics: any;
    };
  };
}

interface OverviewTabProps {
  selectedResult: ProcessedVideo;
}

export function OverviewTab({ selectedResult }: OverviewTabProps) {
  // Hook is now properly called at the top level of this component
  const safeDateFormat = useSafeDateFormat;
  const { config } = useAppStore();

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Processing Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Total Platforms</span>
              <span className="text-sm text-muted-foreground">
                {selectedResult.platforms.length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status</span>
              <Badge variant={selectedResult.status === 'completed' ? 'default' : 'secondary'}>
                {selectedResult.status}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Created</span>
              <span className="text-sm text-muted-foreground">
                {safeDateFormat(selectedResult.created_at)}
              </span>
            </div>
            {selectedResult.cost_metrics && (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Total Cost</span>
                <Badge variant="outline" className="text-xs">
                  ${selectedResult.cost_metrics.total_cost.toFixed(4)}
                </Badge>
              </div>
            )}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Cost Tracking</span>
              <Badge variant={config.track_costs ? "default" : "secondary"} className="text-xs">
                {config.track_costs ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Critique Loop</span>
              <Badge variant={config.enable_critique ? "default" : "secondary"} className="text-xs">
                {config.enable_critique ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            {selectedResult.critique_loop && (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Iterations</span>
                <Badge variant="outline" className="text-xs">
                  {selectedResult.critique_loop.linkedin.iterations + selectedResult.critique_loop.twitter.iterations} iterations
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Content Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <span className="text-sm font-medium">Description</span>
              <p className="text-sm text-muted-foreground mt-1">
                {selectedResult.description}
              </p>
            </div>
            <div>
              <span className="text-sm font-medium">Platforms</span>
              <div className="flex flex-wrap gap-1 mt-2">
                {selectedResult.platforms.map((platform, index) => (
                  <Badge key={index} variant="outline">
                    {platform.charAt(0).toUpperCase() + platform.slice(1)}
                  </Badge>
                ))}
              </div>
            </div>
            
            {/* Content Preview Section */}
            {selectedResult.content_snippets && Object.keys(selectedResult.content_snippets).length > 0 && (
              <div>
                <span className="text-sm font-medium">Generated Content</span>
                <div className="mt-2 space-y-2">
                  {Object.entries(selectedResult.content_snippets).map(([platform, content]) => {
                    const wordCount = content ? content.split(' ').length : 0;
                    const preview = content ? content.substring(0, 150) + (content.length > 150 ? '...' : '') : 'No content';
                    
                    return (
                      <div key={platform} className="p-3 border rounded-lg bg-muted/30">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">{platform}</span>
                          <Badge variant="secondary" className="text-xs">
                            {wordCount} words
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {preview}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Cost Tracking Section */}
      <CostDisplay 
        costMetrics={selectedResult.cost_metrics} 
        isEnabled={config.track_costs} 
      />

      {/* Critique Loop Section */}
      <CritiqueLoopDisplay 
        critiqueLoop={selectedResult.critique_loop} 
        isEnabled={config.enable_critique} 
      />
    </div>
  );
}
