'use client';

import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Video, 
  Play,
  ArrowUpRight,
  CheckCircle
} from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-8 py-12">
        {/* Hero Section */}
        <div className="text-center space-y-8">
          <div className="relative inline-block">
            <div className="h-24 w-24 mx-auto rounded-2xl bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-white shadow-2xl">
              <Video className="h-12 w-12 text-white" />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-foreground mt-6">
              Content Repurposing Agency
            </h1>
            <p className="text-xl text-muted-foreground mt-4 max-w-2xl mx-auto">
              Transform your video content into multi-platform gold with AI-powered intelligence
            </p>
          </div>
          
          <Link 
            href="/process"
            className="inline-flex items-center px-8 py-4 bg-primary text-primary-foreground rounded-xl shadow-lg hover:bg-primary/90 transition-all duration-300"
          >
            <Play className="h-5 w-5 mr-2" />
            Process Your First Video
            <ArrowUpRight className="h-5 w-5 ml-2" />
          </Link>
        </div>

        {/* Features Section */}
        <div className="grid gap-8 md:grid-cols-3">
          <Card className="card-elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <Video className="h-8 w-8 text-primary" />
                Video Processing
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                Upload your video and let our AI transform it into optimized content for every platform
              </p>
              <Link 
                href="/process"
                className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                <Video className="h-4 w-4 mr-2" />
                Start Processing
                <ArrowUpRight className="h-4 w-4 ml-2" />
              </Link>
            </CardContent>
          </Card>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center text-white">
                  <CheckCircle className="h-5 w-5 text-white" />
                </div>
                Multi-Platform Content
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                Generate tailored content for LinkedIn, Twitter, Instagram, and more with a single click
              </p>
              <Link 
                href="/process"
                className="inline-flex items-center px-6 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors"
              >
                <Play className="h-4 w-4 mr-2" />
                Generate Content
                <ArrowUpRight className="h-4 w-4 ml-2" />
              </Link>
            </CardContent>
          </Card>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white">
                  <Video className="h-5 w-5 text-white" />
                </div>
                Analytics & Results
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                View your generated content and track performance across all platforms
              </p>
              <Link 
                href="/results"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
              >
                <Video className="h-4 w-4 mr-2" />
                View Results
                <ArrowUpRight className="h-4 w-4 ml-2" />
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-12">
          <p className="text-muted-foreground mb-6">
            Ready to transform your content strategy? 
          </p>
          <Link 
            href="/process"
            className="inline-flex items-center px-8 py-4 bg-primary text-primary-foreground rounded-xl shadow-lg hover:bg-primary/90 transition-all duration-300"
          >
            <Video className="h-5 w-5 mr-2" />
            Get Started Now
            <ArrowUpRight className="h-5 w-5 ml-2" />
          </Link>
        </div>
      </div>
    </MainLayout>
  );
}
