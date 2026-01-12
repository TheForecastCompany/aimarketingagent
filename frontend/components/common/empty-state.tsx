import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { EmptyStateProps } from '@/types';

export function EmptyState({ 
  title, 
  description, 
  action, 
  className,
  icon: Icon 
}: EmptyStateProps & { icon?: any }) {
  return (
    <Card className={cn('border-dashed', className)}>
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        {Icon && (
          <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Icon className="h-8 w-8 text-muted-foreground" />
          </div>
        )}
        
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground mb-6 max-w-md">{description}</p>
        
        {action && (
          <Button onClick={action.onClick} size="lg">
            {action.label}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

export function EmptyResults({ 
  onProcessVideo 
}: { 
  onProcessVideo?: () => void 
}) {
  return (
    <EmptyState
      title="No Results Yet"
      description="Start processing videos to see your content repurposing results here."
      action={onProcessVideo ? {
        label: "Process Your First Video",
        onClick: onProcessVideo
      } : undefined}
      icon={require('lucide-react').FileText}
    />
  );
}

export function EmptyHistory() {
  return (
    <EmptyState
      title="No Processing History"
      description="Your video processing history will appear here once you start processing videos."
      icon={require('lucide-react').Clock}
    />
  );
}

export function EmptyAnalytics() {
  return (
    <EmptyState
      title="No Analytics Data"
      description="Analytics and performance metrics will be available after processing videos."
      icon={require('lucide-react').BarChart3}
    />
  );
}
