#!/usr/bin/env python3
"""
Daily News Agent V2 - Enhanced Main Orchestration Script
Implements new section structure, enhanced linking, and 2000-word targets
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.rss_collector_enhanced import EnhancedRSSCollector as RSSCollector
from collectors.supplementary import SupplementaryCollector
from collectors.weather_api import WeatherCollector
from collectors.on_this_day_api import OnThisDayCollector
from processors.ai_summarizer_v2 import AISummarizerV2
from generators.markdown_v2 import MarkdownGeneratorV2
from utils.email_sender import EmailSender
from utils.content_filter import ContentFilter
from utils.deduplication import ArticleDeduplicator
from utils.version import VersionManager

# Import caching utilities
try:
    from utils.cache import APIResponseCache, ContentCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyNewsAgentV2:
    def __init__(self, config_path: str = "config/sources-v2.yaml", use_cache: bool = True):
        """Initialize the Enhanced Daily News Agent"""
        load_dotenv()  # Load environment variables
        
        self.config_path = config_path
        self.config = self._load_config()
        self.use_cache = use_cache and CACHE_AVAILABLE
        
        # Initialize caching if available
        if self.use_cache:
            self.api_cache = APIResponseCache(cache_dir="cache/api")
            self.content_cache = ContentCache(cache_dir="cache/content")
            logger.info("Caching enabled")
        else:
            self.api_cache = None
            self.content_cache = None
        
        # Initialize components with V2 versions
        self.rss_collector = RSSCollector()
        self.supplementary_collector = SupplementaryCollector(
            market_api_key=os.getenv('ALPHA_VANTAGE_API_KEY')
        )
        self.weather_collector = WeatherCollector()
        self.otd_collector = OnThisDayCollector()
        self.ai_summarizer = AISummarizerV2(
            claude_api_key=os.getenv('CLAUDE_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.markdown_generator = MarkdownGeneratorV2()
        
        # Initialize email sender, content filter, deduplicator, and version manager
        self.email_sender = EmailSender()
        self.content_filter = ContentFilter()
        self.deduplicator = ArticleDeduplicator()
        self.version_manager = VersionManager()

        logger.info(f"Daily News Agent V2 initialized - {self.version_manager.get_version_string()}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config_path)
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration V2 loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            # Return minimal config for testing
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for testing"""
        return {
            'categories': {
                'ai': {
                    'word_target': 400,
                    'keywords': ['AI', 'artificial intelligence'],
                    'sources': [
                        {'name': 'Test Source', 'url': 'https://example.com/rss', 'type': 'rss'}
                    ]
                }
            }
        }

    def _consolidate_categories(self, categorized_articles: Dict[str, list]) -> Dict[str, list]:
        """Consolidate old categories into new streamlined structure"""
        consolidated = {}

        # AI & Technology: merge ai + tech_tools + tech_headlines
        ai_tech_articles = []
        ai_tech_articles.extend(categorized_articles.get('ai', []))
        ai_tech_articles.extend(categorized_articles.get('tech_tools', []))
        ai_tech_articles.extend(categorized_articles.get('tech_headlines', []))
        if ai_tech_articles:
            consolidated['ai_technology'] = ai_tech_articles

        # Academia & Research: merge academic_research + higher_education
        academia_articles = []
        academia_articles.extend(categorized_articles.get('academic_research', []))
        academia_articles.extend(categorized_articles.get('higher_education', []))
        if academia_articles:
            consolidated['academia_research'] = academia_articles

        # Reddit Highlights: consolidate from_reddit
        reddit_articles = categorized_articles.get('from_reddit', [])
        if reddit_articles:
            consolidated['reddit_highlights'] = reddit_articles

        # Keep these categories as-is
        for category in ['moonshot_strategy', 'market_business', 'us_news', 'space_news',
                        'longform_articles', 'agentic_coding', 'daily_stoicism', 'on_this_day', 'weather']:
            if category in categorized_articles and categorized_articles[category]:
                consolidated[category] = categorized_articles[category]

        logger.info(f"Consolidated {len(categorized_articles)} categories into {len(consolidated)} categories")
        return consolidated

    def collect_all_content(self) -> tuple[Dict[str, list], Dict[str, Any]]:
        """Collect content from all sources with enhanced categories"""
        logger.info("Starting enhanced content collection...")
        
        # Collect RSS articles by category (using enhanced concurrent method)
        categorized_articles = self.rss_collector.collect_by_category_concurrent(
            self.config.get('categories', {})
        )
        
        # Apply content filters to remove unwanted articles
        logger.info("Applying content filters...")
        categorized_articles = self.content_filter.filter_categorized_articles(categorized_articles)

        # Remove duplicate articles
        logger.info("Removing duplicate articles...")
        categorized_articles = self.deduplicator.filter_categorized_articles(categorized_articles)

        # Consolidate categories into new structure
        categorized_articles = self._consolidate_categories(categorized_articles)

        # Collect supplementary content
        supplementary_data = self.supplementary_collector.collect_all_supplementary()
        
        # Add Stoicism quote extraction
        stoicism_articles = categorized_articles.get('daily_stoicism', [])
        supplementary_data['stoicism_quote'] = self.ai_summarizer.extract_stoicism_quote(stoicism_articles)
        
        # Add weather forecast for 01701
        supplementary_data['weather'] = self.weather_collector.get_weather_forecast("01701")
        
        # Add "On This Day" historical events
        supplementary_data['on_this_day'] = self.otd_collector.get_events_for_today()
        
        # Log collection results
        total_articles = sum(len(articles) for articles in categorized_articles.values())
        logger.info(f"Collected {total_articles} articles across {len(categorized_articles)} categories")
        
        for category, articles in categorized_articles.items():
            if articles:  # Only log categories with content
                logger.info(f"  {category}: {len(articles)} articles")
        
        return categorized_articles, supplementary_data
    
    def generate_enhanced_summaries(self, categorized_articles: Dict[str, list]) -> Dict[str, str]:
        """Generate AI summaries with enhanced linking and longer word counts"""
        logger.info("Generating enhanced AI summaries...")
        
        # Check cache first if available
        if self.use_cache:
            cache_key = f"summaries_{datetime.now().strftime('%Y-%m-%d')}"
            cached = self.api_cache.get(cache_key)
            if cached:
                logger.info("Using cached AI summaries")
                return cached
        
        # New word targets for consolidated categories
        word_targets = {
            'ai_technology': 600,         # Merged AI + tech - increased
            'moonshot_strategy': 300,     # High priority
            'market_business': 300,       # High priority
            'academia_research': 400,     # Merged academic + higher ed
            'space_news': 200,            # New section
            'us_news': 200,               # Medium priority
            'longform_articles': 200,     # Medium priority
            'agentic_coding': 400,        # Reddit + articles for AI coding
            'reddit_highlights': 200,     # Consolidated Reddit
            'on_this_day': 50,           # Brief
            'weather': 30,               # Very brief
            'daily_stoicism': 50,        # Brief
            # academic_research uses bullet format, no word target needed
        }
        
        summaries = self.ai_summarizer.create_section_summaries(
            categorized_articles, word_targets
        )
        
        # Cache the summaries if caching is enabled
        if self.use_cache:
            cache_key = f"summaries_{datetime.now().strftime('%Y-%m-%d')}"
            self.api_cache.set(cache_key, summaries, ttl_hours=24)
            logger.info("Cached AI summaries for 24 hours")
        
        logger.info(f"Generated enhanced summaries for {len(summaries)} categories")
        return summaries
    
    def generate_daily_update(self, output_dir: str = None, test_mode: bool = False) -> str:
        """Generate complete enhanced daily update"""
        mode_str = "TEST" if test_mode else "PRODUCTION"
        logger.info(f"=== Starting Enhanced Daily News Update Generation ({mode_str}) ===")

        try:
            # Step 1: Collect content
            categorized_articles, supplementary_data = self.collect_all_content()

            # Step 2: Generate enhanced summaries
            summaries = self.generate_enhanced_summaries(categorized_articles)

            # Step 3: Generate V2 markdown with version and test mode
            markdown_content = self.markdown_generator.generate_daily_update(
                summaries, categorized_articles, supplementary_data,
                version=self.version_manager.get_version_string(),
                test_mode=test_mode
            )
            
            # Step 4: Save to file
            if output_dir is None:
                # Default to Published Updates folder inside the repository
                # This works both locally and in GitHub Actions
                script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                output_dir = os.path.join(script_dir, "Published Updates")

                # Create directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
            
            filepath = self.markdown_generator.save_to_file(markdown_content, output_dir)
            
            # Step 5: Send email (if configured)
            if self.email_sender.enabled:
                # Get source label from environment variable (default to "Local")
                source_label = os.getenv('UPDATE_SOURCE', 'Local')
                email_sent = self.email_sender.send_daily_update(
                    markdown_content,
                    source_label=source_label
                )
                if email_sent:
                    logger.info(f"Daily update emailed successfully ({source_label})")
            
            # Log enhanced statistics
            word_count = len(markdown_content.split())
            total_articles = sum(len(articles) for articles in categorized_articles.values())
            active_categories = len([cat for cat, articles in categorized_articles.items() if articles])
            
            logger.info(f"Enhanced daily update generated successfully:")
            logger.info(f"  File: {filepath}")
            logger.info(f"  Word count: {word_count} (target: ~2000)")
            logger.info(f"  Active categories: {active_categories}/11")
            logger.info(f"  Total articles: {total_articles}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating enhanced daily update: {str(e)}")
            raise
    
    def test_components_v2(self) -> Dict[str, bool]:
        """Test all V2 components for debugging"""
        logger.info("=== Testing All V2 Components ===")
        
        test_results = {}
        
        # Test RSS collector with new categories
        try:
            test_categories = {
                'ai': self.config['categories'].get('ai', {}),
                'tech_headlines': self.config['categories'].get('tech_headlines', {})
            }
            test_articles = self.rss_collector.collect_by_category_concurrent(test_categories)
            test_results['rss_collector_v2'] = len(test_articles.get('ai', [])) > 0 or len(test_articles.get('tech_headlines', [])) > 0
            logger.info(f"RSS Collector V2: {'✓' if test_results['rss_collector_v2'] else '✗'}")
        except Exception as e:
            test_results['rss_collector_v2'] = False
            logger.error(f"RSS Collector V2 failed: {str(e)}")
        
        # Test enhanced AI summarizer
        try:
            mock_articles = [{'title': 'Test AI Article', 'content': 'AI developments...', 'source': 'Test', 'link': '#'}]
            summary = self.ai_summarizer.create_enhanced_narrative(mock_articles, 'ai', 300)
            test_results['ai_summarizer_v2'] = len(summary) > 50
            logger.info(f"AI Summarizer V2: {'✓' if test_results['ai_summarizer_v2'] else '✗'}")
        except Exception as e:
            test_results['ai_summarizer_v2'] = False
            logger.error(f"AI Summarizer V2 failed: {str(e)}")
        
        # Test V2 markdown generator
        try:
            test_content = self.markdown_generator.generate_daily_update(
                {'ai': 'Test AI summary with [embedded links](example.com)'}, 
                {'ai': []}, 
                {'stoicism_quote': {'quote': 'Test quote', 'author': 'Test author'}}
            )
            test_results['markdown_generator_v2'] = len(test_content) > 200
            logger.info(f"Markdown Generator V2: {'✓' if test_results['markdown_generator_v2'] else '✗'}")
        except Exception as e:
            test_results['markdown_generator_v2'] = False
            logger.error(f"Markdown Generator V2 failed: {str(e)}")
        
        return test_results

def main():
    """Main entry point for V2"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate enhanced daily news update')
    parser.add_argument('--test', action='store_true', help='Generate test update (adds "Test" to title)')
    parser.add_argument('--test-components', action='store_true', help='Test all V2 components')
    parser.add_argument('--output', '-o', help='Output directory for generated file')
    parser.add_argument('--config', '-c', default='config/sources-v2.yaml', help='Config file path')

    args = parser.parse_args()

    try:
        agent = DailyNewsAgentV2(config_path=args.config)

        if args.test_components:
            results = agent.test_components_v2()
            print("\n=== V2 Component Test Results ===")
            for component, passed in results.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"{component:25} {status}")

            if not all(results.values()):
                print("\n⚠️  Some V2 components failed. Check logs for details.")
                sys.exit(1)
            else:
                print("\n🎉 All V2 components working!")
        else:
            # Generate enhanced daily update (test mode if --test flag is used)
            filepath = agent.generate_daily_update(args.output, test_mode=args.test)
            mode_str = "TEST" if args.test else "PRODUCTION"
            print(f"✅ Enhanced daily update generated ({mode_str}): {filepath}")
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()