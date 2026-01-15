"""
Readwise Collector
Fetches recent highlights and Reader articles from Readwise API
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ReadwiseCollector:
    def __init__(self, access_token: str = None):
        """
        Initialize Readwise collector

        Args:
            access_token: Readwise API access token (defaults to env var)
        """
        self.access_token = access_token or os.getenv('READWISE_ACCESS_TOKEN')
        self.base_url = "https://readwise.io/api/v3"
        self.base_url_v2 = "https://readwise.io/api/v2"  # For highlights

        if not self.access_token:
            logger.warning("Readwise access token not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Readwise collector initialized")

    def get_recent_highlights(self, days: int = 1, limit: int = 10) -> List[Dict]:
        """
        Get recent highlights from Readwise

        Args:
            days: Number of days back to fetch highlights
            limit: Maximum number of highlights to return

        Returns:
            List of highlight dictionaries with:
            - text: The highlighted text
            - title: Book/article title
            - author: Author name
            - source: Source type (book, article, etc.)
            - url: Link to highlight (if available)
            - highlighted_at: When it was highlighted
        """
        if not self.enabled:
            logger.info("Readwise not configured, skipping highlights")
            return []

        try:
            # Calculate date threshold
            cutoff_date = datetime.now() - timedelta(days=days)

            # Fetch highlights from API (v2 API for highlights)
            url = f"{self.base_url_v2}/highlights/"
            headers = {"Authorization": f"Token {self.access_token}"}
            params = {
                "highlighted_at__gt": cutoff_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "page_size": limit
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            highlights = []

            for item in data.get('results', [])[:limit]:
                # Safely extract book info
                book_info = item.get('book_id') or {}
                if isinstance(book_info, int):
                    # If book_id is just an integer, we need to fetch more info
                    book_title = 'Unknown'
                    book_author = 'Unknown Author'
                    book_category = 'article'
                else:
                    book_title = book_info.get('title', 'Unknown')
                    book_author = book_info.get('author', 'Unknown Author')
                    book_category = book_info.get('category', 'article')

                highlights.append({
                    'text': item.get('text', ''),
                    'title': book_title,
                    'author': book_author,
                    'source': book_category,
                    'url': item.get('url'),
                    'highlighted_at': item.get('highlighted_at'),
                    'note': item.get('note')  # User's note on the highlight
                })

            logger.info(f"Fetched {len(highlights)} recent highlights from Readwise")
            return highlights

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Readwise highlights: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Readwise highlights: {e}")
            return []

    def get_reader_articles(self, days: int = 1, limit: int = 10, location: str = None) -> List[Dict]:
        """
        Get recent articles from Readwise Reader

        Args:
            days: Number of days back to fetch articles
            limit: Maximum number of articles to return
            location: Filter by location (new, later, archive, feed)

        Returns:
            List of article dictionaries with:
            - title: Article title
            - author: Author name
            - url: Article URL
            - summary: Article summary (if available)
            - saved_at: When it was saved
            - reading_progress: Reading progress (0-100)
        """
        if not self.enabled:
            logger.info("Readwise not configured, skipping Reader articles")
            return []

        try:
            # Calculate date threshold
            cutoff_date = datetime.now() - timedelta(days=days)

            # Fetch Reader documents from API (v3)
            url = f"{self.base_url}/list/"
            headers = {"Authorization": f"Token {self.access_token}"}
            params = {
                "updatedAfter": cutoff_date.strftime("%Y-%m-%dT%H:%M:%S"),
            }

            # Only add location if specified
            if location:
                params["location"] = location

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = []

            for item in data.get('results', [])[:limit]:
                articles.append({
                    'title': item.get('title', 'Untitled'),
                    'author': item.get('author', 'Unknown Author'),
                    'url': item.get('url'),  # Readwise Reader link (read.readwise.io)
                    'source_url': item.get('source_url'),  # Original article URL (for reference)
                    'summary': item.get('summary', ''),
                    'saved_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'reading_progress': item.get('reading_progress', 0),
                    'word_count': item.get('word_count', 0),
                    'category': item.get('category', 'article')
                })

            logger.info(f"Fetched {len(articles)} recent articles from Readwise Reader")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Readwise Reader articles: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Readwise Reader articles: {e}")
            return []

    def get_daily_review(self, highlight_limit: int = 5, article_limit: int = 5) -> Dict:
        """
        Get a combined daily review of highlights and saved articles

        Args:
            highlight_limit: Max highlights to include
            article_limit: Max articles to include

        Returns:
            Dictionary with 'highlights' and 'articles' keys
        """
        return {
            'highlights': self.get_recent_highlights(days=1, limit=highlight_limit),
            'articles': self.get_reader_articles(days=1, limit=article_limit)
        }


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    collector = ReadwiseCollector()

    if collector.enabled:
        print("\n=== Testing Readwise Highlights ===")
        highlights = collector.get_recent_highlights(days=7, limit=5)
        print(f"Found {len(highlights)} highlights")
        for h in highlights[:3]:
            print(f"\n📝 {h['title']} by {h['author']}")
            print(f"   \"{h['text'][:100]}...\"")

        print("\n=== Testing Readwise Reader Articles ===")
        articles = collector.get_reader_articles(days=7, limit=5)
        print(f"Found {len(articles)} articles")
        for a in articles[:3]:
            print(f"\n📰 {a['title']}")
            print(f"   by {a['author']}")
            print(f"   {a['url']}")
            print(f"   Progress: {a['reading_progress']}%")

        print("\n=== Testing Daily Review ===")
        review = collector.get_daily_review(highlight_limit=3, article_limit=3)
        print(f"Daily Review: {len(review['highlights'])} highlights, {len(review['articles'])} articles")
    else:
        print("❌ Readwise not configured. Set READWISE_ACCESS_TOKEN in .env")
