"""
Markdown Generator
Creates the final daily update markdown file with proper formatting
"""

import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self, template_path: str = None):
        self.template_path = template_path or "config/templates/daily-update.md"
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Load the markdown template"""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
        
        # Fallback template
        return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Default template if file not found"""
        return '''# Daily Update - {date}

*Generated at {generation_time} | {total_articles} articles analyzed*

---

## 🚀 Moonshot Innovations
{moonshots_content}

## 📊 Strategic Management Insights
{strategic_content}

## 💻 Tech Headlines
{tech_content}

## 🇺🇸 US News Brief
{us_news_content}

## 📈 Market & Business Update
{market_content}

## 📅 On This Day
{on_this_day_content}

## 🏙️ Boston Tech & Entrepreneurship
{boston_content}

---

## 📰 Article References
{article_links}

---
*Daily update powered by AI*'''
    
    def _format_on_this_day(self, otd_data: Dict[str, Any]) -> str:
        """Format the 'On This Day' section"""
        if not otd_data or not otd_data.get('events'):
            return f"On {datetime.now().strftime('%B %d')}, historical events are being compiled..."
        
        content = f"On **{otd_data['date']}** in history:\n\n"
        
        for event in otd_data['events'][:3]:  # Top 3 events
            year = event.get('year', 'Unknown')
            text = event.get('text', 'No description available')
            content += f"- **{year}**: {text}\n"
        
        return content.strip()
    
    def _count_articles(self, categorized_articles: Dict[str, list]) -> int:
        """Count total articles across all categories"""
        return sum(len(articles) for articles in categorized_articles.values())
    
    def _ensure_content_length(self, content: str, target_words: int, category: str) -> str:
        """Ensure content meets minimum length requirements"""
        words = len(content.split())
        
        if words < target_words * 0.5:  # If less than 50% of target
            content += f"\n\n*More {category.replace('_', ' ')} updates will be available as sources are expanded.*"
        
        return content
    
    def generate_daily_update(self, 
                            summaries: Dict[str, str],
                            categorized_articles: Dict[str, list],
                            supplementary_data: Dict[str, Any],
                            article_links: str,
                            date: datetime = None) -> str:
        """Generate the complete daily update markdown"""
        
        if date is None:
            date = datetime.now()
        
        # Word targets for validation
        word_targets = {
            'moonshots': 150,
            'strategic_management': 100,
            'tech_headlines': 200,
            'us_news': 150,
            'market_business': 200,
            'boston_tech': 100
        }
        
        # Ensure minimum content length
        processed_summaries = {}
        for category, content in summaries.items():
            target = word_targets.get(category, 100)
            processed_summaries[category] = self._ensure_content_length(content, target, category)
        
        # Prepare template variables
        template_vars = {
            'date': date.strftime("%B %d, %Y"),
            'generation_time': datetime.now().strftime("%I:%M %p EST"),
            'total_articles': self._count_articles(categorized_articles),
            'moonshots_content': processed_summaries.get('moonshots', 'No moonshot innovations found today.'),
            'strategic_content': processed_summaries.get('strategic_management', 'No strategic management insights found today.'),
            'tech_content': processed_summaries.get('tech_headlines', 'No major tech headlines found today.'),
            'us_news_content': processed_summaries.get('us_news', 'No significant US news found today.'),
            'market_content': processed_summaries.get('market_business', 'No major market movements found today.'),
            'boston_content': processed_summaries.get('boston_tech', 'No Boston tech news found today.'),
            'on_this_day_content': self._format_on_this_day(supplementary_data.get('on_this_day', {})),
            'article_links': article_links or 'No articles referenced today.'
        }
        
        # Generate markdown content
        try:
            markdown_content = self.template.format(**template_vars)
            
            # Add Obsidian frontmatter
            frontmatter = f'''---
date: {date.strftime("%Y-%m-%d")}
type: daily-update
tags: [ai-generated, news, daily]
---

'''
            
            return frontmatter + markdown_content
            
        except KeyError as e:
            logger.error(f"Template formatting error: {str(e)}")
            return self._generate_error_content(date, str(e))
    
    def _generate_error_content(self, date: datetime, error: str) -> str:
        """Generate error content when template fails"""
        return f'''---
date: {date.strftime("%Y-%m-%d")}
type: daily-update
tags: [ai-generated, error]
---

# Daily Update - {date.strftime("%B %d, %Y")}

*Error generating content at {datetime.now().strftime("%I:%M %p EST")}*

## Error Details
Template generation failed: {error}

Please check the configuration and try again.
'''
    
    def save_to_file(self, content: str, output_dir: str, date: datetime = None) -> str:
        """Save markdown content to file"""
        if date is None:
            date = datetime.now()
        
        filename = f"{date.strftime('%Y-%m-%d')}-daily-update.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Daily update saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def get_word_count(self, content: str) -> int:
        """Get word count of content (excluding frontmatter and markdown formatting)"""
        # Remove frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Remove markdown formatting characters
        import re
        content = re.sub(r'[#*_`\[\]()]+', '', content)
        content = re.sub(r'https?://\S+', '', content)  # Remove URLs
        
        words = content.split()
        return len(words)

# Test function
if __name__ == "__main__":
    from datetime import datetime
    
    # Mock data for testing
    mock_summaries = {
        'moonshots': 'Recent breakthroughs in quantum computing show promise for solving grand challenges.',
        'tech_headlines': 'Major tech developments include AI advances and new product launches.',
        'market_business': 'Markets showed mixed signals with technology stocks leading gains.',
    }
    
    mock_articles = {
        'moonshots': [{'title': 'Test Article', 'source': 'Test Source'}],
        'tech_headlines': [{'title': 'Tech News', 'source': 'Tech Source'}]
    }
    
    mock_supplementary = {
        'on_this_day': {
            'date': 'September 10',
            'events': [
                {'year': '2001', 'text': 'Important historical event occurred'}
            ]
        }
    }
    
    generator = MarkdownGenerator()
    content = generator.generate_daily_update(
        mock_summaries, mock_articles, mock_supplementary, "Mock article links"
    )
    
    print("=== GENERATED MARKDOWN ===")
    print(content[:500] + "...")
    print(f"\nWord count: {generator.get_word_count(content)}")