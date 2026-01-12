'use client';

import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Clock,
  Video,
  FileText,
  Target,
  Zap,
  Download,
  Calendar
} from 'lucide-react';
import { useResultsHistory } from '@/hooks/use-app-store';
import { EmptyAnalytics } from '@/components/common/empty-state';
import { useSafeDateTimeFormat } from '@/lib/utils/client-helpers';

export default function Analytics() {
  const resultsHistory = useResultsHistory();
  const safeDateTimeFormat = useSafeDateTimeFormat;

  if (resultsHistory.length === 0) {
    return <EmptyAnalytics />;
  }

  // Calculate analytics from results history
  const totalVideos = resultsHistory.length;
  const totalProcessingTime = resultsHistory.reduce((sum, result) => sum + result.total_execution_time, 0);
  const avgProcessingTime = totalProcessingTime / totalVideos;
  const totalPlatforms = resultsHistory.reduce((sum, result) => sum + Object.keys(result.social_media).length, 0);
  const avgQualityScore = resultsHistory.reduce((sum, result) => {
    const scores = Object.values(result.quality_scores);
    return sum + (scores.reduce((a, b) => a + b, 0) / scores.length);
  }, 0) / totalVideos;

  // Mock performance data
  const performanceData = [
    { metric: 'Total Videos Processed', value: totalVideos, icon: Video, trend: '+2 this week' },
    { metric: 'Average Processing Time', value: `${avgProcessingTime.toFixed(1)}s`, icon: Clock, trend: '-0.5s vs last week' },
    { metric: 'Content Generated', value: totalPlatforms, icon: FileText, trend: '+8 this week' },
    { metric: 'Average Quality Score', value: `${avgQualityScore.toFixed(0)}/100`, icon: Target, trend: '+3 vs last week' },
  ];

  // Mock platform usage data
  const platformUsage = [
    { platform: 'LinkedIn', count: 12, percentage: 30 },
    { platform: 'Twitter', count: 10, percentage: 25 },
    { platform: 'Facebook', count: 8, percentage: 20 },
    { platform: 'Instagram', count: 10, percentage: 25 },
  ];

  // Mock weekly activity
  const weeklyActivity = [
    { day: 'Mon', videos: 2 },
    { day: 'Tue', videos: 3 },
    { day: 'Wed', videos: 1 },
    { day: 'Thu', videos: 4 },
    { day: 'Fri', videos: 2 },
    { day: 'Sat', videos: 1 },
    { day: 'Sun', videos: 0 },
  ];

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground">
              Track your content repurposing performance and insights
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Calendar className="h-4 w-4 mr-2" />
              Last 30 Days
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {performanceData.map((item) => (
            <Card key={item.metric}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {item.metric}
                </CardTitle>
                <item.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{item.value}</div>
                <p className="text-xs text-muted-foreground">
                  {item.trend}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Platform Usage */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Platform Usage
              </CardTitle>
              <CardDescription>
                Distribution of content across platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {platformUsage.map((platform) => (
                  <div key={platform.platform} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{platform.platform}</span>
                      <span className="text-sm text-muted-foreground">
                        {platform.count} pieces ({platform.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all duration-300"
                        style={{ width: `${platform.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Weekly Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Weekly Activity
              </CardTitle>
              <CardDescription>
                Videos processed this week
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {weeklyActivity.map((day) => (
                  <div key={day.day} className="flex items-center justify-between">
                    <span className="text-sm font-medium w-8">{day.day}</span>
                    <div className="flex-1 mx-3">
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(day.videos / 4) * 100}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm text-muted-foreground w-4 text-right">
                      {day.videos}
                    </span>
                  </div>
                ))}
              </div>
              
              <Separator className="my-4" />
              
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">
                  {weeklyActivity.reduce((sum, day) => sum + day.videos, 0)}
                </div>
                <p className="text-xs text-muted-foreground">Total this week</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Processing History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Recent Processing History
            </CardTitle>
            <CardDescription>
              Latest video processing activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {resultsHistory.slice(0, 5).map((result, index) => (
                <div key={result.workflow_id}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Video className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">Processing #{resultsHistory.length - index}</p>
                        <p className="text-sm text-muted-foreground">
                          {safeDateTimeFormat(result.metadata.processed_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {result.total_execution_time.toFixed(1)}s
                      </Badge>
                      <Badge variant="secondary">
                        {Object.keys(result.social_media).length} platforms
                      </Badge>
                    </div>
                  </div>
                  {index < Math.min(4, resultsHistory.length - 1) && <Separator className="mt-4" />}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
