'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Video, 
  Play, 
  Settings, 
  AlertCircle,
  CheckCircle,
  Loader2,
  X
} from 'lucide-react';
import { useVideoProcessing } from '@/hooks/use-video-processing';
import { useConfig, useAppActions } from '@/hooks/use-app-store';
import { BrandVoice, VideoUrlForm, ConfigurationForm } from '@/types';
import { toast } from 'sonner';

const videoUrlSchema = z.object({
  video_url: z
    .string()
    .min(1, 'Video URL is required')
    .url('Please enter a valid URL')
    .refine(
      (url) => {
        return url.includes('youtube.com') || 
               url.includes('youtu.be') || 
               url.includes('vimeo.com') ||
               url.includes('loom.com');
      },
      'Please enter a valid video URL (YouTube, Vimeo, or Loom)'
    ),
});

const configurationSchema = z.object({
  brand_voice: z.nativeEnum(BrandVoice),
  keywords: z.string().min(1, 'At least one keyword is required'),
  enable_critique: z.boolean(),
  track_costs: z.boolean(),
});

type VideoUrlFormData = z.infer<typeof videoUrlSchema>;
type ConfigurationFormData = z.infer<typeof configurationSchema>;

export default function ProcessVideo() {
  const { processVideo, processing, isLocked } = useVideoProcessing();
  const config = useConfig();
  const { setConfig } = useAppActions();
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Video URL form
  const videoForm = useForm<VideoUrlFormData>({
    resolver: zodResolver(videoUrlSchema),
    defaultValues: {
      video_url: '',
    },
  });

  // Configuration form
  const configForm = useForm<ConfigurationFormData>({
    resolver: zodResolver(configurationSchema),
    defaultValues: {
      brand_voice: config.brand_voice,
      keywords: config.keywords.join('\n'),
      enable_critique: config.enable_critique,
      track_costs: config.track_costs,
    },
  });

  const onVideoSubmit = async (data: VideoUrlFormData) => {
    if (isLocked) {
      console.warn('⚠️ Submission blocked: Processing already in progress');
      return;
    }

    try {
      const configData = configForm.getValues();
      
      // Convert keywords string to array
      const keywordsArray = configData.keywords
        .split('\n')
        .map(k => k.trim())
        .filter(k => k.length > 0);
      
      // Update global config
      setConfig({
        brand_voice: configData.brand_voice,
        keywords: keywordsArray,
        enable_critique: configData.enable_critique,
        track_costs: configData.track_costs,
      });

      // Process video
      await processVideo({
        youtube_url: data.video_url,
        brand_voice: configData.brand_voice,
        target_keywords: keywordsArray,
        enable_critique_loop: configData.enable_critique,
      });

      toast.success('Video processing started successfully!');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Processing failed');
    }
  };

  const onConfigChange = () => {
    const configData = configForm.getValues();
    
    // Convert keywords string to array
    const keywordsArray = configData.keywords
      .split('\n')
      .map(k => k.trim())
      .filter(k => k.length > 0);
    
    setConfig({
      brand_voice: configData.brand_voice,
      keywords: keywordsArray,
      enable_critique: configData.enable_critique,
      track_costs: configData.track_costs,
    });
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Process Video</h1>
          <p className="text-muted-foreground">
            Transform your video content into multi-platform gold with AI-powered repurposing
          </p>
        </div>

        {/* Processing Status */}
        {processing.isProcessing && (
          <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-900 dark:text-blue-100">
                <Loader2 className="h-5 w-5 animate-spin" />
                Processing Video
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  {processing.currentStep}
                </span>
                <span className="text-sm text-blue-700 dark:text-blue-300">
                  {processing.progress}%
                </span>
              </div>
              <Progress value={processing.progress} className="h-2" />
              
              {processing.error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700">{processing.error}</span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Video className="h-5 w-5" />
                  Video Information
                </CardTitle>
                <CardDescription>
                  Enter the URL of the video you want to process
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...videoForm}>
                  <form onSubmit={videoForm.handleSubmit(onVideoSubmit)} className="space-y-4">
                    <FormField
                      control={videoForm.control}
                      name="video_url"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Video URL</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="https://www.youtube.com/watch?v=..."
                              {...field}
                              disabled={processing.isProcessing || isLocked}
                            />
                          </FormControl>
                          <FormDescription>
                            Supported platforms: YouTube, Vimeo, Loom
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <Button 
                      type="submit" 
                      size="lg" 
                      className="w-full"
                      disabled={processing.isProcessing || isLocked}
                    >
                      {processing.isProcessing || isLocked ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          {isLocked ? 'Processing in background...' : 'Processing...'}
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Process Video
                        </>
                      )}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>

            {/* Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration
                </CardTitle>
                <CardDescription>
                  Customize how your content will be generated
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...configForm}>
                  <form onChange={onConfigChange} className="space-y-6">
                    <FormField
                      control={configForm.control}
                      name="brand_voice"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Brand Voice</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select brand voice" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value={BrandVoice.PROFESSIONAL}>Professional</SelectItem>
                              <SelectItem value={BrandVoice.CASUAL}>Casual</SelectItem>
                              <SelectItem value={BrandVoice.PLAYFUL}>Playful</SelectItem>
                              <SelectItem value={BrandVoice.AUTHORITATIVE}>Authoritative</SelectItem>
                              <SelectItem value={BrandVoice.EMPATHETIC}>Empathetic</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormDescription>
                            Choose the tone and style for your content
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={configForm.control}
                      name="keywords"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Target Keywords</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="AI&#10;machine learning&#10;technology"
                              className="min-h-[100px]"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Enter keywords you want to target (one per line)
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="space-y-4">
                      <FormField
                        control={configForm.control}
                        name="enable_critique"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">AI Critique Loop</FormLabel>
                              <FormDescription>
                                Enable AI-powered content quality improvement
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                                disabled={processing.isProcessing}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={configForm.control}
                        name="track_costs"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Track Costs</FormLabel>
                              <FormDescription>
                                Monitor API usage and costs
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                                disabled={processing.isProcessing}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Tips */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Tips</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                  <p className="text-sm">Use high-quality videos for better transcription accuracy</p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                  <p className="text-sm">Videos with clear audio perform best</p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                  <p className="text-sm">Include relevant keywords for better SEO</p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                  <p className="text-sm">Enable AI critique for higher quality content</p>
                </div>
              </CardContent>
            </Card>

            {/* Processing Info */}
            <Card>
              <CardHeader>
                <CardTitle>What Happens Next</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">1</Badge>
                  <span className="text-sm">Extract transcript from video</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">2</Badge>
                  <span className="text-sm">Analyze content and topics</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">3</Badge>
                  <span className="text-sm">Generate platform-specific content</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">4</Badge>
                  <span className="text-sm">Apply quality checks</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">5</Badge>
                  <span className="text-sm">Deliver final results</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
