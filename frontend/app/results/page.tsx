'use client';

import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Download,
  Copy,
  MessageSquare,
  Video,
  BarChart3,
  CheckCircle,
  Clock,
  Users,
  Mail,
  Share
} from 'lucide-react';
import { toast } from 'sonner';
import { Separator } from '@/components/ui/separator';
import { ResultCard } from '@/components/results/result-card';
import { OverviewTab } from '@/components/results/overview-tab';

// Types for API responses
interface ProcessedVideo {
  id: string;
  title: string;
  description: string;
  platforms: string[];
  created_at: string;
  status: string;
  thumbnail_url: string;
  content_snippets: Record<string, string>;
  newsletter?: {
    subject: string;
    body_content: string;
    call_to_action?: string;
  };
  social_media?: Record<string, {
    content: string;
    hashtags?: string[];
  }>;
  blog?: {
    title: string;
    content: string;
    excerpt?: string;
  };
  scripts?: Record<string, {
    content: string;
    duration?: number;
  }>;
}

interface VideoContent {
  platform: string;
  content: string;
  word_count: number;
  created_at: string;
}

export default function Results() {
  const [processedVideos, setProcessedVideos] = useState<ProcessedVideo[]>([]);
  const [selectedResult, setSelectedResult] = useState<ProcessedVideo | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch processed videos from API
  const fetchVideos = async () => {
    try {
      setIsLoading(true);
      console.log('🔍 Fetching videos from API client...');
      const { apiClient } = await import('@/services/api');
      const data = await apiClient.getVideos();
      console.log('📊 Fetched videos:', data);
      console.log('📊 Number of videos:', data.length);
      console.log('📊 Data type:', typeof data);
      console.log('📊 Is array?:', Array.isArray(data));
      
      if (data && data.length > 0) {
        console.log('📋 First video structure:', Object.keys(data[0]));
        console.log('📋 First video content snippets:', data[0].content_snippets ? Object.keys(data[0].content_snippets) : 'No content_snippets');
        
        // Defensive rendering - log actual content
        if (data[0].content_snippets) {
          Object.entries(data[0].content_snippets).forEach(([key, value]) => {
            const content = value as string;
            console.log(`📝 ${key}: ${content ? content.length : 0} characters`);
            console.log(`📝 ${key} preview: ${content ? content.substring(0, 100) + '...' : 'EMPTY'}`);
          });
        } else {
          console.warn('⚠️ No content_snippets found on video object');
        }
      }
      
      setProcessedVideos(data);
    } catch (error) {
      console.error('❌ Error fetching videos:', error);
      toast.error(`Failed to load processed videos: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  // Fetch content for selected video
  useEffect(() => {
    if (selectedResult?.id && selectedResult.content_snippets) {
      console.log('🎯 Processing content for video:', selectedResult.id);
      console.log('📝 Content snippets available:', Object.keys(selectedResult.content_snippets));
      
      // Defensive: Check if content_snippets actually has content
      const hasContent = Object.values(selectedResult.content_snippets).some(value => 
        value && typeof value === 'string' && value.trim().length > 0
      );
      
      if (!hasContent) {
        console.warn('⚠️ Content snippets exist but are empty or invalid');
        Object.entries(selectedResult.content_snippets).forEach(([key, value]) => {
          console.log(`🔍 ${key}:`, { value, type: typeof value, length: value?.length, isEmpty: !value?.trim() });
        });
      }
      
      // Content is already in content_snippets, no need for separate fetch
      // Convert content_snippets to the expected format for display
      const socialMedia: Record<string, { content: string; hashtags?: string[] }> = {};
      const scripts: Record<string, { content: string; duration?: number }> = {};
      
      Object.entries(selectedResult.content_snippets).forEach(([platform, content]) => {
        console.log(`🔄 Processing platform: ${platform}`);
        const contentStr = content as string;
        
        if (['LinkedIn', 'Twitter', 'Facebook', 'Instagram'].includes(platform)) {
          socialMedia[platform.toLowerCase()] = { content: contentStr || 'No content generated' };
        } else if (['Scripts', 'Short Scripts'].includes(platform)) {
          scripts[platform.toLowerCase().replace(' ', '_')] = { content: contentStr || 'No content generated' };
        }
      });

      console.log('📱 Social media content:', Object.keys(socialMedia));
      console.log('🎬 Scripts content:', Object.keys(scripts));

      setSelectedResult(prev => prev ? {
        ...prev,
        social_media: socialMedia,
        scripts: scripts,
        newsletter: selectedResult.content_snippets['Newsletter'] ? {
          subject: 'Newsletter Content',
          body_content: selectedResult.content_snippets['Newsletter'] as string || 'No newsletter content generated',
          call_to_action: 'Learn more about our offerings'
        } : undefined,
        blog: selectedResult.content_snippets['Blog'] ? {
          title: 'Blog Post',
          content: selectedResult.content_snippets['Blog'] as string || 'No blog content generated',
          excerpt: (selectedResult.content_snippets['Blog'] as string || '').substring(0, 200) + '...'
        } : undefined
      } : null);
    }
  }, [selectedResult?.id, selectedResult?.content_snippets]);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  const downloadContent = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    toast.success(`Downloaded ${filename}`);
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
            <p className="text-muted-foreground">Loading processed videos...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (processedVideos.length === 0 && !isLoading) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground" />
            <h1 className="text-3xl font-bold tracking-tight mb-4">No Results Yet</h1>
            <p className="text-muted-foreground mb-6">
              Start processing videos to see your content repurposing results here.
            </p>
            <a 
              href="/process"
              className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Video className="h-4 w-4 mr-2" />
              Process Your First Video
            </a>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6 p-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Results</h1>
            <p className="text-muted-foreground">
              Your AI-generated content from video processing
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={fetchVideos}>
              <Users className="h-4 w-4 mr-2" />
              Refresh Results
            </Button>
          </div>
        </div>

        {/* Results Grid */}
        {processedVideos.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {processedVideos.map((video) => (
              <ResultCard
                key={video.id}
                video={video}
                isSelected={selectedResult?.id === video.id}
                onClick={() => setSelectedResult(video)}
              />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No processed videos available</p>
            </CardContent>
          </Card>
        )}

        {/* Selected Result Details */}
        {selectedResult && (
          <div className="mt-8">
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="social">Social Media</TabsTrigger>
                <TabsTrigger value="newsletter">Newsletter</TabsTrigger>
                <TabsTrigger value="blog">Blog Post</TabsTrigger>
                <TabsTrigger value="scripts">Scripts</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                <OverviewTab selectedResult={selectedResult} />
              </TabsContent>

              {/* Newsletter Tab */}
              <TabsContent value="newsletter" className="space-y-6">
                {selectedResult.newsletter ? (
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <Mail className="h-5 w-5" />
                          Newsletter Content
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => copyToClipboard(selectedResult.newsletter!.body_content, 'Newsletter content')}
                          >
                            <Copy className="h-4 w-4 mr-1" />
                            Copy
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => downloadContent(selectedResult.newsletter!.body_content, 'newsletter.txt')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <span className="text-sm font-medium">Subject:</span>
                        <p className="text-sm mt-1 font-medium text-foreground">
                          {selectedResult.newsletter.subject}
                        </p>
                      </div>
                      <Separator />
                      <div>
                        <span className="text-sm font-medium">Body Content:</span>
                        <div className="mt-2 p-4 bg-muted/50 rounded-lg border">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {selectedResult.newsletter.body_content}
                          </p>
                        </div>
                      </div>
                      {selectedResult.newsletter.call_to_action && (
                        <div>
                          <span className="text-sm font-medium">Call to Action:</span>
                          <div className="mt-1 p-3 bg-primary/10 rounded border-l-4 border-primary">
                            <p className="text-sm font-medium">{selectedResult.newsletter.call_to_action}</p>
                          </div>
                        </div>
                      )}
                      <div className="flex justify-end gap-2 pt-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => copyToClipboard(selectedResult.newsletter!.body_content, 'Newsletter content')}
                        >
                          <Copy className="h-4 w-4 mr-1" />
                          Copy
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => downloadContent(selectedResult.newsletter!.body_content, 'newsletter.txt')}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">No newsletter content generated</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Blog Post Tab */}
              <TabsContent value="blog" className="space-y-6">
                {selectedResult.blog ? (
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <FileText className="h-5 w-5" />
                          Blog Post
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => copyToClipboard(selectedResult.blog!.content, 'Blog post')}
                          >
                            <Copy className="h-4 w-4 mr-1" />
                            Copy
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => downloadContent(selectedResult.blog!.content, 'blog-post.txt')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <span className="text-sm font-medium">Title:</span>
                        <p className="text-sm mt-1 font-medium text-foreground">
                          {selectedResult.blog.title}
                        </p>
                      </div>
                      {selectedResult.blog.excerpt && (
                        <div>
                          <span className="text-sm font-medium">Excerpt:</span>
                          <div className="mt-1 p-3 bg-muted/50 rounded border">
                            <p className="text-sm italic text-muted-foreground">
                              {selectedResult.blog.excerpt}
                            </p>
                          </div>
                        </div>
                      )}
                      <Separator />
                      <div>
                        <span className="text-sm font-medium">Content:</span>
                        <div className="mt-2 p-4 bg-muted/50 rounded-lg border">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {selectedResult.blog.content}
                          </p>
                        </div>
                      </div>
                      <div className="flex justify-end gap-2 pt-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => copyToClipboard(selectedResult.blog!.content, 'Blog post')}
                        >
                          <Copy className="h-4 w-4 mr-1" />
                          Copy
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => downloadContent(selectedResult.blog!.content, 'blog-post.txt')}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">No blog content generated</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Scripts Tab */}
              <TabsContent value="scripts" className="space-y-6">
                {selectedResult.scripts && Object.keys(selectedResult.scripts).length > 0 ? (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Video className="h-5 w-5" />
                        Video Scripts
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {Object.entries(selectedResult.scripts).map(([scriptType, script]) => (
                        <div key={scriptType} className="space-y-3 p-4 border rounded-lg bg-muted/30">
                          <div className="flex items-center justify-between mb-3">
                            <h3 className="text-lg font-semibold capitalize">
                              {scriptType.replace('_', ' ')}
                            </h3>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                {script.content ? script.content.split(' ').length : 0} words
                              </Badge>
                              {script.duration && (
                                <Badge variant="secondary" className="text-xs">
                                  {script.duration}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <div className="p-3 bg-background rounded border">
                            <p className="text-sm leading-relaxed whitespace-pre-wrap font-mono">
                              {script.content || 'No content generated'}
                            </p>
                          </div>
                          <div className="flex justify-end gap-2 pt-3">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => copyToClipboard(script.content, `${scriptType} script`)}
                            >
                              <Copy className="h-4 w-4 mr-1" />
                              Copy
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => downloadContent(script.content, `${scriptType}-script.txt`)}
                            >
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </Button>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Video className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">No scripts generated</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Social Media Tab */}
              <TabsContent value="social" className="space-y-6">
                {selectedResult.social_media && Object.keys(selectedResult.social_media).length > 0 ? (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Share className="h-5 w-5" />
                        Social Media Posts
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {Object.entries(selectedResult.social_media).map(([platform, post]) => (
                        <div key={platform} className="space-y-3 p-4 border rounded-lg bg-muted/30">
                          <div className="flex items-center justify-between mb-3">
                            <h3 className="text-lg font-semibold capitalize">
                              {platform}
                            </h3>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                {post.content ? post.content.split(' ').length : 0} words
                              </Badge>
                              {post.hashtags && post.hashtags.length > 0 && (
                                <div className="flex gap-1">
                                  {post.hashtags.map((tag, index) => (
                                    <Badge key={index} variant="secondary" className="text-xs">
                                      #{tag}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="p-3 bg-background rounded border">
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">
                              {post.content || 'No content generated'}
                            </p>
                          </div>
                          <div className="flex justify-end gap-2 pt-3">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => copyToClipboard(post.content, `${platform} post`)}
                            >
                              <Copy className="h-4 w-4 mr-1" />
                              Copy
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => downloadContent(post.content, `${platform}-post.txt`)}
                            >
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </Button>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Share className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">No social media content generated</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
