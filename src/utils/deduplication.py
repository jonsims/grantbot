"""
Article Deduplication System
Prevents the same articles from appearing in multiple daily updates
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)

class ArticleDeduplicator:
    def __init__(self, cache_dir: str = "cache/seen_articles"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "seen_articles.json")
        self.seen_articles = self._load_seen_articles()

    def _load_seen_articles(self) -> Dict[str, str]:
        """Load previously seen articles from cache"""
        os.makedirs(self.cache_dir, exist_ok=True)

        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Clean old entries (older than 24 hours)
                    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
                    cleaned = {k: v for k, v in data.items() if v > cutoff}
                    return cleaned
            except Exception as e:
                logger.error(f"Error loading seen articles: {e}")
                return {}
        return {}

    def _save_seen_articles(self):
        """Save seen articles to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.seen_articles, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving seen articles: {e}")

    def _generate_article_hash(self, article: Dict) -> str:
        """Generate unique hash for article based on URL and title"""
        url = article.get('link', '')
        title = article.get('title', '')
        content = f"{url}|{title}".lower()
        return hashlib.md5(content.encode()).hexdigest()

    def is_duplicate(self, article: Dict) -> bool:
        """Check if article has been seen recently"""
        article_hash = self._generate_article_hash(article)
        return article_hash in self.seen_articles

    def mark_as_seen(self, article: Dict):
        """Mark article as seen"""
        article_hash = self._generate_article_hash(article)
        self.seen_articles[article_hash] = datetime.now().isoformat()

    def filter_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Filter out duplicate articles and mark new ones as seen"""
        unique_articles = []
        duplicates_found = 0

        for article in articles:
            if not self.is_duplicate(article):
                unique_articles.append(article)
                self.mark_as_seen(article)
            else:
                duplicates_found += 1

        if duplicates_found > 0:
            logger.info(f"Filtered out {duplicates_found} duplicate articles")

        self._save_seen_articles()
        return unique_articles

    def filter_categorized_articles(self, categorized_articles: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Filter duplicates from all categories"""
        filtered = {}
        total_duplicates = 0

        for category, articles in categorized_articles.items():
            filtered_articles = self.filter_duplicates(articles)
            filtered[category] = filtered_articles
            duplicates = len(articles) - len(filtered_articles)
            if duplicates > 0:
                total_duplicates += duplicates
                logger.info(f"  {category}: Removed {duplicates} duplicates")

        if total_duplicates > 0:
            logger.info(f"Total duplicates removed: {total_duplicates}")

        return filtered

    def clean_old_entries(self, hours: int = 24):
        """Remove entries older than specified hours"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        before_count = len(self.seen_articles)
        self.seen_articles = {k: v for k, v in self.seen_articles.items() if v > cutoff}
        after_count = len(self.seen_articles)
        removed = before_count - after_count

        if removed > 0:
            logger.info(f"Cleaned {removed} old article entries")
            self._save_seen_articles()

        return removed


if __name__ == "__main__":
    # Test deduplication
    deduplicator = ArticleDeduplicator()

    test_articles = [
        {'title': 'Test Article 1', 'link': 'https://example.com/1'},
        {'title': 'Test Article 2', 'link': 'https://example.com/2'},
        {'title': 'Test Article 1', 'link': 'https://example.com/1'},  # Duplicate
    ]

    filtered = deduplicator.filter_duplicates(test_articles)
    print(f"Original: {len(test_articles)}, Filtered: {len(filtered)}")
    print(f"Duplicates removed: {len(test_articles) - len(filtered)}")