"""
OPML Parser
Parses OPML files and extracts RSS feeds organized by category
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class OPMLParser:
    def __init__(self):
        self.feeds_by_category = {}
    
    def parse_opml_file(self, opml_path: str) -> Dict[str, List[Dict[str, str]]]:
        """Parse OPML file and return feeds organized by category"""
        try:
            tree = ET.parse(opml_path)
            root = tree.getroot()
            
            feeds_by_category = {}
            
            # Find all outline elements with categories
            for outline in root.findall(".//outline"):
                category_name = outline.get('text') or outline.get('title')
                
                # Skip if no category name
                if not category_name:
                    continue
                
                # If this outline has child outlines (it's a category)
                child_outlines = outline.findall('outline')
                if child_outlines:
                    feeds = []
                    for child in child_outlines:
                        feed_url = child.get('xmlUrl')
                        feed_title = child.get('text') or child.get('title')
                        feed_html = child.get('htmlUrl')
                        
                        if feed_url and feed_title:
                            feeds.append({
                                'name': feed_title,
                                'url': feed_url,
                                'html_url': feed_html,
                                'type': 'rss'
                            })
                    
                    if feeds:
                        feeds_by_category[category_name] = feeds
                else:
                    # This is a direct feed (not in a category)
                    feed_url = outline.get('xmlUrl')
                    feed_title = outline.get('text') or outline.get('title')
                    feed_html = outline.get('htmlUrl')
                    
                    if feed_url and feed_title:
                        if 'Uncategorized' not in feeds_by_category:
                            feeds_by_category['Uncategorized'] = []
                        
                        feeds_by_category['Uncategorized'].append({
                            'name': feed_title,
                            'url': feed_url,
                            'html_url': feed_html,
                            'type': 'rss'
                        })
            
            logger.info(f"Parsed OPML file: {len(feeds_by_category)} categories found")
            for category, feeds in feeds_by_category.items():
                logger.info(f"  {category}: {len(feeds)} feeds")
            
            return feeds_by_category
            
        except Exception as e:
            logger.error(f"Error parsing OPML file: {str(e)}")
            return {}
    
    def map_to_content_categories(self, opml_feeds: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
        """Map OPML categories to our content categories with keywords"""
        
        # Mapping from OPML categories to our content categories
        category_mapping = {
            'moonshots': {
                'opml_categories': ['AI', 'Space', 'Medical Science', 'Tech Longform'],
                'keywords': ['breakthrough', 'innovation', 'grand challenge', 'moonshot', 'disruptive', 'quantum', 'fusion', 'space exploration', 'medical breakthrough'],
                'word_target': 150
            },
            'strategic_management': {
                'opml_categories': ['Strategy Blogs', 'Journals', 'Substack'],
                'keywords': ['strategy', 'management', 'business model', 'competitive advantage', 'organizational', 'leadership', 'transformation'],
                'word_target': 100
            },
            'tech_headlines': {
                'opml_categories': ['*Tech News', 'AI', 'Software', 'Vibe Coding'],
                'keywords': ['technology', 'AI', 'software', 'hardware', 'startup', 'product launch', 'apple', 'google', 'microsoft'],
                'word_target': 200
            },
            'us_news': {
                'opml_categories': [],  # Will need separate news sources
                'keywords': ['politics', 'government', 'policy', 'congress', 'senate', 'election'],
                'exclude_keywords': ['Trump', 'Donald Trump', 'MAGA'],
                'word_target': 150
            },
            'market_business': {
                'opml_categories': ['Money', 'Startup'],
                'keywords': ['market', 'stocks', 'business', 'economy', 'earnings', 'IPO', 'merger', 'funding', 'investment'],
                'word_target': 200
            },
            'boston_tech': {
                'opml_categories': ['Babson Blogs'],
                'keywords': ['Boston', 'Cambridge', 'MIT', 'Harvard', 'startup', 'biotech', 'fintech', 'entrepreneurship'],
                'word_target': 100
            }
        }
        
        # Build the configuration
        config = {'categories': {}}
        
        for content_category, mapping in category_mapping.items():
            sources = []
            
            # Add feeds from matching OPML categories
            for opml_category in mapping['opml_categories']:
                if opml_category in opml_feeds:
                    sources.extend(opml_feeds[opml_category])
            
            # Create category configuration
            config['categories'][content_category] = {
                'priority': 'high' if content_category in ['moonshots', 'tech_headlines', 'market_business'] else 'medium',
                'word_target': mapping['word_target'],
                'keywords': mapping['keywords'],
                'sources': sources[:10]  # Limit to top 10 sources per category
            }
            
            # Add exclude keywords if specified
            if 'exclude_keywords' in mapping:
                config['categories'][content_category]['exclude_keywords'] = mapping['exclude_keywords']
        
        # Add supplementary categories
        config['categories']['on_this_day'] = {
            'priority': 'low',
            'word_target': 50,
            'sources': [
                {'name': 'Wikipedia On This Day', 'type': 'api', 'endpoint': 'https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all'}
            ]
        }
        
        return config
    
    def get_high_quality_feeds(self, opml_feeds: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """Extract high-quality feeds for moonshot/innovation content"""
        high_quality_feeds = []
        
        priority_categories = ['AI', 'Strategy Blogs', 'Journals', '*Tech News', 'Tech Longform']
        
        for category in priority_categories:
            if category in opml_feeds:
                for feed in opml_feeds[category][:3]:  # Top 3 from each priority category
                    high_quality_feeds.append(feed)
        
        return high_quality_feeds

# Test function
if __name__ == "__main__":
    parser = OPMLParser()
    
    # Test with the actual OPML file
    opml_path = "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/1004892875.xml"
    
    feeds = parser.parse_opml_file(opml_path)
    config = parser.map_to_content_categories(feeds)
    
    print("=== OPML PARSING RESULTS ===")
    print(f"Total categories: {len(feeds)}")
    
    print("\n=== CONTENT CATEGORY MAPPING ===")
    for category, data in config['categories'].items():
        print(f"{category}: {len(data['sources'])} sources")
        if data['sources']:
            print(f"  Sample: {data['sources'][0]['name']}")
    
    print("\n=== HIGH QUALITY FEEDS ===")
    hq_feeds = parser.get_high_quality_feeds(feeds)
    for feed in hq_feeds[:5]:
        print(f"- {feed['name']} ({feed['url'][:50]}...)")