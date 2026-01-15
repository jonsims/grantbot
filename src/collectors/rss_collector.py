"""
RSS Feed Content Collector
Handles fetching and parsing RSS feeds from various news sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_feed(self, url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Fetch articles from a single RSS feed"""
        try:
            logger.info(f"Fetching feed: {url}")
            response = self.session.get(url, timeout=10)
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries[:max_articles]:
                # Parse publication date
                pub_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Only include articles from last 24 hours for daily updates
                if (datetime.now() - pub_date) > timedelta(days=1):
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'content': self._extract_content(entry),
                    'published': pub_date,
                    'source': feed.feed.get('title', 'Unknown Source'),
                    'author': entry.get('author', ''),
                    'categories': [tag.get('term', '') for tag in entry.get('tags', [])]
                }
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} recent articles from {feed.feed.get('title', url)}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {str(e)}")
            return []
    
    def _extract_content(self, entry) -> str:
        """Extract the main content from feed entry"""
        # Try different content fields
        content = ""
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # Clean HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def categorize_article(self, article: Dict[str, Any], keywords: List[str], 
                          exclude_keywords: List[str] = None) -> float:
        """
        Score article relevance to a category based on keywords
        Returns score between 0 and 1
        """
        if exclude_keywords is None:
            exclude_keywords = []
        
        text = f"{article['title']} {article['summary']} {article['content']}".lower()
        
        # Check for excluded keywords first
        for exclude_word in exclude_keywords:
            if exclude_word.lower() in text:
                return 0.0
        
        # Count keyword matches
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text:
                matches += 1
        
        # Boost score for title matches
        title_text = article['title'].lower()
        title_matches = sum(1 for keyword in keywords if keyword.lower() in title_text)
        
        score = (matches + title_matches * 2) / (len(keywords) + 2)
        return min(score, 1.0)
    
    def collect_by_category(self, sources_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Collect articles organized by category"""
        categorized_articles = {}
        
        for category, config in sources_config.items():
            if category == 'categories':  # Skip the categories key itself
                continue
                
            logger.info(f"Collecting articles for category: {category}")
            articles = []
            
            for source in config.get('sources', []):
                if source['type'] == 'rss':
                    feed_articles = self.fetch_feed(source['url'])
                    
                    # Score and filter articles for this category
                    keywords = config.get('keywords', [])
                    exclude_keywords = config.get('exclude_keywords', [])
                    
                    for article in feed_articles:
                        score = self.categorize_article(article, keywords, exclude_keywords)
                        if score > 0.1:  # Only include somewhat relevant articles
                            article['relevance_score'] = score
                            article['category'] = category
                            articles.append(article)
            
            # Sort by relevance and recency
            articles.sort(key=lambda x: (x['relevance_score'], x['published']), reverse=True)
            categorized_articles[category] = articles[:5]  # Top 5 per category
        
        return categorized_articles

# Test function for development
if __name__ == "__main__":
    import yaml
    import os
    
    # Load test configuration
    config_path = "../../config/sources.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        collector = RSSCollector()
        results = collector.collect_by_category(config['categories'])
        
        for category, articles in results.items():
            print(f"\n=== {category.upper()} ===")
            for article in articles[:2]:  # Show top 2 per category
                print(f"- {article['title']}")
                print(f"  Score: {article['relevance_score']:.2f} | {article['source']}")
    else:
        print("Configuration file not found. Run from project root directory.")