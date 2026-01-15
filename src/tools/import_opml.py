#!/usr/bin/env python3
"""
Import feeds from InoReader OPML file and map to our categories
Creates a report of all feeds and suggests category mappings
"""

import xml.etree.ElementTree as ET
import yaml
import json
import requests
import feedparser
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OPMLImporter:
    def __init__(self, opml_path: str, config_path: str):
        self.opml_path = opml_path
        self.config_path = config_path
        self.feeds = []
        self.categories = {}
        self.mapping = {
            # InoReader categories -> Our categories
            'AI': 'ai',
            'Vibe Coding': 'ai',
            'Product Hunt': 'ai',
            '*Tech News': 'tech_headlines',
            'Tech Longform': 'longform_articles',
            'Space': 'space_news',
            'Money': 'market_business',
            'Startup': 'market_business',
            'Strategy Blogs': 'moonshot_strategy',
            'Journals': 'academic_research',
            'Babson Blogs': 'higher_education',
            'Teaching': 'higher_education',
            'Philosophy & Tips': 'daily_stoicism',
            'Writers': 'longform_articles',
            'Substack': 'longform_articles',
        }
    
    def parse_opml(self):
        """Parse OPML file and extract feeds"""
        tree = ET.parse(self.opml_path)
        root = tree.getroot()
        
        current_category = None
        
        for outline in root.iter('outline'):
            # Check if this is a category
            if outline.get('text') and not outline.get('xmlUrl'):
                current_category = outline.get('text')
                if current_category not in self.categories:
                    self.categories[current_category] = []
            
            # Check if this is a feed
            if outline.get('xmlUrl'):
                feed = {
                    'title': outline.get('title', 'Unknown'),
                    'url': outline.get('xmlUrl'),
                    'html_url': outline.get('htmlUrl', ''),
                    'text': outline.get('text', ''),
                    'category': current_category
                }
                self.feeds.append(feed)
                if current_category:
                    self.categories[current_category].append(feed)
        
        logger.info(f"Parsed {len(self.feeds)} feeds in {len(self.categories)} categories")
    
    def test_feeds(self, sample_size: int = 5) -> Dict:
        """Test a sample of feeds for availability"""
        import random
        sample = random.sample(self.feeds, min(sample_size, len(self.feeds)))
        
        results = {'working': [], 'broken': []}
        
        for feed in sample:
            try:
                # Skip special InoReader internal feeds
                if '@ino.to' in feed['url']:
                    continue
                    
                response = requests.head(feed['url'], timeout=3, allow_redirects=True)
                if response.status_code < 400:
                    results['working'].append(feed)
                else:
                    results['broken'].append(feed)
            except:
                results['broken'].append(feed)
        
        return results
    
    def generate_report(self) -> str:
        """Generate a report of all feeds and suggested mappings"""
        report = []
        report.append("# InoReader OPML Import Report\n")
        report.append(f"Total feeds: {len(self.feeds)}")
        report.append(f"Categories: {len(self.categories)}\n")
        
        # Category mapping suggestions
        report.append("## Category Mappings\n")
        for ino_cat, our_cat in self.mapping.items():
            if ino_cat in self.categories:
                count = len(self.categories[ino_cat])
                report.append(f"- {ino_cat} ({count} feeds) → {our_cat}")
        
        # Unmapped categories
        unmapped = [cat for cat in self.categories if cat not in self.mapping]
        if unmapped:
            report.append("\n## Unmapped Categories")
            for cat in unmapped:
                count = len(self.categories[cat])
                report.append(f"- {cat} ({count} feeds)")
        
        # Top feeds by category
        report.append("\n## Top Feeds by Category\n")
        for category, feeds in self.categories.items():
            if len(feeds) > 0:
                report.append(f"\n### {category}")
                for feed in feeds[:3]:  # Show first 3
                    title = feed['title'][:50]
                    report.append(f"- {title}")
        
        return "\n".join(report)
    
    def suggest_additions(self) -> List[Dict]:
        """Suggest high-value feeds to add to our config"""
        suggestions = []
        
        # Priority feeds to add
        priority_patterns = [
            'cursor', 'replit', 'vercel', 'bolt', 'lovable',
            'openai', 'anthropic', 'claude', 'gpt',
            'hacker news', 'techcrunch', 'product hunt',
            'babson', 'mit', 'harvard'
        ]
        
        for feed in self.feeds:
            # Skip internal InoReader feeds
            if '@ino.to' in feed['url']:
                continue
                
            title_lower = feed['title'].lower()
            for pattern in priority_patterns:
                if pattern in title_lower:
                    our_category = self.mapping.get(feed['category'], 'ai')
                    suggestions.append({
                        'name': feed['title'],
                        'url': feed['url'],
                        'html_url': feed['html_url'],
                        'category': our_category,
                        'reason': f"Matches priority pattern: {pattern}"
                    })
                    break
        
        return suggestions[:20]  # Top 20 suggestions
    
    def export_suggestions(self, output_path: str):
        """Export suggested feeds in YAML format"""
        suggestions = self.suggest_additions()
        
        # Group by category
        by_category = {}
        for feed in suggestions:
            cat = feed['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                'name': feed['name'],
                'url': feed['url'],
                'html_url': feed['html_url'],
                'type': 'rss'
            })
        
        with open(output_path, 'w') as f:
            yaml.dump({'suggested_additions': by_category}, f, default_flow_style=False)
        
        logger.info(f"Exported {len(suggestions)} suggestions to {output_path}")


def main():
    """Run the OPML importer"""
    import sys
    import os
    
    # Paths
    opml_path = "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/1004892875.xml"
    config_path = "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent/config/sources-v2.yaml"
    
    if not os.path.exists(opml_path):
        print(f"OPML file not found: {opml_path}")
        sys.exit(1)
    
    importer = OPMLImporter(opml_path, config_path)
    
    # Parse OPML
    importer.parse_opml()
    
    # Generate report
    report = importer.generate_report()
    print(report)
    
    # Save report
    report_path = "opml_import_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")
    
    # Export suggestions
    suggestions_path = "suggested_feeds.yaml"
    importer.export_suggestions(suggestions_path)
    
    # Test a sample
    print("\n## Testing Sample Feeds")
    results = importer.test_feeds(10)
    print(f"Working: {len(results['working'])}")
    print(f"Broken: {len(results['broken'])}")


if __name__ == "__main__":
    main()