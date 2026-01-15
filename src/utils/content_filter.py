"""
Content Filter for Daily News Agent
Filters out unwanted articles based on user preferences
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        """Initialize content filter with Jon's preferences"""
        
        # Keywords that instantly disqualify an article
        self.blacklist_keywords = [
            # Sports (comprehensive list)
            'NFL', 'NBA', 'MLB', 'NHL', 'FIFA', 'UEFA', 'Premier League',
            'football', 'basketball', 'baseball', 'hockey', 'soccer',
            'quarterback', 'touchdown', 'home run', 'slam dunk', 'playoffs',
            'championship game', 'Super Bowl', 'World Series', 'Stanley Cup',
            'World Cup', 'Olympics', 'athlete', 'coach', 'stadium',
            'draft pick', 'free agent', 'sports team', 'season opener',
            'game score', 'winning streak', 'losing streak', 'tournament',
            'referee', 'penalty', 'overtime', 'halftime', 'innings',
            
            # Sports betting
            'sports betting', 'fantasy football', 'fantasy sports', 'DraftKings',
            'FanDuel', 'betting odds', 'point spread', 'over/under',
            
            # Entertainment & Celebrity
            'red carpet', 'celebrity', 'Hollywood', 'movie premiere',
            'box office', 'Oscar', 'Emmy', 'Grammy', 'Golden Globe',
            'reality TV', 'reality show', 'Bachelor', 'Bachelorette',
            'Kardashian', 'influencer drama', 'celebrity couple',
            'breakup', 'dating', 'engaged', 'pregnant', 'baby bump',
            'paparazzi', 'tabloid', 'gossip',
            
            # Fashion & Lifestyle
            'fashion week', 'runway', 'designer collection', 'haute couture',
            'fashion trend', 'style icon', 'what she wore', 'outfit',
            'Met Gala', 'fashion designer', 'spring collection', 'fall collection',
            
            # Award Shows & Entertainment Events
            'award show', 'awards ceremony', 'nominees', 'acceptance speech',
            'after party', 'VMA', 'BET Awards', 'CMA', 'ACM',
            
            # Music Industry (unless tech-related)
            'album release', 'concert tour', 'music festival', 'Coachella',
            'Lollapalooza', 'tour dates', 'backstage', 'fan meet',
            
            # TV Shows (unless tech/business related)
            'season finale', 'season premiere', 'episode recap', 'spoiler alert',
            'streaming numbers', 'ratings', 'renewed for season', 'cancelled show'
        ]
        
        # Special whitelist - always include these
        self.whitelist_keywords = [
            # David Brooks exception
            'David Brooks',
            
            # AI and tools Jon specifically wants
            'AI tool', 'AI app', 'new app', 'productivity tool',
            'developer tool', 'no-code', 'low-code', 'API',
            'open source', 'GitHub', 'framework', 'library'
        ]
        
        # Politics filter (exclude unless business-related)
        self.political_keywords = [
            'Republican', 'Democrat', 'GOP', 'liberal', 'conservative',
            'election', 'campaign', 'poll', 'primary', 'caucus',
            'Congress', 'Senate', 'House of Representatives',
            'political party', 'partisan', 'filibuster', 'gerrymander',
            'swing state', 'electoral', 'voter', 'ballot'
        ]
        
        # Business/tech keywords that override political filter
        self.business_override = [
            'regulation', 'antitrust', 'merger', 'acquisition',
            'IPO', 'earnings', 'revenue', 'market', 'stock',
            'startup', 'venture', 'funding', 'investment',
            'technology', 'innovation', 'AI', 'crypto', 'blockchain',
            'tech', 'big tech', 'Silicon Valley', 'platform'
        ]
        
        # Boston-specific filter (exclude unless entrepreneurship/events)
        self.boston_keywords = ['Boston', 'Cambridge', 'Massachusetts', ' MA ']  # Space around MA to avoid matching other words
        self.boston_whitelist = [
            'MIT', 'Harvard', 'startup', 'entrepreneur', 'incubator',
            'accelerator', 'hackathon', 'tech event', 'conference',
            'Babson', 'innovation', 'venture capital', 'biotech'
        ]

        # Boring administrative/bureaucratic keywords (low relevance)
        self.boring_keywords = [
            'custodial', 'janitorial', 'landscaping', 'maintenance contract',
            'cleaning services', 'facilities management', 'groundskeeping',
            'contract awarded', 'services contract', 'vendor selected',
            'procurement', 'RFP awarded', 'facilities services',
            'routine maintenance', 'administrative', 'HR policy',
            'personnel announcement', 'staff appointment', 'office relocation',
            'building renovation', 'parking lot', 'cafeteria',
            # Press releases that don't matter
            'appoints', 'names', 'announces appointment of', 'joins as',
            'promoted to', 'vice president of operations'
        ]
    
    def should_include_article(self, article: Dict[str, Any]) -> bool:
        """
        Determine if an article should be included based on filters
        
        Args:
            article: Dictionary with 'title', 'content', 'source' keys
            
        Returns:
            bool: True if article should be included, False otherwise
        """
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        source = article.get('source', '').lower()
        
        full_text = f"{title} {content} {source}"
        
        # Check whitelist first - these always get through
        for keyword in self.whitelist_keywords:
            if keyword.lower() in full_text:
                logger.debug(f"✅ Whitelisted: '{article.get('title', '')[:50]}...' (matched: {keyword})")
                return True
        
        # Check blacklist - instant rejection
        for keyword in self.blacklist_keywords:
            if keyword.lower() in full_text:
                logger.debug(f"❌ Blacklisted: '{article.get('title', '')[:50]}...' (matched: {keyword})")
                return False

        # Check boring/administrative content - rejection
        for keyword in self.boring_keywords:
            if keyword.lower() in full_text:
                logger.debug(f"❌ Boring: '{article.get('title', '')[:50]}...' (matched: {keyword})")
                return False
        
        # Check political content (exclude unless business-related)
        has_political = any(kw.lower() in full_text for kw in self.political_keywords)
        has_business = any(kw.lower() in full_text for kw in self.business_override)
        
        if has_political and not has_business:
            logger.debug(f"❌ Political (non-business): '{article.get('title', '')[:50]}...' - Political: {[kw for kw in self.political_keywords if kw.lower() in full_text]}")
            return False
        elif has_political and has_business:
            logger.debug(f"✅ Political+Business: '{article.get('title', '')[:50]}...' - Business: {[kw for kw in self.business_override if kw.lower() in full_text]}")
        
        # Check Boston content (exclude unless entrepreneurship/events)
        has_boston = any(kw.lower() in full_text for kw in self.boston_keywords)
        has_boston_whitelist = any(kw.lower() in full_text for kw in self.boston_whitelist)
        
        if has_boston and not has_boston_whitelist:
            logger.debug(f"❌ Boston (non-entrepreneurship): '{article.get('title', '')[:50]}...'")
            return False
        
        # Article passed all filters
        return True
    
    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of articles based on user preferences
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of filtered articles
        """
        filtered = []
        removed_count = 0
        
        for article in articles:
            if self.should_include_article(article):
                filtered.append(article)
            else:
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Filtered out {removed_count} articles based on content preferences")
        
        return filtered
    
    def filter_categorized_articles(self, categorized: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter articles within each category
        
        Args:
            categorized: Dictionary of category -> list of articles
            
        Returns:
            Dictionary with filtered articles in each category
        """
        filtered_categorized = {}
        total_removed = 0
        
        for category, articles in categorized.items():
            filtered_articles = self.filter_articles(articles)
            removed = len(articles) - len(filtered_articles)
            
            if removed > 0:
                logger.info(f"  {category}: Removed {removed} articles")
                total_removed += removed
            
            # Only include category if it still has articles
            if filtered_articles:
                filtered_categorized[category] = filtered_articles
        
        if total_removed > 0:
            logger.info(f"Total articles filtered out: {total_removed}")
        
        return filtered_categorized

def test_filter():
    """Test the content filter with sample articles"""
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    filter = ContentFilter()
    
    test_articles = [
        {
            'title': 'New AI Tool Revolutionizes Code Generation',
            'content': 'A new AI application helps developers write code faster...',
            'source': 'TechCrunch'
        },
        {
            'title': 'Yankees Win World Series in Dramatic Fashion',
            'content': 'The New York Yankees defeated the Dodgers in game 7...',
            'source': 'ESPN'
        },
        {
            'title': 'Celebrity Couple Announces Engagement at Met Gala',
            'content': 'Hollywood stars revealed their engagement at the fashion event...',
            'source': 'People Magazine'
        },
        {
            'title': 'David Brooks on the Future of American Innovation',
            'content': 'David Brooks writes about technology and society...',
            'source': 'NYTimes'
        },
        {
            'title': 'Congress Debates New Tech Regulation Bill',
            'content': 'Lawmakers discuss tech regulation and antitrust measures for big tech companies...',
            'source': 'Washington Post'
        },
        {
            'title': 'Boston Restaurant Opens New Location',
            'content': 'Popular local eatery expands to second location...',
            'source': 'Boston Globe'
        },
        {
            'title': 'MIT Startup Raises $50M for Quantum Computing',
            'content': 'Boston-based quantum computing startup secures Series B...',
            'source': 'Boston Globe'
        }
    ]
    
    print("Testing Content Filter:")
    print("-" * 50)
    
    for article in test_articles:
        result = filter.should_include_article(article)
        status = "✅ INCLUDE" if result else "❌ EXCLUDE"
        print(f"{status}: {article['title'][:60]}...")
    
    print("\nFiltered Results:")
    filtered = filter.filter_articles(test_articles)
    print(f"Original: {len(test_articles)} articles")
    print(f"Filtered: {len(filtered)} articles")
    
    print("\nIncluded articles:")
    for article in filtered:
        print(f"  - {article['title']}")

if __name__ == "__main__":
    test_filter()