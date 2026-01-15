"""
Enhanced AI-Powered Content Summarizer V5
Uses Claude 3.5 Haiku with GPT-4 fallback for article summarization
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

class AISummarizerV5:
    def __init__(self, claude_api_key: str = None, openai_api_key: str = None):
        self.claude_client = None
        self.openai_client = None
        self.model_used = None  # Track which model was used for this session
        
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
    
    def _call_claude(self, prompt: str, max_tokens: int = 1000) -> tuple:
        """Call Claude API - Returns (response_text, model_name)"""
        try:
            model = "claude-3-5-haiku-20241022"  # Claude 3.5 Haiku
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return (response.content[0].text, "Claude 3.5 Haiku")
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return (None, None)
    
    def _call_openai(self, prompt: str, max_tokens: int = 1000) -> tuple:
        """Call OpenAI API - Returns (response_text, model_name)"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return (response.choices[0].message.content, "GPT-4")
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return (None, None)
    
    def _generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using available AI service"""
        # Try Claude first, then OpenAI
        if self.claude_client:
            result, model_name = self._call_claude(prompt, max_tokens)
            if result:
                self.model_used = model_name  # Track which model was used
                return result

        if self.openai_client:
            result, model_name = self._call_openai(prompt, max_tokens)
            if result:
                self.model_used = model_name  # Track which model was used
                return result

        # Fallback to mock response for testing
        self.model_used = "Mock (No API Key)"
        return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing without API keys - clean list format"""
        # Return empty string for mock - better than fake content
        return ""
    
    def create_enhanced_narrative(self, articles: List[Dict[str, Any]],
                                category: str, word_target: int = 300) -> str:
        """Create clean list summary with embedded links"""

        # Skip API call if no articles
        if not articles or len(articles) == 0:
            logger.info(f"Skipping {category} - no articles to summarize")
            return ""
        
        # Professional prompts for different categories
        category_prompts = {
            'ai': """Focus on AI developments with emphasis on practical tools for solo developers and non-technical founders. 
                    Prioritize: text-to-code platforms (Cursor, Replit, Bolt, Lovable, Vercel), low-code tools (Builder.io, Retool), 
                    platform updates with real-world impact, early access/beta releases, and pricing changes. Include brief mentions 
                    of how updates help with debugging, API integration, auth, or deployment. Use professional, measured tone. 
                    Keep sentences concise - 2-3 sentences max per article.""",
            'moonshot_strategy': """Focus on breakthrough innovations, 'impossible' achievements, strategic business moves from major companies, 
                               first principles thinking examples, failed moonshot initiatives and lessons learned. Include major acquisitions, 
                               pivots, public-private partnerships, and coalition building for grand challenges. Cover developments from Google X, 
                               DARPA, and similar moonshot labs. Emphasize teaching moments and strategic implications. Use factual, professional 
                               tone without hyperbole. Every sentence should have 2-3 embedded links.""",
            'tech_headlines': """Focus on major technology company developments, product releases, software/hardware advances, 
                              and industry trends. Use straightforward, professional reporting style. 
                              Every sentence should have 2-3 embedded links.""",
            'market_business': """Focus on strategic business decisions, major acquisitions, pivots, market-moving announcements, 
                              IPOs, significant funding rounds, and strategic partnerships. Prioritize moves that demonstrate strategic 
                              thinking or industry impact. Include brief strategic implications when relevant. Use professional financial 
                              reporting tone. Every sentence should have 2-3 embedded links.""",
            'us_news': """Focus on significant national developments, policy changes, government actions, and major events 
                        while maintaining balanced coverage. Use professional journalistic tone. 
                        Every sentence should have 2-3 embedded links.""",
            'longform_articles': """Focus on analytical pieces, investigative reports, and substantive commentary 
                               from established sources. Use professional, thoughtful tone. 
                               Every sentence should have 2-3 embedded links.""",
            'space_news': """Focus on NASA missions, SpaceX developments, Artemis program updates, space exploration 
                          achievements, satellite launches, and significant space technology advances. Use factual, 
                          professional reporting style. Keep summaries concise - 2-3 sentences max per article.""",
            'higher_education': """Focus on higher education developments with emphasis on Boston-area opportunities, 
                               Babson College news, MIT/Harvard developments, innovation challenges, hackathons, 
                               entrepreneurship events, and AI in education. Prioritize actionable opportunities for 
                               students and faculty within 50 miles of Boston/Cambridge/Worcester area. Use professional 
                               academic tone. Keep summaries concise - 2-3 sentences max per article."""
        }
        
        # Prepare article summaries for AI
        article_summaries = []
        for i, article in enumerate(articles[:8]):  # More articles for better content
            summary = f"Article {i+1}:\n"
            summary += f"Title: {article['title']}\n"
            summary += f"Source: {article['source']}\n"
            summary += f"Link: {article['link']}\n"
            summary += f"Content: {article['content'][:300]}...\n"
            article_summaries.append(summary)
        
        specific_prompt = category_prompts.get(category, 
            "Focus on the key developments in this category. Every sentence should have 2-3 embedded links.")
        
        prompt = f"""
Create a clean list summary for the {category.replace('_', ' ')} category. Requirements:

1. Format each article as a single line item (no bullet character)
2. Use this EXACT format: [Article Title](link) - 1-2 sentence summary of the article. — Source Name
3. Plain link (no bold), followed by a dash, then the summary, ending with em-dash and source
4. Keep summaries factual and concise (1-2 sentences maximum)
5. No editorial commentary or flowery language
6. Include {min(len(articles), 8)} items
7. Add one blank line between each item for spacing

Example of correct format:
[OpenAI launches new safety framework](https://openai.com/...) - OpenAI partnered with AARP to develop AI safety guidelines specifically for older adults online. — OpenAI Blog

[Britain introduces mandatory digital ID](https://reuters.com/...) - UK government announces compulsory digital identity cards for workers, raising privacy concerns. — Reuters

{specific_prompt}

Articles to summarize:
{chr(10).join(article_summaries)}

Generate items in the exact format shown above. Focus on clear, factual summaries with blank lines between items.
"""
        
        return self._generate_text(prompt, max_tokens=word_target + 200)
    
    def create_section_summaries(self, categorized_articles: Dict[str, List[Dict[str, Any]]], 
                                word_targets: Dict[str, int]) -> Dict[str, str]:
        """Create enhanced summaries for all sections"""
        summaries = {}
        
        # Skip categories that don't need AI narrative summaries
        skip_categories = ['on_this_day', 'weather', 'daily_stoicism']
        
        for category, articles in categorized_articles.items():
            if category in skip_categories:
                continue
                
            if category in word_targets:
                logger.info(f"Creating enhanced {category} summary with {len(articles)} articles")
                target_words = word_targets.get(category, 300)
                summaries[category] = self.create_enhanced_narrative(
                    articles, category, target_words
                )
        
        return summaries
    
    def extract_stoicism_quote(self, stoicism_articles: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract a Stoicism quote - uses curated list to avoid API calls"""
        # Use curated quotes instead of AI extraction to save API calls
        quotes = [
            {"quote": "The best revenge is not to be like your enemy.", "author": "Marcus Aurelius"},
            {"quote": "You have power over your mind - not outside events. Realize this, and you will find strength.", "author": "Marcus Aurelius"},
            {"quote": "The happiness of your life depends upon the quality of your thoughts.", "author": "Marcus Aurelius"},
            {"quote": "Wealth consists in not having great possessions, but in having few wants.", "author": "Epictetus"},
            {"quote": "It is impossible for a man to learn what he thinks he already knows.", "author": "Epictetus"},
            {"quote": "We suffer more often in imagination than in reality.", "author": "Seneca"},
            {"quote": "Luck is what happens when preparation meets opportunity.", "author": "Seneca"},
            {"quote": "He who fears death will never do anything worth of a man who is alive.", "author": "Seneca"},
            {"quote": "If it is not right, do not do it. If it is not true, do not say it.", "author": "Marcus Aurelius"},
            {"quote": "The obstacle is the way.", "author": "Marcus Aurelius"}
        ]
        import random
        return random.choice(quotes)

# Test function
if __name__ == "__main__":
    # Test with mock data
    mock_articles = [
        {
            'title': 'Cursor AI Revolutionizes Coding',
            'source': 'Tech News',
            'link': 'https://example.com/cursor',
            'content': 'Cursor, the AI-powered code editor, has introduced new agentic coding features...',
            'relevance_score': 0.9
        },
        {
            'title': 'Claude Code Transforms Development',
            'source': 'AI Weekly',
            'link': 'https://example.com/claude-code',
            'content': 'Anthropic\'s Claude Code is changing how developers interact with AI assistants...',
            'relevance_score': 0.8
        }
    ]
    
    summarizer = AISummarizerV5()  # Will use mock responses
    
    # Test enhanced narrative creation
    summary = summarizer.create_enhanced_narrative(mock_articles, 'ai', 300)
    print("=== ENHANCED AI SUMMARY ===")
    print(summary)
    
    # Test Stoicism quote extraction
    quote = summarizer.extract_stoicism_quote([])
    print(f"\n=== DAILY STOICISM ===")
    print(f'"{quote["quote"]}" - {quote["author"]}')
    
    # Test section summaries
    categorized = {'ai': mock_articles}
    word_targets = {'ai': 300}
    summaries = summarizer.create_section_summaries(categorized, word_targets)
    print(f"\n=== SECTION SUMMARIES ===")
    for category, content in summaries.items():
        print(f"{category}: {len(content.split())} words")