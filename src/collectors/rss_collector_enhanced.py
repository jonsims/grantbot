"""
Enhanced RSS Feed Collector with Concurrent Fetching and Robust Error Handling
Improves performance from ~30s to ~5s for multiple feeds
"""

import feedparser
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import defaultdict

logger = logging.getLogger(__name__)

class EnhancedRSSCollector:
    def __init__(self, max_workers: int = 10, timeout: int = 10, status_tracker=None):
        """
        Initialize enhanced RSS collector with concurrent processing

        Args:
            max_workers: Maximum number of concurrent threads
            timeout: Request timeout in seconds
            status_tracker: FeedStatusGenerator instance for tracking feed health
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = self._create_session()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.status_tracker = status_tracker

        # Statistics tracking
        self.stats = {
            'feeds_attempted': 0,
            'feeds_successful': 0,
            'feeds_failed': 0,
            'articles_collected': 0,
            'total_time': 0
        }
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'DailyNewsAgent/2.0 (Enhanced RSS Collector)',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        })
        
        return session
    
    def _fetch_single_feed(self, source: Dict[str, Any], keywords: List[str] = None,
                          exclude_keywords: List[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Fetch a single RSS feed with error handling
        
        Returns:
            Tuple of (source_name, articles_list)
        """
        url = source['url']
        source_name = source.get('name', 'Unknown')
        
        try:
            # Make request with timeout
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {source_name}: {feed.bozo_exception}")
                if self.status_tracker:
                    self.status_tracker.track_warning(source_name, f"Feed parsing: {str(feed.bozo_exception)[:50]}")
            
            articles = []
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=2)
            
            for entry in feed.entries[:20]:  # Process more entries
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    
                    # Skip old articles
                    if pub_date and pub_date < cutoff_date:
                        continue
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'content') and len(entry.content) > 0:
                        content = entry.content[0].get('value', '')
                    
                    # Clean content
                    content = self._clean_html(content)
                    
                    # Create article
                    article = {
                        'title': entry.get('title', 'Untitled'),
                        'link': entry.get('link', ''),
                        'source': source_name,
                        'content': content[:500],  # Limit content length
                        'published': pub_date.isoformat() if pub_date else None,
                        'relevance_score': 0.5
                    }
                    
                    # Apply keyword filtering
                    if self._matches_keywords(article, keywords, exclude_keywords):
                        articles.append(article)
                    
                except Exception as e:
                    logger.debug(f"Error processing entry in {source_name}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from {source_name}")

            # Track feed status
            if self.status_tracker:
                self.status_tracker.track_feed_result(source_name, len(articles))

            return (source_name, articles)

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {source_name} ({url})")
            if self.status_tracker:
                self.status_tracker.track_feed_result(source_name, 0, error="Request timeout")
            return (source_name, [])
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error for {source_name}: {str(e)}")
            if self.status_tracker:
                self.status_tracker.track_feed_result(source_name, 0, error=f"Connection error: {str(e)[:50]}")
            return (source_name, [])
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error for {source_name}: {e.response.status_code}")
            if self.status_tracker:
                self.status_tracker.track_feed_result(source_name, 0, error=f"HTTP {e.response.status_code}")
            return (source_name, [])
        except Exception as e:
            logger.error(f"Unexpected error fetching {source_name}: {str(e)}")
            if self.status_tracker:
                self.status_tracker.track_feed_result(source_name, 0, error=str(e)[:50])
            return (source_name, [])
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text"""
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _matches_keywords(self, article: Dict[str, Any], 
                         keywords: List[str] = None,
                         exclude_keywords: List[str] = None) -> bool:
        """Check if article matches keyword criteria"""
        text = f"{article['title']} {article['content']}".lower()
        
        # Check exclude keywords first
        if exclude_keywords:
            for keyword in exclude_keywords:
                if keyword.lower() in text:
                    return False
        
        # Check include keywords (if specified, at least one must match)
        if keywords:
            return any(keyword.lower() in text for keyword in keywords)
        
        return True  # No keyword filtering
    
    def collect_by_category_concurrent(self, sources_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect articles from all categories using concurrent processing
        
        Returns:
            Dictionary mapping category names to lists of articles
        """
        start_time = time.time()
        categorized_articles = defaultdict(list)
        source_article_counts = defaultdict(lambda: defaultdict(int))
        
        # Prepare all feed fetching tasks
        futures_to_info = {}
        
        for category, config in sources_config.items():
            if category == 'categories':
                continue
                
            keywords = config.get('keywords', [])
            exclude_keywords = config.get('exclude_keywords', [])
            sources = config.get('sources', [])
            
            logger.info(f"Collecting articles for category: {category}")
            
            for source in sources:
                if source.get('type') == 'rss':
                    future = self.executor.submit(
                        self._fetch_single_feed,
                        source,
                        keywords,
                        exclude_keywords
                    )
                    futures_to_info[future] = (category, source)
                    self.stats['feeds_attempted'] += 1
        
        # Collect results as they complete
        for future in as_completed(futures_to_info, timeout=60):
            category, source_config = futures_to_info[future]
            
            try:
                source_name, articles = future.result(timeout=5)
                
                if articles:
                    # Apply max_articles limit if specified
                    max_articles = source_config.get('max_articles', 10)
                    
                    # Apply filter_keywords for specific sources (like Reddit)
                    if source_config.get('filter_keywords'):
                        filter_keywords = [kw.lower() for kw in source_config['filter_keywords']]
                        filtered_articles = []
                        for article in articles:
                            content = f"{article.get('title', '')} {article.get('content', '')}".lower()
                            if any(keyword in content for keyword in filter_keywords):
                                filtered_articles.append(article)
                        articles = filtered_articles
                    
                    # Limit articles per source
                    articles_to_add = articles[:max_articles]
                    categorized_articles[category].extend(articles_to_add)
                    source_article_counts[category][source_name] = len(articles_to_add)
                    
                    self.stats['feeds_successful'] += 1
                    self.stats['articles_collected'] += len(articles_to_add)
                    
                    if len(articles_to_add) < len(articles):
                        logger.info(f"Limited {source_name} to {len(articles_to_add)} articles (had {len(articles)})")
                else:
                    self.stats['feeds_failed'] += 1
                    
            except Exception as e:
                logger.error(f"Error collecting from category {category}: {str(e)}")
                self.stats['feeds_failed'] += 1
        
        # Sort articles by relevance and recency
        for category in categorized_articles:
            categorized_articles[category] = self._rank_articles(
                categorized_articles[category]
            )[:10]  # Limit to top 10 per category
            
            # Log source distribution for this category
            if source_article_counts[category]:
                logger.info(f"  {category}: {dict(source_article_counts[category])}")
        
        self.stats['total_time'] = time.time() - start_time
        self._log_statistics()
        
        return dict(categorized_articles)
    
    def _rank_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank articles by relevance and recency"""
        # Simple ranking: newer articles first
        def score_article(article):
            score = article.get('relevance_score', 0.5)
            
            # Boost score for recent articles
            if article.get('published'):
                try:
                    pub_date = datetime.fromisoformat(article['published'])
                    hours_old = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600
                    if hours_old < 24:
                        score += (24 - hours_old) / 24  # Boost newer articles
                except:
                    pass
            
            return score
        
        return sorted(articles, key=score_article, reverse=True)
    
    def _log_statistics(self):
        """Log collection statistics"""
        logger.info(f"=== RSS Collection Statistics ===")
        logger.info(f"Total time: {self.stats['total_time']:.2f} seconds")
        logger.info(f"Feeds attempted: {self.stats['feeds_attempted']}")
        logger.info(f"Feeds successful: {self.stats['feeds_successful']}")
        logger.info(f"Feeds failed: {self.stats['feeds_failed']}")
        logger.info(f"Articles collected: {self.stats['articles_collected']}")
        
        if self.stats['feeds_attempted'] > 0:
            success_rate = (self.stats['feeds_successful'] / self.stats['feeds_attempted']) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")
    
    def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)
        self.session.close()

# Backward compatibility wrapper
class RSSCollector(EnhancedRSSCollector):
    """Maintains backward compatibility with existing code"""
    
    def collect_by_category(self, sources_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Legacy method name for compatibility"""
        return self.collect_by_category_concurrent(sources_config)
    
    def fetch_feed(self, url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Legacy single feed fetch for compatibility"""
        source = {'url': url, 'name': url}
        _, articles = self._fetch_single_feed(source)
        return articles[:max_articles]


# Test the enhanced collector
if __name__ == "__main__":
    import yaml
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    config_path = "config/sources-v2.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        collector = EnhancedRSSCollector(max_workers=10)
        
        try:
            articles = collector.collect_by_category_concurrent(config['categories'])
            
            print(f"\n=== Collection Results ===")
            for category, items in articles.items():
                print(f"{category}: {len(items)} articles")
        
        finally:
            collector.cleanup()
    else:
        print(f"Config file not found: {config_path}")