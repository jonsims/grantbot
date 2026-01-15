"""
Feed Status Generator
Analyzes RSS collection results and generates feed-status.json for web UI
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

class FeedStatusGenerator:
    def __init__(self, output_path: str = "config/feed-status.json"):
        self.output_path = Path(output_path)
        self.feed_status = {}

    def track_feed_result(self, source_name: str, article_count: int, error: str = None):
        """Track the result of fetching from a feed"""

        if error:
            self.feed_status[source_name] = {
                'status': 'error',
                'tooltip': f'✗ Error: {error[:50]}...' if len(error) > 50 else f'✗ Error: {error}',
                'article_count': 0,
                'last_checked': datetime.now().isoformat()
            }
        elif article_count > 0:
            self.feed_status[source_name] = {
                'status': 'success',
                'tooltip': f'✓ {article_count} article{"s" if article_count != 1 else ""} fetched',
                'article_count': article_count,
                'last_checked': datetime.now().isoformat()
            }
        else:
            # 0 articles but no error
            self.feed_status[source_name] = {
                'status': 'empty',
                'tooltip': '⚠ No new articles (feed may be empty or inactive)',
                'article_count': 0,
                'last_checked': datetime.now().isoformat()
            }

    def track_warning(self, source_name: str, warning_msg: str):
        """Track a warning for a feed (e.g., parsing issues)"""
        self.feed_status[source_name] = {
            'status': 'warning',
            'tooltip': f'⚠ {warning_msg[:60]}...' if len(warning_msg) > 60 else f'⚠ {warning_msg}',
            'article_count': 0,
            'last_checked': datetime.now().isoformat()
        }

    def generate_status_file(self):
        """Generate and save feed-status.json"""
        try:
            # Ensure directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Add metadata
            status_data = {
                'generated_at': datetime.now().isoformat(),
                'total_feeds': len(self.feed_status),
                'feeds': self.feed_status
            }

            # Write to file
            with open(self.output_path, 'w') as f:
                json.dump(status_data, f, indent=2)

            logger.info(f"Feed status saved to {self.output_path} ({len(self.feed_status)} feeds)")
            return str(self.output_path)

        except Exception as e:
            logger.error(f"Error generating feed status: {e}")
            return None

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics"""
        summary = {
            'success': 0,
            'empty': 0,
            'warning': 0,
            'error': 0
        }

        for feed_data in self.feed_status.values():
            status = feed_data.get('status', 'unknown')
            if status in summary:
                summary[status] += 1

        return summary


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test the generator
    generator = FeedStatusGenerator()

    # Simulate some feed results
    generator.track_feed_result("GitHub Blog", 3)
    generator.track_feed_result("OpenAI Blog", 2)
    generator.track_feed_result("Replit Blog", 0)
    generator.track_warning("Supabase Blog", "Feed parsing warning: not well-formed")
    generator.track_feed_result("DeepMind Blog", 0, error="HTTP 404: Not Found")

    # Generate file
    output = generator.generate_status_file()
    print(f"Generated: {output}")

    # Show summary
    summary = generator.get_summary()
    print(f"Summary: {summary}")
