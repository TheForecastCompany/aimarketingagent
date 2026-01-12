/**
 * Clean and reformat agent response content for user-friendly display
 */
export interface CleanedContent {
  title: string | null;
  content: string;
  confidencePercentage: string | null;
  proTips: string[] | null;
  hashtags: string[];
}

export function cleanAgentResponse(agentResponse: any): CleanedContent {
  // Extract content from AgentResponse wrapper
  if (!agentResponse?.success) {
    return {
      title: null,
      content: "Content generation failed. Please try again.",
      confidencePercentage: null,
      proTips: null,
      hashtags: []
    };
  }
  
  let rawContent = agentResponse.content || '';
  
  // Handle different content types
  if (typeof rawContent === 'object') {
    rawContent = rawContent.content || JSON.stringify(rawContent);
  } else {
    rawContent = String(rawContent);
  }
  
  // Header Cleanup - Detect and format title
  let title: string | null = null;
  if (rawContent.startsWith('Title:')) {
    const lines = rawContent.split('\n', 1);
    if (lines.length > 1) {
      title = lines[0].replace('Title:', '').trim();
      rawContent = lines[1].trim();
    }
  }
  
  // Visual Formatting - Clean up newlines and spacing
  rawContent = rawContent.replace(/\\n\\n/g, '\n\n'); // Fix double escaped newlines
  rawContent = rawContent.replace(/\\n/g, '\n');     // Fix single escaped newlines
  
  // Ensure proper paragraph spacing
  const paragraphs = rawContent.split('\n\n').map((p: string) => p.trim()).filter((p: string) => p);
  rawContent = paragraphs.join('\n\n');
  
  // Emoji & Hashtag Handling
  const hashtagPattern = /#(\w+)/g;
  const hashtags: string[] = [];
  let match;
  while ((match = hashtagPattern.exec(rawContent)) !== null) {
    hashtags.push(match[1]);
  }
  
  // Remove hashtags from main content
  rawContent = rawContent.replace(hashtagPattern, '').trim();
  
  // Confidence Score Formatting
  let confidencePercentage: string | null = null;
  if (agentResponse.confidence !== undefined) {
    const confidence = agentResponse.confidence;
    if (typeof confidence === 'number') {
      confidencePercentage = `Match Confidence: ${Math.round(confidence * 100)}%`;
    }
  }
  
  // Suggestions Processing
  let proTips: string[] | null = null;
  if (agentResponse.suggestions && Array.isArray(agentResponse.suggestions)) {
    proTips = agentResponse.suggestions.map((suggestion: string) => `• ${suggestion}`);
  }
  
  return {
    title,
    content: rawContent,
    confidencePercentage,
    proTips,
    hashtags
  };
}

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface CleanedContentViewProps {
  agentResponse: any;
}

export function CleanedContentView({ agentResponse }: CleanedContentViewProps) {
  const cleaned = cleanAgentResponse(agentResponse);
  
  return (
    <Card className="border rounded-lg shadow-sm bg-white">
      <div className="p-6">
        {cleaned.title && (
          <h1 className="text-2xl font-bold mb-4 text-gray-900">
            {cleaned.title}
          </h1>
        )}
        
        <div className="prose max-w-none">
          {cleaned.content.split('\n\n').map((paragraph, index) => (
            <p key={index} className="mb-4 leading-relaxed">
              {paragraph}
            </p>
          ))}
        </div>
        
        {cleaned.confidencePercentage && (
          <div className="mt-6 p-3 bg-blue-50 rounded border-l-4 border-blue-200">
            <span className="text-sm font-medium text-blue-800">
              {cleaned.confidencePercentage}
            </span>
          </div>
        )}
        
        {cleaned.hashtags && cleaned.hashtags.length > 0 && (
          <div className="mt-4">
            <div className="flex flex-wrap gap-2">
              {cleaned.hashtags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="px-3 py-1">
                  #{tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {cleaned.proTips && cleaned.proTips.length > 0 && (
          <div className="mt-6 p-4 bg-green-50 rounded border-l-4 border-green-200">
            <h3 className="text-sm font-semibold text-green-800 mb-2">Pro-Tips:</h3>
            <ul className="space-y-1">
              {cleaned.proTips.map((tip, index) => (
                <li key={index} className="text-sm text-green-700">
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}
