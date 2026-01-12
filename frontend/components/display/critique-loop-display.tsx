'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  RefreshCw, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle, 
  MessageSquare,
  Target,
  Zap
} from 'lucide-react';

interface CritiqueResult {
  original_content: string;
  improved_content: string;
  iterations: number;
  final_score: number;
  critique_history: any[];
  improvement_summary: string;
  quality_metrics: any;
}

interface CritiqueLoopDisplayProps {
  critiqueLoop?: {
    linkedin: CritiqueResult;
    twitter: CritiqueResult;
  };
  isEnabled: boolean;
}

export function CritiqueLoopDisplay({ critiqueLoop, isEnabled }: CritiqueLoopDisplayProps) {
  if (!isEnabled || !critiqueLoop) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            AI Critique Loop
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>AI Critique Loop is disabled</p>
            <p className="text-sm">Enable in settings to improve content quality through iterative AI feedback</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatScore = (score: number) => Math.round(score * 100);

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            AI Critique Loop Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {critiqueLoop.linkedin.iterations + critiqueLoop.twitter.iterations}
              </div>
              <div className="text-sm text-muted-foreground">Total Iterations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatScore(critiqueLoop.linkedin.final_score)}%
              </div>
              <div className="text-sm text-muted-foreground">LinkedIn Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatScore(critiqueLoop.twitter.final_score)}%
              </div>
              <div className="text-sm text-muted-foreground">Twitter Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {formatScore((critiqueLoop.linkedin.final_score + critiqueLoop.twitter.final_score) / 2)}%
              </div>
              <div className="text-sm text-muted-foreground">Average Score</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* LinkedIn Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            LinkedIn Content Improvement
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Quality Score</span>
            <div className="flex items-center gap-2">
              <Progress value={formatScore(critiqueLoop.linkedin.final_score)} className="w-24" />
              <Badge variant={formatScore(critiqueLoop.linkedin.final_score) >= 80 ? "default" : "secondary"}>
                {formatScore(critiqueLoop.linkedin.final_score)}%
              </Badge>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Iterations</span>
            <Badge variant="outline">
              {critiqueLoop.linkedin.iterations} revisions
            </Badge>
          </div>

          <div>
            <span className="text-sm font-medium">Improvement Summary</span>
            <p className="text-sm text-muted-foreground mt-1">
              {critiqueLoop.linkedin.improvement_summary}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium">Original Content</span>
              <div className="mt-1 p-3 bg-muted rounded text-sm max-h-32 overflow-y-auto">
                {critiqueLoop.linkedin.original_content}
              </div>
            </div>
            <div>
              <span className="text-sm font-medium">Improved Content</span>
              <div className="mt-1 p-3 bg-green-50 border border-green-200 rounded text-sm max-h-32 overflow-y-auto">
                {critiqueLoop.linkedin.improved_content}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Twitter Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Twitter Thread Improvement
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Quality Score</span>
            <div className="flex items-center gap-2">
              <Progress value={formatScore(critiqueLoop.twitter.final_score)} className="w-24" />
              <Badge variant={formatScore(critiqueLoop.twitter.final_score) >= 80 ? "default" : "secondary"}>
                {formatScore(critiqueLoop.twitter.final_score)}%
              </Badge>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Iterations</span>
            <Badge variant="outline">
              {critiqueLoop.twitter.iterations} revisions
            </Badge>
          </div>

          <div>
            <span className="text-sm font-medium">Improvement Summary</span>
            <p className="text-sm text-muted-foreground mt-1">
              {critiqueLoop.twitter.improvement_summary}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium">Original Content</span>
              <div className="mt-1 p-3 bg-muted rounded text-sm max-h-32 overflow-y-auto">
                {critiqueLoop.twitter.original_content}
              </div>
            </div>
            <div>
              <span className="text-sm font-medium">Improved Content</span>
              <div className="mt-1 p-3 bg-green-50 border border-green-200 rounded text-sm max-h-32 overflow-y-auto">
                {critiqueLoop.twitter.improved_content}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quality Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Quality Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium mb-3">LinkedIn Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Grammar Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.linkedin.quality_metrics?.grammar_score || 0.8)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Engagement Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.linkedin.quality_metrics?.engagement_score || 0.7)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Clarity Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.linkedin.quality_metrics?.clarity_score || 0.9)}%</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-3">Twitter Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Grammar Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.twitter.quality_metrics?.grammar_score || 0.8)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Engagement Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.twitter.quality_metrics?.engagement_score || 0.7)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Clarity Score</span>
                  <span className="font-mono">{formatScore(critiqueLoop.twitter.quality_metrics?.clarity_score || 0.9)}%</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
