#!/usr/bin/env python3
"""
Daily News Agent V3 - Discovery Edition
Focus on novel, intellectually stimulating content with rich narratives
"""

import os
import sys
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.rss_collector_enhanced import EnhancedRSSCollector
from collectors.supplementary import SupplementaryCollector
from processors.ai_summarizer_v2 import AISummarizerV2
from generators.markdown_v3 import MarkdownGeneratorV3
from processors.narrative_enhancer import NarrativeEnhancer
from utils.content_filter import ContentFilter
from utils.email_sender import EmailSender
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyNewsAgentV3:
    def __init__(self, config_path: str = "config/sources-v2.yaml", enable_cache: bool = True):
        """Initialize v3 agent with discovery focus"""
        logger.info("Initializing Daily News Agent V3 - Discovery Edition")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.enable_cache = enable_cache
        self.cache_file = "cache/daily_cache_v3.pkl"
        
        # Initialize components
        self.rss_collector = EnhancedRSSCollector()
        self.supplementary_collector = SupplementaryCollector(self.config)
        self.ai_summarizer = AISummarizerV2(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.markdown_generator = MarkdownGeneratorV3()
        self.narrative_enhancer = NarrativeEnhancer()
        self.content_filter = ContentFilter()
        self.email_sender = EmailSender(
            sender_email=os.getenv("EMAIL_ADDRESS"),
            sender_password=os.getenv("EMAIL_PASSWORD")
        )
        
        logger.info("Daily News Agent V3 initialized")
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration V3 loaded from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
    def _load_cache(self) -> dict:
        """Load cached data if available and recent"""
        if not self.enable_cache:
            return None
            
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                
                # Check if cache is from today
                cache_date = cache_data.get('date')
                if cache_date and cache_date.date() == datetime.now().date():
                    logger.info("Using cached data from today")
                    return cache_data
                else:
                    logger.info("Cache is outdated, will refresh")
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
        
        return None
    
    def _save_cache(self, data: dict):
        """Save data to cache"""
        if not self.enable_cache:
            return
            
        try:
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            data['date'] = datetime.now()
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info("Cache saved successfully")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def collect_content(self) -> tuple:
        """Collect content with focus on discovery"""
        logger.info("Starting discovery-focused content collection...")
        
        # Check cache first
        cache_data = self._load_cache()
        if cache_data:
            return (
                cache_data['categorized_articles'],
                cache_data['supplementary_data']
            )
        
        # Collect from RSS feeds
        categories = self.config.get('categories', {})
        categorized_articles = self.rss_collector.collect_by_category_concurrent(categories)
        
        # Apply initial content filtering
        logger.info("Applying discovery-focused content filters...")
        for category in list(categorized_articles.keys()):
            if category in categorized_articles:
                filtered = self.content_filter.filter_articles(
                    categorized_articles[category]
                )
                original_count = len(categorized_articles[category])
                categorized_articles[category] = filtered
                
                if len(filtered) != original_count:
                    removed = original_count - len(filtered)
                    logger.info(f"  {category}: Removed {removed} mainstream articles")
        
        # Filter by novelty scores
        logger.info("Scoring articles for novelty and interest...")
        categorized_articles = self.narrative_enhancer.filter_by_novelty(categorized_articles)
        
        # Collect supplementary data
        supplementary_data = self.supplementary_collector.collect_all_supplementary()
        
        # Log discovery statistics
        total_articles = sum(len(articles) for articles in categorized_articles.values())
        high_novelty = sum(
            1 for cat_articles in categorized_articles.values()
            for article in cat_articles
            if article.get('novelty_score', 0) > 2.0
        )
        logger.info(f"Collected {total_articles} articles, {high_novelty} with high novelty scores")
        
        # Save to cache
        self._save_cache({
            'categorized_articles': categorized_articles,
            'supplementary_data': supplementary_data
        })
        
        return categorized_articles, supplementary_data
    
    def generate_summaries(self, categorized_articles: dict) -> dict:
        """Generate AI summaries with discovery focus"""
        logger.info("Generating discovery-focused AI summaries...")
        
        summaries = {}
        
        # Focus on high-priority categories
        priority_categories = [
            'moonshot_strategy',
            'ai',
            'academic_research',
            'space_news',
            'longform_articles'
        ]
        
        for category in priority_categories:
            if category in categorized_articles and categorized_articles[category]:
                logger.info(f"  Generating enhanced summary for {category}")
                
                # Create discovery-focused prompt
                prompt = f"""
                Analyze these {category} articles and create a narrative that:
                1. Identifies the most novel and surprising insights
                2. Connects dots between different developments
                3. Explains why these discoveries matter
                4. Highlights counterintuitive findings
                
                Focus on substance over hype. Be specific about breakthroughs.
                Write 2-3 paragraphs that tell a cohesive story.
                """
                
                summary = self.ai_summarizer.create_enhanced_narrative(
                    categorized_articles[category][:10],
                    category
                )
                summaries[category] = summary
        
        return summaries
    
    def run(self) -> str:
        """Run the v3 daily news agent"""
        logger.info("=== Starting Daily Discoveries Generation (V3) ===")
        
        try:
            # Collect content
            categorized_articles, supplementary_data = self.collect_content()
            
            # Log category distribution
            for category, articles in categorized_articles.items():
                if articles:
                    logger.info(f"  {category}: {len(articles)} articles")
            
            # Generate AI summaries (optional - narratives work without them)
            summaries = {}
            if os.getenv("OPENAI_API_KEY"):
                logger.info("Generating enhanced AI summaries...")
                summaries = self.generate_summaries(categorized_articles)
            else:
                logger.info("Skipping AI summaries (no API key)")
            
            # Generate markdown with enhanced narratives
            markdown_content = self.markdown_generator.generate_daily_update(
                summaries,
                categorized_articles,
                supplementary_data
            )
            
            # Save to file
            filepath = self.markdown_generator.save_to_file(markdown_content)
            
            # Send email
            if os.getenv("EMAIL_ADDRESS"):
                recipient = os.getenv("RECIPIENT_EMAIL", os.getenv("EMAIL_ADDRESS"))
                subject = f"Morning Discoveries - {datetime.now().strftime('%A, %B %d')}"
                
                # Add custom CSS for v3
                html_content = self.email_sender._markdown_to_html(markdown_content)
                
                self.email_sender.send_email(
                    recipient=recipient,
                    subject=subject,
                    html_body=html_content
                )
                logger.info(f"Discovery digest emailed to {recipient}")
            
            # Log completion
            word_count = len(markdown_content.split())
            logger.info(f"Daily discoveries generated successfully:")
            logger.info(f"  File: {filepath}")
            logger.info(f"  Word count: {word_count}")
            logger.info(f"  Focus: Novel discoveries and insights")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating daily discoveries: {str(e)}")
            raise

def main():
    """Main entry point for v3"""
    try:
        # Check for required environment variables
        required_vars = ["EMAIL_ADDRESS", "EMAIL_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            logger.warning("Email sending will be disabled")
        
        # Initialize and run agent
        agent = DailyNewsAgentV3(enable_cache=True)
        filepath = agent.run()
        
        print(f"\n✅ Daily discoveries generated: {filepath}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()