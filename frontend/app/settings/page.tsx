'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MainLayout } from '@/components/layout/main-layout';
import { 
  Settings as SettingsIcon, 
  Video, 
  Sliders,
  Zap,
  Clock,
  CheckCircle
} from 'lucide-react';
import { useUI, useProcessing, useAppStore } from '@/hooks/use-app-store';
import { BrandVoice } from '@/types';

export default function Settings() {
  const { darkMode, toggleDarkMode } = useUI();
  const { isProcessing, currentStep, progress } = useProcessing();
  const { config, setConfig } = useAppStore();

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Processing Settings</h1>
          <p className="text-muted-foreground">
            Configure your video processing preferences and AI behavior.
          </p>
        </div>

        {/* Processing Settings Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sliders className="h-5 w-5" />
              Processing Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Brand Voice */}
            <div>
              <label className="text-sm font-medium mb-2">Brand Voice</label>
              <select 
                value={config.brand_voice}
                onChange={(e) => setConfig({...config, brand_voice: e.target.value as any})}
                className="w-full p-2 border rounded-md bg-background"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="playful">Playful</option>
                <option value="authoritative">Authoritative</option>
                <option value="empathetic">Empathetic</option>
              </select>
            </div>

            {/* Enable Critique Loop */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium">Enable Critique Loop</label>
                <p className="text-xs text-muted-foreground">Iteratively improve content quality</p>
              </div>
              <Button
                variant={config.enable_critique ? "default" : "outline"}
                onClick={() => setConfig({...config, enable_critique: !config.enable_critique})}
                className="w-20"
              >
                {config.enable_critique ? 'Enabled' : 'Disabled'}
              </Button>
            </div>

            {/* Track Costs */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium">Track Costs</label>
                <p className="text-xs text-muted-foreground">Monitor API usage</p>
              </div>
              <Button
                variant={config.track_costs ? "default" : "outline"}
                onClick={() => setConfig({...config, track_costs: !config.track_costs})}
                className="w-20"
              >
                {config.track_costs ? 'Enabled' : 'Disabled'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Current Processing Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Current Processing Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isProcessing ? (
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-primary animate-pulse" />
                  <span className="font-medium">Processing in progress...</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Current Step:</span>
                    <Badge variant="secondary">{currentStep}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Progress:</span>
                    <div className="flex-1">
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm text-muted-foreground">{progress}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                <p className="text-muted-foreground">No active processing</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <Button 
            variant="outline"
            onClick={() => {
              // Reset to defaults
              setConfig({
                brand_voice: BrandVoice.PROFESSIONAL,
                keywords: ['AI', 'machine learning', 'technology'],
                enable_critique: true,
                track_costs: true,
              });
            }}
          >
            Reset to Defaults
          </Button>
          <Button 
            onClick={() => {
              // Show success message
              alert('Settings saved successfully!');
            }}
          >
            Save Settings
          </Button>
        </div>
      </div>
    </MainLayout>
  );
}
