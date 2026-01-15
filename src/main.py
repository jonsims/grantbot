#!/usr/bin/env python3
"""
Daily News Agent - Main Orchestration Script
Coordinates all components to generate daily news updates
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

from collectors.rss_collector import RSSCollector
from collectors.supplementary import SupplementaryCollector
from processors.ai_summarizer import AISummarizer
from generators.markdown import MarkdownGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyNewsAgent:
    def __init__(self, config_path: str = "config/sources.yaml"):
        """Initialize the Daily News Agent"""
        load_dotenv()  # Load environment variables
        
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.rss_collector = RSSCollector()
        self.supplementary_collector = SupplementaryCollector(
            market_api_key=os.getenv('ALPHA_VANTAGE_API_KEY')
        )
        self.ai_summarizer = AISummarizer(
            claude_api_key=os.getenv('CLAUDE_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.markdown_generator = MarkdownGenerator()
        
        logger.info("Daily News Agent initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config_path)
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            # Return minimal config for testing
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for testing"""
        return {
            'categories': {
                'moonshots': {
                    'word_target': 150,
                    'keywords': ['breakthrough', 'innovation'],
                    'sources': [
                        {'name': 'MIT News', 'url': 'https://news.mit.edu/rss/topic/innovation', 'type': 'rss'}
                    ]
                },
                'tech_headlines': {
                    'word_target': 200,
                    'keywords': ['technology', 'AI', 'software'],
                    'sources': [
                        {'name': 'The Verge', 'url': 'https://www.theverge.com/rss/index.xml', 'type': 'rss'}
                    ]
                }
            }
        }
    
    def collect_all_content(self) -> tuple[Dict[str, list], Dict[str, Any]]:
        """Collect content from all sources"""
        logger.info("Starting content collection...")
        
        # Collect RSS articles by category
        categorized_articles = self.rss_collector.collect_by_category(
            self.config.get('categories', {})
        )
        
        # Collect supplementary content
        supplementary_data = self.supplementary_collector.collect_all_supplementary()
        
        # Log collection results
        total_articles = sum(len(articles) for articles in categorized_articles.values())
        logger.info(f"Collected {total_articles} articles across {len(categorized_articles)} categories")
        
        for category, articles in categorized_articles.items():
            logger.info(f"  {category}: {len(articles)} articles")
        
        return categorized_articles, supplementary_data
    
    def generate_summaries(self, categorized_articles: Dict[str, list]) -> Dict[str, str]:
        """Generate AI summaries for all categories"""
        logger.info("Generating AI summaries...")
        
        # Extract word targets from config
        word_targets = {}
        for category, config in self.config.get('categories', {}).items():
            word_targets[category] = config.get('word_target', 150)
        
        summaries = self.ai_summarizer.create_section_summaries(
            categorized_articles, word_targets
        )
        
        logger.info(f"Generated summaries for {len(summaries)} categories")
        return summaries
    
    def generate_daily_update(self, output_dir: str = None) -> str:
        """Generate complete daily update"""
        logger.info("=== Starting Daily News Update Generation ===")
        
        try:
            # Step 1: Collect content
            categorized_articles, supplementary_data = self.collect_all_content()
            
            # Step 2: Generate summaries
            summaries = self.generate_summaries(categorized_articles)
            
            # Step 3: Create article links section
            article_links = self.ai_summarizer.create_article_links_section(categorized_articles)
            
            # Step 4: Generate markdown
            markdown_content = self.markdown_generator.generate_daily_update(
                summaries, categorized_articles, supplementary_data, article_links
            )
            
            # Step 5: Save to file
            if output_dir is None:
                # Default to Daily Updates folder if run from the correct location
                output_dir = "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)"
                if not os.path.exists(output_dir):
                    output_dir = "output"  # Fallback to local output directory
            
            filepath = self.markdown_generator.save_to_file(markdown_content, output_dir)
            
            # Log statistics
            word_count = self.markdown_generator.get_word_count(markdown_content)
            logger.info(f"Daily update generated successfully:")
            logger.info(f"  File: {filepath}")
            logger.info(f"  Word count: {word_count}")
            logger.info(f"  Categories: {len(summaries)}")
            logger.info(f"  Total articles: {sum(len(articles) for articles in categorized_articles.values())}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating daily update: {str(e)}")
            raise
    
    def test_components(self) -> Dict[str, bool]:
        """Test all components for debugging"""
        logger.info("=== Testing All Components ===")
        
        test_results = {}
        
        # Test RSS collector
        try:
            test_articles = self.rss_collector.collect_by_category(
                {'tech_headlines': self.config['categories']['tech_headlines']}
            )
            test_results['rss_collector'] = len(test_articles.get('tech_headlines', [])) > 0
            logger.info(f"RSS Collector: {'✓' if test_results['rss_collector'] else '✗'}")
        except Exception as e:
            test_results['rss_collector'] = False
            logger.error(f"RSS Collector failed: {str(e)}")
        
        # Test supplementary collector
        try:
            supp_data = self.supplementary_collector.collect_all_supplementary()
            test_results['supplementary'] = 'on_this_day' in supp_data
            logger.info(f"Supplementary Collector: {'✓' if test_results['supplementary'] else '✗'}")
        except Exception as e:
            test_results['supplementary'] = False
            logger.error(f"Supplementary Collector failed: {str(e)}")
        
        # Test AI summarizer
        try:
            mock_articles = [{'title': 'Test', 'content': 'Test content', 'source': 'Test', 'link': '#'}]
            summary = self.ai_summarizer.create_narrative_summary(mock_articles, 'test', 50)
            test_results['ai_summarizer'] = len(summary) > 10
            logger.info(f"AI Summarizer: {'✓' if test_results['ai_summarizer'] else '✗'}")
        except Exception as e:
            test_results['ai_summarizer'] = False
            logger.error(f"AI Summarizer failed: {str(e)}")
        
        # Test markdown generator
        try:
            test_content = self.markdown_generator.generate_daily_update(
                {'test': 'Test summary'}, {'test': []}, {}, 'Test links'
            )
            test_results['markdown_generator'] = len(test_content) > 100
            logger.info(f"Markdown Generator: {'✓' if test_results['markdown_generator'] else '✗'}")
        except Exception as e:
            test_results['markdown_generator'] = False
            logger.error(f"Markdown Generator failed: {str(e)}")
        
        return test_results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate daily news update')
    parser.add_argument('--test', action='store_true', help='Test all components')
    parser.add_argument('--output', '-o', help='Output directory for generated file')
    parser.add_argument('--config', '-c', default='config/sources.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    try:
        agent = DailyNewsAgent(config_path=args.config)
        
        if args.test:
            results = agent.test_components()
            print("\n=== Component Test Results ===")
            for component, passed in results.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"{component:20} {status}")
            
            if not all(results.values()):
                print("\n⚠️  Some components failed. Check logs for details.")
                sys.exit(1)
            else:
                print("\n🎉 All components working!")
        else:
            # Generate daily update
            filepath = agent.generate_daily_update(args.output)
            print(f"✅ Daily update generated: {filepath}")
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()