"""
Enhanced Markdown Generator V2
Creates daily updates with new structure, conditional headers, and embedded article links
"""

import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MarkdownGeneratorV2:
    def __init__(self, template_path: str = None):
        self.template_path = template_path or "config/templates/daily-update-v2.md"
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Load the markdown template"""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
        
        # Fallback template with new structure
        return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Default template with new section order"""
        return '''# Jonathan's {test_prefix}Daily Update for {day_of_week}, {date}

*Generated at {generation_time} | {total_articles} articles analyzed | {version}*

---

{weather_content}

{ai_technology_content}

{academia_research_content}

{moonshot_strategy_content}

{market_business_content}

{us_news_content}

{space_news_content}

{longform_articles_content}

{agentic_coding_content}

{reddit_highlights_content}

{daily_stoicism_content}'''
    
    def _format_section(self, title: str, content: str, articles: List[Dict],
                       include_article_links: bool = True, bullet_format: bool = False) -> str:
        """Format a section with styled header and thin line separator"""
        if not content and not articles:
            return ""  # Skip empty sections completely

        # Use HTML-style heading for better control
        section = f"\n<div style='font-size: 1.3em; font-weight: bold; text-decoration: underline; margin-bottom: 0.5em;'>{title}</div>\n"

        # All sections now use clean list format from AI-generated content
        if content:
            section += content + "\n\n"
        elif not articles:
            return ""  # Skip if no content and no articles

        # Thin line separator
        return section + "<hr style='border: none; border-top: 1px solid #ddd; margin: 1.5em 0;' />\n\n"
    
    def _format_weather(self, weather_data: Dict[str, Any]) -> str:
        """Format weather section for zip 01701 with detailed narrative"""
        if not weather_data or not weather_data.get('forecast'):
            return ""  # No content = no section at all
        
        forecast = weather_data['forecast']
        location = forecast.get('location', 'Worcester, MA (01701)')
        date = forecast.get('date', 'Today')
        high_temp = forecast.get('high_temp', '--')
        low_temp = forecast.get('low_temp', '--')
        
        weather_content = f"\n<div style='font-size: 1.3em; font-weight: bold; text-decoration: underline; margin-bottom: 0.5em;'>Weather (01701)</div>\n"
        weather_content += f"**{location}** - {date}\n\n"
        
        # Create detailed narrative if hourly data is available
        hourly = forecast.get('hourly_breakdown')
        if hourly:
            morning = hourly.get('morning', {})
            afternoon = hourly.get('afternoon', {})
            evening = hourly.get('evening', {})
            overnight = hourly.get('overnight', {})
            
            # Morning forecast
            if morning.get('temp'):
                weather_content += f"This morning will start with {morning.get('condition', 'conditions').lower()} and temperatures around {morning['temp']}°F"
                if morning.get('precip_prob', 0) > 30:
                    weather_content += f" with a {morning['precip_prob']}% chance of precipitation"
                weather_content += ". "
            
            # Afternoon forecast
            if afternoon.get('temp'):
                weather_content += f"The afternoon will see {afternoon.get('condition', 'conditions').lower()} with temperatures reaching {afternoon['temp']}°F"
                if afternoon.get('precip_prob', 0) > 30:
                    weather_content += f" and a {afternoon['precip_prob']}% chance of rain"
                weather_content += ". "
            
            # Evening forecast
            if evening.get('temp'):
                weather_content += f"Evening conditions will feature {evening.get('condition', 'conditions').lower()} as temperatures cool to {evening['temp']}°F"
                if evening.get('precip_prob', 0) > 30:
                    weather_content += f" with {evening['precip_prob']}% precipitation probability"
                weather_content += ". "
            
            # Overnight forecast
            if overnight.get('temp'):
                weather_content += f"Overnight will bring {overnight.get('condition', 'conditions').lower()} with lows around {overnight['temp']}°F"
                if overnight.get('precip_prob', 0) > 30:
                    weather_content += f" and a {overnight['precip_prob']}% chance of precipitation"
                weather_content += "."
        else:
            # Fallback to simple format
            condition = forecast.get('condition', 'Unknown conditions')
            weather_content += f"Today will feature {condition.lower()} with a high of {high_temp}°F and a low of {low_temp}°F."
            
            precipitation = forecast.get('precipitation', 0)
            if precipitation and precipitation > 0:
                weather_content += f" Expected precipitation: {precipitation} inches."
        
        weather_content += "\n\n<hr style='border: none; border-top: 1px solid #ddd; margin: 1.5em 0;' />\n\n"
        return weather_content
    
    def _format_stoicism_quote(self, quote_data: Dict[str, Any]) -> str:
        """Format daily Stoicism quote"""
        if not quote_data or not quote_data.get('quote'):
            return ""
        
        quote = quote_data.get('quote', '')
        author = quote_data.get('author', 'Stoic philosopher')
        
        return f"\n<div style='font-size: 1.3em; font-weight: bold; text-decoration: underline; margin-bottom: 0.5em;'>Daily Stoicism</div>\n\"{quote}\"\n\n— {author}\n\n<hr style='border: none; border-top: 1px solid #ddd; margin: 1.5em 0;' />\n\n"
    
    def _format_on_this_day(self, otd_data: Dict[str, Any], day_of_week: str, date_str: str) -> str:
        """Format the final 'On This Day' section with single interesting fact"""
        if not otd_data or not otd_data.get('events'):
            return ""  # No content = no section at all
        
        content = f"\n### On This Day - {day_of_week}, {date_str}\n"
        
        # Show only the single most interesting recent event
        event = otd_data['events'][0]  # We now only have one event
        year = event.get('year', 'Unknown')
        text = event.get('text', 'No description available')
        content += f"On this day in **{year}**, {text.lower() if text and text[0].isupper() else text}\n\n"
        
        return content
    
    def _count_articles(self, categorized_articles: Dict[str, list]) -> int:
        """Count total articles across all categories"""
        return sum(len(articles) for articles in categorized_articles.values())
    
    def _format_article_links(self, categorized_articles: Dict[str, list], section_configs: Dict[str, Dict]) -> str:
        """Format all article links in a single section at the bottom with small font"""
        content = "\n### Article Links\n\n<div class=\"article-links-section\">\n"
        has_articles = False

        for category, config in section_configs.items():
            if category in ['weather', 'daily_stoicism']:
                continue  # Skip non-article sections
                
            articles = categorized_articles.get(category, [])
            if articles:
                has_articles = True
                content += f"**{config['title']}:**\n"
                for article in articles[:8]:  # Limit articles per section
                    title_text = article.get('title', 'Untitled')
                    link = article.get('link', '#')
                    source = article.get('source', 'Unknown Source')
                    content += f"• [{title_text}]({link}) — {source}\n"
                content += "\n"
        
        if not has_articles:
            return ""
            
        return content + "</div>\n\n---\n\n"
    
    def generate_daily_update(self,
                            summaries: Dict[str, str],
                            categorized_articles: Dict[str, list],
                            supplementary_data: Dict[str, Any],
                            date: datetime = None,
                            version: str = "v0.3",
                            test_mode: bool = False) -> str:
        """Generate the complete daily update markdown with new structure"""

        if date is None:
            date = datetime.now()

        # New consolidated section mappings (On This Day removed)
        section_configs = {
            'weather': {'title': 'Weather (01701)'},
            'ai_technology': {'title': 'AI & Technology'},
            'academia_research': {'title': 'Academia & Research'},
            'moonshot_strategy': {'title': 'Moonshot Strategy'},
            'market_business': {'title': 'Business & Markets'},
            'us_news': {'title': 'US News Brief'},
            'space_news': {'title': 'Space & Exploration'},
            'longform_articles': {'title': 'Longform Reading'},
            'agentic_coding': {'title': 'Agentic Coding'},
            'reddit_highlights': {'title': 'Reddit Highlights'},
            'daily_stoicism': {'title': 'Daily Stoicism'}
        }

        # Track empty sections
        empty_sections = []

        # Generate sections
        template_vars = {
            'test_prefix': 'Test ' if test_mode else '',
            'day_of_week': date.strftime("%A"),
            'date': date.strftime("%B %d, %Y"),
            'generation_time': datetime.now().strftime("%I:%M %p EST"),
            'last_updated': datetime.now().strftime("%I:%M %p EST on %B %d, %Y"),
            'total_articles': self._count_articles(categorized_articles),
            'version': version
        }
        
        # Special handling for specific sections
        template_vars['weather_content'] = self._format_weather(
            supplementary_data.get('weather', {})
        )

        template_vars['daily_stoicism_content'] = self._format_stoicism_quote(
            supplementary_data.get('stoicism_quote', {})
        )

        # Check special sections for emptiness
        if not supplementary_data.get('weather', {}).get('forecast'):
            empty_sections.append('Weather (01701)')
        if not supplementary_data.get('stoicism_quote', {}).get('quote'):
            empty_sections.append('Daily Stoicism')
        
        # Generate content for all other sections
        for category, config in section_configs.items():
            if category in ['weather', 'daily_stoicism']:
                continue  # Already handled above
            
            content = summaries.get(category, '')
            articles = categorized_articles.get(category, [])
            
            # Check if section is empty
            if not content and not articles:
                empty_sections.append(config['title'])
                template_vars[f'{category}_content'] = ""
            else:
                template_vars[f'{category}_content'] = self._format_section(
                    config['title'],
                    content,
                    articles
                )
        
        # Article links section removed - all links are now inline in bullet points
        
        # Generate markdown content
        try:
            markdown_content = self.template.format(**template_vars)
            print(f"DEBUG: Total markdown length: {len(markdown_content)}")
            print(f"DEBUG: Contains 'Article Links': {'Article Links' in markdown_content}")
            
            # Add empty sections note before the footer if needed
            if empty_sections:
                # Create a proper sentence listing empty sections
                if len(empty_sections) == 1:
                    empty_note = f"There are no updates today for {empty_sections[0]}."
                elif len(empty_sections) == 2:
                    empty_note = f"There are no updates today for {empty_sections[0]} and {empty_sections[1]}."
                else:
                    empty_note = f"There are no updates today for {', '.join(empty_sections[:-1])}, and {empty_sections[-1]}."
                
                # Insert before the final footer
                footer_marker = "---\n*Daily update powered by AI"
                if footer_marker in markdown_content:
                    markdown_content = markdown_content.replace(
                        footer_marker,
                        f"{empty_note}\n\n{footer_marker}"
                    )
            
            # Add minimal Obsidian frontmatter
            frontmatter = f'''---
date: {date.strftime("%Y-%m-%d")}
type: daily-update
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
type: daily-update-error
tags: [ai-generated, error]
---

# Daily Update - {date.strftime("%B %d, %Y")}

*Error generating content at {datetime.now().strftime("%I:%M %p EST")}*

### Error Details
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
            
            logger.info(f"Daily update v2 saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

# Test function
if __name__ == "__main__":
    from datetime import datetime
    
    # Mock data for testing
    mock_summaries = {
        'ai': 'Recent developments in [AI coding assistants](link) are transforming how developers work...',
        'tech_headlines': 'Major tech companies announced [new products](link) this week...',
        'market_business': 'Markets responded positively to [earnings reports](link) from major corporations...',
    }
    
    mock_articles = {
        'ai': [{'title': 'AI Coding Revolution', 'source': 'Tech Source', 'link': 'https://example.com'}],
        'academic_research': [{'title': 'New Management Study', 'source': 'AMJ', 'link': 'https://example.com'}]
    }
    
    mock_supplementary = {
        'on_this_day': {
            'date': 'September 10',
            'events': [
                {'year': '2001', 'text': 'Important historical event occurred'}
            ]
        },
        'stoicism_quote': {
            'quote': 'The best revenge is not to be like your enemy.',
            'author': 'Marcus Aurelius'
        }
    }
    
    generator = MarkdownGeneratorV2()
    content = generator.generate_daily_update(
        mock_summaries, mock_articles, mock_supplementary
    )
    
    print("=== GENERATED MARKDOWN V2 ===")
    print(content[:800] + "...")
    print(f"\nWord count: {len(content.split())}")