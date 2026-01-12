'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, TrendingUp, Activity, BarChart3 } from 'lucide-react';

interface CostMetrics {
  total_cost: number;
  total_tokens: number;
  total_calls: number;
  session_duration: number;
  agents_count: number;
  video_count: number;
  content_pieces_generated: number;
  cost_breakdown?: Record<string, {
    total_cost: number;
    total_tokens: number;
    total_calls: number;
    avg_cost_per_call: number;
    avg_tokens_per_call: number;
  }>;
}

interface CostDisplayProps {
  costMetrics?: CostMetrics;
  isEnabled: boolean;
}

export function CostDisplay({ costMetrics, isEnabled }: CostDisplayProps) {
  if (!isEnabled || !costMetrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Cost Tracking
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Cost tracking is disabled</p>
            <p className="text-sm">Enable cost tracking in settings to monitor API usage</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatCost = (cost: number) => `$${cost.toFixed(4)}`;
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Cost Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCost(costMetrics.total_cost)}
              </div>
              <div className="text-sm text-muted-foreground">Total Cost</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {costMetrics.total_tokens.toLocaleString()}
              </div>
              <div className="text-sm text-muted-foreground">Total Tokens</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {costMetrics.total_calls}
              </div>
              <div className="text-sm text-muted-foreground">API Calls</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {formatDuration(costMetrics.session_duration)}
              </div>
              <div className="text-sm text-muted-foreground">Session Time</div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">
                {costMetrics.video_count}
              </div>
              <div className="text-sm text-muted-foreground">Videos Processed</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">
                {costMetrics.content_pieces_generated}
              </div>
              <div className="text-sm text-muted-foreground">Content Pieces</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-purple-600">
                {costMetrics.agents_count}
              </div>
              <div className="text-sm text-muted-foreground">Active Agents</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Efficiency Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Efficiency Metrics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold">
                {formatCost(costMetrics.total_cost / costMetrics.total_calls)}
              </div>
              <div className="text-sm text-muted-foreground">Cost per Call</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">
                {Math.round(costMetrics.total_tokens / costMetrics.total_calls)}
              </div>
              <div className="text-sm text-muted-foreground">Tokens per Call</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">
                {formatCost(costMetrics.total_cost / costMetrics.video_count)}
              </div>
              <div className="text-sm text-muted-foreground">Cost per Video</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown by Agent */}
      {costMetrics.cost_breakdown && Object.keys(costMetrics.cost_breakdown).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Cost Breakdown by Agent
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(costMetrics.cost_breakdown).map(([agentName, metrics]) => (
                <div key={agentName} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{agentName}</div>
                    <div className="text-sm text-muted-foreground">
                      {metrics.total_calls} calls • {metrics.total_tokens.toLocaleString()} tokens
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">{formatCost(metrics.total_cost)}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatCost(metrics.avg_cost_per_call)}/call
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
