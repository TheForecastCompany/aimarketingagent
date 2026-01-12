import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CleanedContent:
    """Cleaned and formatted content for display"""
    title: Optional[str] = None
    content: str = ""
    confidence_percentage: Optional[str] = None
    pro_tips: Optional[list] = None
    hashtags: Optional[list] = None

def clean_agent_response(agent_response: Dict[str, Any]) -> CleanedContent:
    """
    Clean and reformat agent response content for user-friendly display.
    
    Args:
        agent_response: Raw AgentResponse dictionary
        
    Returns:
        CleanedContent: Formatted content ready for UI display
    """
    # Extract content from AgentResponse wrapper
    if not agent_response.get('success', False):
        return CleanedContent(content="Content generation failed. Please try again.")
    
    raw_content = agent_response.get('content', '')
    
    # Handle different content types
    if isinstance(raw_content, dict):
        # If content is a dict, extract the main text content
        content_text = raw_content.get('content', str(raw_content))
    else:
        content_text = str(raw_content)
    
    # 1. Header Cleanup - Detect and format title
    title = None
    if content_text.startswith('Title:'):
        lines = content_text.split('\n', 1)
        if len(lines) > 1:
            title = lines[0].replace('Title:', '').strip()
            content_text = lines[1].strip()
    
    # 2. Visual Formatting - Clean up newlines and spacing
    content_text = re.sub(r'\\n\\n', '\n\n', content_text)  # Fix double escaped newlines
    content_text = re.sub(r'\\n', '\n', content_text)     # Fix single escaped newlines
    
    # Ensure proper paragraph spacing
    paragraphs = content_text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    content_text = '\n\n'.join(paragraphs)
    
    # 3. Emoji & Hashtag Handling
    hashtags = []
    hashtag_pattern = r'#(\w+)'
    found_hashtags = re.findall(hashtag_pattern, content_text)
    if found_hashtags:
        hashtags = found_hashtags
        # Remove hashtags from main content
        content_text = re.sub(hashtag_pattern, '', content_text).strip()
    
    # 4. Confidence Score Formatting
    confidence_percentage = None
    if 'confidence' in agent_response:
        confidence = agent_response['confidence']
        if isinstance(confidence, (int, float)):
            confidence_percentage = f"Match Confidence: {int(confidence * 100)}%"
    
    # 5. Suggestions Processing
    pro_tips = None
    if 'suggestions' in agent_response and agent_response['suggestions']:
        suggestions = agent_response['suggestions']
        if isinstance(suggestions, list):
            pro_tips = [f"• {suggestion}" for suggestion in suggestions]
    
    return CleanedContent(
        title=title,
        content=content_text,
        confidence_percentage=confidence_percentage,
        pro_tips=pro_tips,
        hashtags=hashtags
    )

# JavaScript/TypeScript version for frontend
def generate_content_cleaner_js():
    """
    Generate JavaScript function for content cleaning in frontend
    """
    return '''
/**
 * Clean and reformat agent response content for user-friendly display
 */
export function cleanAgentResponse(agentResponse) {
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
    let title = null;
    if (rawContent.startsWith('Title:')) {
        const lines = rawContent.split('\\n', 1);
        if (lines.length > 1) {
            title = lines[0].replace('Title:', '').trim();
            rawContent = lines[1].trim();
        }
    }
    
    // Visual Formatting - Clean up newlines and spacing
    rawContent = rawContent.replace(/\\\\n\\\\n/g, '\\n\\n'); // Fix double escaped newlines
    rawContent = rawContent.replace(/\\\\n/g, '\\n');     // Fix single escaped newlines
    
    // Ensure proper paragraph spacing
    const paragraphs = rawContent.split('\\n\\n').map(p => p.trim()).filter(p => p);
    rawContent = paragraphs.join('\\n\\n');
    
    // Emoji & Hashtag Handling
    const hashtagPattern = /#(\\w+)/g;
    const hashtags = [];
    let match;
    while ((match = hashtagPattern.exec(rawContent)) !== null) {
        hashtags.push(match[1]);
    }
    
    // Remove hashtags from main content
    rawContent = rawContent.replace(hashtagPattern, '').trim();
    
    // Confidence Score Formatting
    let confidencePercentage = null;
    if (agentResponse.confidence !== undefined) {
        const confidence = agentResponse.confidence;
        if (typeof confidence === 'number') {
            confidencePercentage = `Match Confidence: ${Math.round(confidence * 100)}%`;
        }
    }
    
    // Suggestions Processing
    let proTips = null;
    if (agentResponse.suggestions && Array.isArray(agentResponse.suggestions)) {
        proTips = agentResponse.suggestions.map(suggestion => `• ${suggestion}`);
    }
    
    return {
        title,
        content: rawContent,
        confidencePercentage,
        proTips,
        hashtags
    };
}

/**
 * React component for displaying cleaned content
 */
export function CleanedContentView({ agentResponse }) {
    const cleaned = cleanAgentResponse(agentResponse);
    
    return (
        <div className="cleaned-content-card border rounded-lg p-6 shadow-sm bg-white">
            {cleaned.title && (
                <h1 className="text-2xl font-bold mb-4 text-gray-900">
                    {cleaned.title}
                </h1>
            )}
            
            <div className="prose max-w-none">
                {cleaned.content.split('\\n\\n').map((paragraph, index) => (
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
                            <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                #{tag}
                            </span>
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
    );
}
'''

# Example usage
if __name__ == "__main__":
    # Example agent response
    example_response = {
        "success": True,
        "content": "Title: Amazing Content Strategy\\n\\nThis is a comprehensive content strategy that will help your business grow. #marketing #strategy\\n\\nKey points include engagement and reach optimization.",
        "confidence": 0.85,
        "suggestions": ["Add more specific examples", "Include metrics", "Consider target audience"]
    }
    
    cleaned = clean_agent_response(example_response)
    print("=== Cleaned Content ===")
    print(f"Title: {cleaned.title}")
    print(f"Content: {cleaned.content}")
    print(f"Confidence: {cleaned.confidence_percentage}")
    print(f"Hashtags: {cleaned.hashtags}")
    print(f"Pro-Tips: {cleaned.pro_tips}")
