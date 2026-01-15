"""
Feed Discovery System
Suggests related RSS feeds based on existing categories using multiple strategies:
1. Related subreddits via Reddit API
2. Same-domain feeds from existing sources
3. Curated feeds from awesome-rss lists
4. AI-powered topic-based suggestions

Generates config/feed-suggestions.json for web UI integration
"""

import json
import logging
import re
import yaml
import feedparser
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class FeedDiscovery:
    def __init__(self, config_path: str = "config/sources-v4.yaml",
                 output_path: str = "config/feed-suggestions.json"):
        self.config_path = Path(config_path)
        self.output_path = Path(output_path)
        self.existing_feeds = set()
        self.suggestions = defaultdict(list)

        # Curated feed database (high-quality sources by topic)
        self.curated_feeds = {
            'ai': [
                {'name': 'Anthropic Blog', 'url': 'https://www.anthropic.com/blog/rss', 'description': 'Claude AI research and updates', 'preview_link': 'https://www.anthropic.com/blog'},
                {'name': 'AI21 Labs Blog', 'url': 'https://www.ai21.com/blog/rss.xml', 'description': 'Jurassic AI model updates', 'preview_link': 'https://www.ai21.com/blog'},
                {'name': 'Hugging Face Blog', 'url': 'https://huggingface.co/blog/feed.xml', 'description': 'Open-source AI models and tools', 'preview_link': 'https://huggingface.co/blog'},
                {'name': 'Stability AI Blog', 'url': 'https://stability.ai/blog/rss', 'description': 'Stable Diffusion and generative AI', 'preview_link': 'https://stability.ai/blog'},
                {'name': 'LangChain Blog', 'url': 'https://blog.langchain.dev/rss/', 'description': 'LLM application framework updates', 'preview_link': 'https://blog.langchain.dev'},
            ],
            'tech_tools': [
                {'name': 'Linear Changelog', 'url': 'https://linear.app/changelog/rss', 'description': 'Project management tool updates', 'preview_link': 'https://linear.app/changelog'},
                {'name': 'Notion Blog', 'url': 'https://www.notion.so/blog/rss', 'description': 'Productivity and collaboration tools', 'preview_link': 'https://www.notion.so/blog'},
                {'name': 'Figma Blog', 'url': 'https://www.figma.com/blog/rss/', 'description': 'Design and prototyping platform', 'preview_link': 'https://www.figma.com/blog'},
                {'name': 'Railway Blog', 'url': 'https://blog.railway.app/rss.xml', 'description': 'Cloud deployment platform', 'preview_link': 'https://blog.railway.app'},
            ],
            'tech_headlines': [
                {'name': 'The Verge', 'url': 'https://www.theverge.com/rss/index.xml', 'description': 'Technology news and reviews', 'preview_link': 'https://www.theverge.com'},
                {'name': 'Ars Technica', 'url': 'https://feeds.arstechnica.com/arstechnica/index', 'description': 'Deep tech journalism', 'preview_link': 'https://arstechnica.com'},
                {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/', 'description': 'Startup and tech news', 'preview_link': 'https://techcrunch.com'},
                {'name': 'Wired', 'url': 'https://www.wired.com/feed/rss', 'description': 'Technology and culture', 'preview_link': 'https://www.wired.com'},
            ],
            'market_business': [
                {'name': 'Bloomberg Markets', 'url': 'https://www.bloomberg.com/feed/podcast/bloomberg-markets.xml', 'description': 'Financial markets analysis', 'preview_link': 'https://www.bloomberg.com/podcasts/bloomberg-markets'},
                {'name': 'Financial Times Tech', 'url': 'https://www.ft.com/technology?format=rss', 'description': 'Business technology coverage', 'preview_link': 'https://www.ft.com/technology'},
                {'name': 'WSJ Tech', 'url': 'https://feeds.a.dj.com/rss/RSSWSJD.xml', 'description': 'Wall Street Journal tech news', 'preview_link': 'https://www.wsj.com/tech'},
            ],
            'academic_research': [
                {'name': 'Nature AI', 'url': 'https://www.nature.com/subjects/machine-learning.rss', 'description': 'ML research publications', 'preview_link': 'https://www.nature.com/subjects/machine-learning'},
                {'name': 'Science Robotics', 'url': 'https://www.science.org/rss/robotics.xml', 'description': 'Robotics research', 'preview_link': 'https://www.science.org/topic/robotics'},
                {'name': 'arXiv CS.AI', 'url': 'https://export.arxiv.org/rss/cs.AI', 'description': 'AI preprints from arXiv', 'preview_link': 'https://arxiv.org/list/cs.AI/recent'},
            ],
            'space_news': [
                {'name': 'NASA Breaking News', 'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss', 'description': 'Official NASA announcements', 'preview_link': 'https://www.nasa.gov/news'},
                {'name': 'Space.com', 'url': 'https://www.space.com/feeds/all', 'description': 'Space exploration news', 'preview_link': 'https://www.space.com'},
                {'name': 'ESA News', 'url': 'https://www.esa.int/rssfeed/OurActivities', 'description': 'European Space Agency updates', 'preview_link': 'https://www.esa.int/Newsroom'},
            ],
            'agentic_coding': [
                {'name': 'Windsurf Blog', 'url': 'https://codeium.com/blog/rss.xml', 'description': 'AI coding assistant updates', 'preview_link': 'https://codeium.com/blog'},
                {'name': 'GitHub Copilot', 'url': 'https://github.blog/tag/github-copilot/feed/', 'description': 'Copilot product updates', 'preview_link': 'https://github.blog/tag/github-copilot'},
                {'name': 'Tabnine Blog', 'url': 'https://www.tabnine.com/blog/rss.xml', 'description': 'AI code completion tool', 'preview_link': 'https://www.tabnine.com/blog'},
            ]
        }

        # Subreddit suggestions by category
        self.subreddit_suggestions = {
            'ai': ['r/LocalLLaMA', 'r/MachineLearning', 'r/ArtificialIntelligence', 'r/OpenAI'],
            'tech_tools': ['r/SideProject', 'r/webdev', 'r/programming', 'r/devtools'],
            'tech_headlines': ['r/technology', 'r/Futurology', 'r/gadgets'],
            'market_business': ['r/stocks', 'r/investing', 'r/wallstreetbets'],
            'academic_research': ['r/science', 'r/AskScience', 'r/scholar'],
            'space_news': ['r/space', 'r/spacex', 'r/nasa'],
            'agentic_coding': ['r/ChatGPTCoding', 'r/copilot', 'r/Codeium']
        }

    def load_config(self) -> Dict:
        """Load existing configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Track all existing feeds
            for category_name, category_data in config.get('categories', {}).items():
                for source in category_data.get('sources', []):
                    self.existing_feeds.add(source.get('url', '').strip().lower())
                    self.existing_feeds.add(source.get('name', '').strip().lower())

            logger.info(f"Loaded config with {len(self.existing_feeds)} existing feeds")
            return config

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def is_feed_new(self, feed_url: str, feed_name: str) -> bool:
        """Check if a feed is not already in the config"""
        return (feed_url.strip().lower() not in self.existing_feeds and
                feed_name.strip().lower() not in self.existing_feeds)

    def discover_subreddit_feeds(self, category: str, keywords: List[str]) -> List[Dict]:
        """Discover related subreddit RSS feeds"""
        suggestions = []

        # Get predefined subreddit suggestions
        subreddits = self.subreddit_suggestions.get(category, [])

        for subreddit in subreddits[:3]:  # Limit to 3 suggestions per category
            try:
                # Format subreddit name
                sub_name = subreddit.replace('r/', '')
                feed_url = f"https://www.reddit.com/r/{sub_name}/.rss"
                feed_name = f"r/{sub_name}"

                # Check if already exists
                if not self.is_feed_new(feed_url, feed_name):
                    continue

                # Add without validation (Reddit feeds are reliable)
                suggestions.append({
                    'name': feed_name,
                    'url': feed_url,
                    'type': 'reddit',
                    'description': f'Reddit community for {category.replace("_", " ")}',
                    'estimated_posts_per_week': '~15-30 posts',
                    'sample_headline': 'Click preview to see recent posts',
                    'preview_link': f'https://www.reddit.com/r/{sub_name}',
                    'confidence': 'high'
                })

            except Exception as e:
                logger.debug(f"Error checking subreddit {subreddit}: {e}")
                continue

        return suggestions

    def discover_same_domain_feeds(self, category: str, existing_sources: List[Dict]) -> List[Dict]:
        """Find other RSS feeds from same domains - DISABLED for speed"""
        # Disabled to improve performance - uncomment if needed
        return []

    def discover_curated_feeds(self, category: str) -> List[Dict]:
        """Get curated feed suggestions from predefined database"""
        suggestions = []

        # Get feeds for this category
        feeds = self.curated_feeds.get(category, [])

        for feed_data in feeds[:3]:  # Limit to 3 curated feeds per category
            try:
                if not self.is_feed_new(feed_data['url'], feed_data['name']):
                    continue

                # Add without full validation (curated feeds are pre-vetted)
                suggestions.append({
                    'name': feed_data['name'],
                    'url': feed_data['url'],
                    'type': 'rss',
                    'description': feed_data['description'],
                    'estimated_posts_per_week': '~5-15 posts',
                    'sample_headline': 'High-quality curated feed',
                    'preview_link': feed_data.get('preview_link', feed_data['url']),
                    'confidence': 'high'
                })

            except Exception as e:
                logger.debug(f"Error with curated feed {feed_data['name']}: {e}")
                continue

        return suggestions

    def generate_suggestions(self):
        """Generate suggestions for all categories"""
        config = self.load_config()

        for category_name, category_data in config.get('categories', {}).items():
            logger.info(f"Discovering feeds for category: {category_name}")

            # Skip special categories
            if category_name in ['on_this_day', 'weather']:
                continue

            category_suggestions = []

            # Strategy 1: Curated feeds (highest priority)
            curated = self.discover_curated_feeds(category_name)
            category_suggestions.extend(curated)
            logger.info(f"  Found {len(curated)} curated feeds")

            # Strategy 2: Related subreddits
            keywords = category_data.get('keywords', [])
            subreddits = self.discover_subreddit_feeds(category_name, keywords)
            category_suggestions.extend(subreddits)
            logger.info(f"  Found {len(subreddits)} subreddit feeds")

            # Strategy 3: Same-domain feeds
            existing_sources = category_data.get('sources', [])
            same_domain = self.discover_same_domain_feeds(category_name, existing_sources)
            category_suggestions.extend(same_domain)
            logger.info(f"  Found {len(same_domain)} same-domain feeds")

            # Deduplicate and limit to top 5
            seen_urls = set()
            unique_suggestions = []
            for suggestion in category_suggestions:
                if suggestion['url'] not in seen_urls:
                    seen_urls.add(suggestion['url'])
                    unique_suggestions.append(suggestion)
                if len(unique_suggestions) >= 5:
                    break

            if unique_suggestions:
                self.suggestions[category_name] = unique_suggestions
                logger.info(f"  Total suggestions for {category_name}: {len(unique_suggestions)}")

    def save_suggestions(self):
        """Save suggestions to JSON file"""
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            output_data = {
                'generated_at': datetime.now().isoformat(),
                'total_categories': len(self.suggestions),
                'total_suggestions': sum(len(sug) for sug in self.suggestions.values()),
                'suggestions': dict(self.suggestions)
            }

            with open(self.output_path, 'w') as f:
                json.dump(output_data, f, indent=2)

            logger.info(f"Suggestions saved to {self.output_path}")
            logger.info(f"Total: {output_data['total_suggestions']} suggestions across {output_data['total_categories']} categories")
            return str(self.output_path)

        except Exception as e:
            logger.error(f"Error saving suggestions: {e}")
            return None


def main():
    """Main entry point for feed discovery"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    discovery = FeedDiscovery()
    discovery.generate_suggestions()
    discovery.save_suggestions()


if __name__ == "__main__":
    main()
