"""
Markdown Generator V3
Creates minimalist, narrative-rich daily updates with focus on discovery
"""

import os
from datetime import datetime
from typing import Dict, Any, List
import logging
from processors.narrative_enhancer import NarrativeEnhancer

logger = logging.getLogger(__name__)

class MarkdownGeneratorV3:
    def __init__(self):
        self.narrative_enhancer = NarrativeEnhancer()
        self.template = self._get_template()
        
        # Section icons (professional, minimal)
        self.section_icons = {
            'moonshot_frontiers': '🚀',  # Using minimal emoji only where essential
            'ai_future_computing': '◆',
            'space_frontier_science': '☆',
            'strategic_thinking': '◎',
            'academic_research': '◈',
            'new_tech_tools': '🔧',
            'from_reddit': '📱',
            'cool_news': '◇',
            'weather': '◌',
            'daily_reflection': '—'
        }
    
    def _get_template(self) -> str:
        """Minimalist template focused on content"""
        return '''**{day_of_week}, {date}**  
*Curated discoveries in science, technology, and human ambition*

{weather_section}

{moonshot_section}

{ai_section}

{space_section}

{strategic_section}

{research_section}

{tech_tools_section}

{from_reddit_section}

{cool_news_section}

{reflection_section}

---
*{total_articles} articles analyzed • {novel_articles} discoveries surfaced*'''
    
    def generate_daily_update(self,
                            summaries: Dict[str, str],
                            categorized_articles: Dict[str, List],
                            supplementary_data: Dict[str, Any],
                            date: datetime = None) -> str:
        """Generate v3 daily update with enhanced narratives"""
        
        if date is None:
            date = datetime.now()
        
        # Filter articles by novelty
        filtered_articles = self.narrative_enhancer.filter_by_novelty(categorized_articles)
        
        # Map old categories to new ones
        category_mapping = {
            'moonshot_strategy': 'moonshot_frontiers',
            'ai': 'ai_future_computing', 
            'space_news': 'space_frontier_science',
            'longform_articles': 'strategic_thinking',
            'academic_research': 'academic_research',
            'tech_tools': 'new_tech_tools',
            'from_reddit': 'from_reddit'
        }
        
        # Remap articles to new categories
        remapped_articles = {}
        for old_cat, new_cat in category_mapping.items():
            if old_cat in filtered_articles:
                remapped_articles[new_cat] = filtered_articles[old_cat]
        
        # Add cool news (combine interesting items from various sources)
        cool_news = []
        for cat in ['tech_headlines', 'higher_education', 'market_business']:
            if cat in filtered_articles:
                # Take only highest scoring articles
                for article in filtered_articles[cat][:2]:
                    if article.get('novelty_score', 0) > 2.0:
                        cool_news.append(article)
        if cool_news:
            remapped_articles['cool_news'] = cool_news[:5]
        
        # Generate sections
        template_vars = {
            'day_of_week': date.strftime("%A"),
            'date': date.strftime("%B %d, %Y"),
            'total_articles': self._count_total_articles(categorized_articles),
            'novel_articles': self._count_novel_articles(remapped_articles)
        }
        
        # Weather section (minimal)
        template_vars['weather_section'] = self._format_weather_minimal(
            supplementary_data.get('weather', {})
        )
        
        # Generate enhanced narrative sections
        template_vars['moonshot_section'] = self._format_section(
            'moonshot_frontiers',
            'Moonshot Frontiers',
            remapped_articles.get('moonshot_frontiers', []),
            summaries.get('moonshot_strategy', '')
        )
        
        template_vars['ai_section'] = self._format_section(
            'ai_future_computing',
            'AI & Future Computing',
            remapped_articles.get('ai_future_computing', []),
            summaries.get('ai', '')
        )
        
        template_vars['space_section'] = self._format_section(
            'space_frontier_science',
            'Space & Frontier Science',
            remapped_articles.get('space_frontier_science', []),
            summaries.get('space_news', '')
        )
        
        template_vars['strategic_section'] = self._format_section(
            'strategic_thinking',
            'Strategic Thinking',
            remapped_articles.get('strategic_thinking', []),
            summaries.get('longform_articles', '')
        )
        
        template_vars['research_section'] = self._format_section(
            'academic_research',
            'Academic Research',
            remapped_articles.get('academic_research', []),
            summaries.get('academic_research', '')
        )
        
        # Tech tools section (special formatting - bullet points)
        template_vars['tech_tools_section'] = self._format_tech_tools_section(
            remapped_articles.get('new_tech_tools', [])
        )
        
        # From Reddit section  
        template_vars['from_reddit_section'] = self._format_section(
            'from_reddit',
            'From Reddit',
            remapped_articles.get('from_reddit', []),
            ''
        )
        
        template_vars['cool_news_section'] = self._format_section(
            'cool_news',
            'Cool News',
            remapped_articles.get('cool_news', []),
            ''
        )
        
        # Daily reflection (replacing stoicism with broader wisdom)
        template_vars['reflection_section'] = self._format_reflection(
            supplementary_data.get('stoicism_quote', {})
        )
        
        # Generate final markdown
        try:
            markdown_content = self.template.format(**template_vars)
            
            # Clean opening without metadata  
            opening = f'''# My Morning Update
'''
            
            # Add metadata at bottom for Obsidian
            bottom_metadata = f'''

---
*Metadata: {date.strftime("%Y-%m-%d")} • v3 • discovery-focused*'''
            
            return opening + markdown_content + bottom_metadata
            
        except Exception as e:
            logger.error(f"Error generating markdown: {str(e)}")
            raise
    
    def _format_section(self, 
                       section_key: str,
                       section_title: str, 
                       articles: List[Dict],
                       ai_summary: str) -> str:
        """Format section with enhanced narrative"""
        
        if not articles:
            return ""
        
        icon = self.section_icons.get(section_key, '•')
        
        # Generate enhanced narrative
        narrative = self.narrative_enhancer.generate_enhanced_narrative(
            section_key,
            articles,
            ai_summary
        )
        
        if not narrative:
            return ""
        
        # Minimal section design
        return f'''
**{icon} {section_title}**

{narrative}
'''
    
    def _format_tech_tools_section(self, articles: List[Dict]) -> str:
        """Format tech tools section with bullet points"""
        
        if not articles:
            return ""
        
        icon = self.section_icons.get('new_tech_tools', '🔧')
        
        # Sort by novelty score and take top items
        sorted_articles = sorted(articles, key=lambda x: x.get('novelty_score', 0), reverse=True)
        top_articles = sorted_articles[:8]  # Max 8 items as per instructions
        
        bullet_points = []
        for article in top_articles:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            
            # Create one-sentence description from title
            # Remove common prefixes and clean up
            clean_title = title.replace('New:', '').replace('Update:', '').replace('Introducing', '').strip()
            
            bullet_point = f"• {clean_title}. [{article.get('source', 'Link')}]({url})"
            bullet_points.append(bullet_point)
        
        if not bullet_points:
            return ""
        
        return f'''
**{icon} New Tech Tools**

{chr(10).join(bullet_points)}
'''
    
    def _format_weather_minimal(self, weather_data: Dict) -> str:
        """Format comprehensive weather forecast for Framingham, MA"""
        if not weather_data or not weather_data.get('forecast'):
            return "*Weather: Forecast unavailable*\n"
        
        forecast = weather_data['forecast']
        location = weather_data.get('location', 'Framingham, MA')
        
        # Extract hourly data if available
        hourly = forecast.get('hourly_breakdown', {})
        high_temp = forecast.get('high_temp', 'N/A') 
        low_temp = forecast.get('low_temp', 'N/A')
        
        if hourly:
            morning = hourly.get('morning', {})
            afternoon = hourly.get('afternoon', {})
            evening = hourly.get('evening', {})
            
            # Build descriptive forecast paragraph
            forecast_parts = []
            
            if morning.get('temp'):
                morning_desc = f"starting at {morning['temp']}°F this morning"
                if morning.get('precip_prob', 0) > 30:
                    morning_desc += f" with a {morning['precip_prob']}% chance of precipitation"
                forecast_parts.append(morning_desc)
            
            if afternoon.get('temp'):
                afternoon_desc = f"reaching {afternoon['temp']}°F this afternoon"
                if afternoon.get('condition'):
                    afternoon_desc += f" under {afternoon['condition'].lower()} skies"
                forecast_parts.append(afternoon_desc)
                
            if evening.get('temp'):
                evening_desc = f"cooling to {evening['temp']}°F by evening"
                if evening.get('precip_prob', 0) > 20:
                    evening_desc += f" with possible precipitation ({evening['precip_prob']}% chance)"
                forecast_parts.append(evening_desc)
            
            if forecast_parts:
                forecast_text = f"Today in {location} will see temperatures {', '.join(forecast_parts)}."
            else:
                forecast_text = f"Today in {location}: High {high_temp}°F, Low {low_temp}°F."
        else:
            # Fallback for minimal data
            conditions = forecast.get('conditions', 'Variable conditions')
            forecast_text = f"Today in {location}: {conditions.capitalize()} with a high of {high_temp}°F and low of {low_temp}°F."
        
        return f"*{forecast_text}*\n"
    
    def _format_reflection(self, quote_data: Dict) -> str:
        """Format daily reflection/wisdom"""
        if not quote_data or not quote_data.get('quote'):
            return ""
        
        quote = quote_data.get('quote', '')
        author = quote_data.get('author', 'Unknown')
        
        return f'''
**Daily Reflection**

*"{quote}"*  
— {author}'''
    
    def _count_total_articles(self, articles: Dict[str, List]) -> int:
        """Count total articles analyzed"""
        return sum(len(cat_articles) for cat_articles in articles.values())
    
    def _count_novel_articles(self, articles: Dict[str, List]) -> int:
        """Count articles that made it through novelty filter"""
        return sum(len(cat_articles) for cat_articles in articles.values())
    
    def save_to_file(self, content: str, output_dir: str = None) -> str:
        """Save markdown to file"""
        if output_dir is None:
            output_dir = os.path.expanduser("~/Documents/Obsidian Vault/Daily Updates (Agent)")
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-daily-discoveries-v3.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Daily discoveries v3 saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise