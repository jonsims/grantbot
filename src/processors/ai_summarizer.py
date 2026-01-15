"""
AI-Powered Content Summarizer
Handles article summarization and narrative generation using Claude/OpenAI
"""

import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Support both Claude and OpenAI
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self, claude_api_key: str = None, openai_api_key: str = None):
        self.claude_client = None
        self.openai_client = None
        
        # Initialize Claude if available and API key provided
        if CLAUDE_AVAILABLE and claude_api_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
                logger.info("Claude client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {str(e)}")
        
        # Initialize OpenAI if available and API key provided
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}")
        
        if not self.claude_client and not self.openai_client:
            logger.warning("No AI clients initialized. Using mock responses for testing.")
    
    def _call_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call Claude API"""
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return None
    
    def _call_openai(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
    
    def _generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using available AI service"""
        # Try Claude first, then OpenAI
        if self.claude_client:
            result = self._call_claude(prompt, max_tokens)
            if result:
                return result
        
        if self.openai_client:
            result = self._call_openai(prompt, max_tokens)
            if result:
                return result
        
        # Fallback to mock response for testing
        return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing without API keys"""
        if "moonshot" in prompt.lower():
            return "Recent breakthroughs in [quantum computing](example.com) and [fusion energy](example.com) represent significant progress toward solving grand challenges. MIT researchers announced advances in quantum error correction, while fusion startup Commonwealth Fusion Systems reached new milestones in plasma containment."
        elif "tech" in prompt.lower():
            return "The tech industry saw major developments this week with [Apple's new AI features](example.com) and [Google's quantum chip breakthrough](example.com). Meanwhile, [Microsoft announced](example.com) significant partnerships in the cloud computing space."
        elif "market" in prompt.lower():
            return "Markets showed mixed signals today with the [S&P 500 gaining 0.5%](example.com) while tech stocks faced pressure. [Federal Reserve minutes](example.com) indicated potential rate adjustments, and [major earnings](example.com) from tech giants exceeded expectations."
        else:
            return f"[Mock AI response for testing] - This would be a real AI-generated summary based on the provided articles. Generated at {datetime.now().strftime('%H:%M')}."
    
    def create_narrative_summary(self, articles: List[Dict[str, Any]], 
                                category: str, word_target: int = 150) -> str:
        """Create engaging narrative summary with embedded links"""
        
        if not articles:
            return f"No {category} articles found for today's update."
        
        # Prepare article summaries for AI
        article_summaries = []
        for i, article in enumerate(articles[:5]):  # Top 5 articles
            summary = f"Article {i+1}:\n"
            summary += f"Title: {article['title']}\n"
            summary += f"Source: {article['source']}\n"
            summary += f"Link: {article['link']}\n"
            summary += f"Content: {article['content'][:500]}...\n"
            article_summaries.append(summary)
        
        prompt = f"""
Create an engaging narrative summary for the {category} category. Requirements:

1. Write exactly {word_target} words
2. Use flowing, narrative prose (not bullet points)
3. Embed links naturally within sentences like: "Apple announced [new AI features](link)"
4. Combine information from multiple articles into coherent story
5. Include source attribution within the text
6. Make it engaging and informative

Articles to summarize:
{chr(10).join(article_summaries)}

Write a {word_target}-word narrative summary that flows naturally and includes embedded markdown links to the articles.
"""
        
        return self._generate_text(prompt, max_tokens=word_target + 100)
    
    def create_section_summaries(self, categorized_articles: Dict[str, List[Dict[str, Any]]], 
                                word_targets: Dict[str, int]) -> Dict[str, str]:
        """Create summaries for all sections"""
        summaries = {}
        
        section_prompts = {
            'moonshots': 'Focus on breakthrough technologies, grand challenges, and innovative solutions',
            'strategic_management': 'Focus on business strategy, management frameworks, and organizational insights',
            'tech_headlines': 'Focus on major technology developments, product launches, and industry trends',
            'us_news': 'Focus on important national news while avoiding excessive political coverage',
            'market_business': 'Focus on market movements, business developments, and economic indicators',
            'boston_tech': 'Focus on local Boston/Cambridge tech scene, startups, and innovation'
        }
        
        for category, articles in categorized_articles.items():
            if category in word_targets:
                logger.info(f"Creating {category} summary with {len(articles)} articles")
                target_words = word_targets.get(category, 150)
                summaries[category] = self.create_narrative_summary(
                    articles, category, target_words
                )
        
        return summaries
    
    def create_article_links_section(self, categorized_articles: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create the article links reference section"""
        links_by_category = []
        
        for category, articles in categorized_articles.items():
            if articles:
                category_name = category.replace('_', ' ').title()
                links_by_category.append(f"### {category_name}")
                
                for article in articles[:3]:  # Top 3 per category
                    source = article.get('source', 'Unknown')
                    title = article.get('title', 'Untitled')
                    link = article.get('link', '#')
                    links_by_category.append(f"- [{title}]({link}) - *{source}*")
                
                links_by_category.append("")  # Empty line between categories
        
        return "\n".join(links_by_category)

# Test function
if __name__ == "__main__":
    # Test with mock data
    mock_articles = [
        {
            'title': 'MIT Breakthrough in Quantum Computing',
            'source': 'MIT News',
            'link': 'https://example.com/mit-quantum',
            'content': 'Researchers at MIT have developed a new approach to quantum error correction...',
            'relevance_score': 0.9
        },
        {
            'title': 'Fusion Energy Milestone Reached',
            'source': 'Nature',
            'link': 'https://example.com/fusion-breakthrough',
            'content': 'A major milestone in fusion energy has been achieved by scientists...',
            'relevance_score': 0.8
        }
    ]
    
    summarizer = AISummarizer()  # Will use mock responses
    
    # Test narrative creation
    summary = summarizer.create_narrative_summary(mock_articles, 'moonshots', 150)
    print("=== SAMPLE NARRATIVE SUMMARY ===")
    print(summary)
    
    # Test article links
    categorized = {'moonshots': mock_articles}
    links = summarizer.create_article_links_section(categorized)
    print("\n=== SAMPLE ARTICLE LINKS ===")
    print(links)