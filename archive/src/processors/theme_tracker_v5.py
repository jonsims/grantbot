"""
Theme Tracker V5
Enhanced meta-summary with variable length, category weighting, and tone control
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ThemeTrackerV5:
    def __init__(self, history_dir: str = "cache/themes", settings_file: str = "config/v5-settings.json"):
        self.history_dir = Path(history_dir)
        self.history_file = self.history_dir / "theme_history.json"
        self.settings_file = Path(settings_file)
        self.max_days = 7
        self.tone = self._load_tone_setting()

        # Create directory if it doesn't exist
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Load existing history
        self.history = self._load_history()

    def _load_tone_setting(self) -> str:
        """Load tone setting from config file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    tone = settings.get('meta_summary', {}).get('tone', 'mixed')
                    logger.info(f"Loaded tone setting: {tone}")
                    return tone
            except Exception as e:
                logger.error(f"Error loading tone setting: {e}")
                return 'mixed'
        return 'mixed'

    def _load_history(self) -> Dict[str, Any]:
        """Load theme history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)

                # Clean old entries (older than 7 days)
                cutoff = (datetime.now() - timedelta(days=self.max_days)).strftime('%Y-%m-%d')
                cleaned = {date: data for date, data in history.items() if date >= cutoff}

                logger.info(f"Loaded theme history: {len(cleaned)} days")
                return cleaned
            except Exception as e:
                logger.error(f"Error loading theme history: {e}")
                return {}
        return {}

    def _save_history(self):
        """Save theme history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Saved theme history: {len(self.history)} days")
        except Exception as e:
            logger.error(f"Error saving theme history: {e}")

    def extract_themes_from_articles(self, categorized_articles: Dict[str, List[Dict]]) -> List[str]:
        """Extract key themes from today's articles (without AI for now)"""
        themes = []

        # Extract from titles and categories
        for category, articles in categorized_articles.items():
            if articles:
                # Category itself is a theme
                themes.append(category.replace('_', ' ').title())

                # Extract common words from titles (simple approach)
                for article in articles[:5]:  # Top 5 articles per category
                    title = article.get('title', '')
                    # Extract potential themes (words > 4 chars, capitalized or all caps)
                    words = title.split()
                    for word in words:
                        if len(word) > 4 and (word[0].isupper() or word.isupper()):
                            word_clean = word.strip('.,!?;:').title()
                            if word_clean and word_clean not in themes:
                                themes.append(word_clean)

        return themes[:15]  # Limit to top 15 themes

    def store_today_themes(self, categorized_articles: Dict[str, List[Dict]], summaries: Dict[str, str]):
        """Store today's themes and summaries for future reference"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Extract themes
        themes = self.extract_themes_from_articles(categorized_articles)

        # Store article count per category
        category_counts = {cat: len(articles) for cat, articles in categorized_articles.items() if articles}

        # Store today's data
        self.history[today] = {
            'date': today,
            'themes': themes,
            'categories': list(category_counts.keys()),
            'article_count': sum(category_counts.values()),
            'category_counts': category_counts,
            'summaries': {cat: summary[:200] for cat, summary in summaries.items()}  # Store first 200 chars
        }

        self._save_history()
        logger.info(f"Stored themes for {today}: {len(themes)} themes, {sum(category_counts.values())} articles")

    def _calculate_word_target(self, total_articles: int) -> int:
        """Calculate target word count based on article volume"""
        # Base: 50 words for minimal news days
        # Scale: +15 words per 10 articles
        # Cap: 400 words maximum
        base = 50
        scale = (total_articles // 10) * 15
        target = min(base + scale, 400)
        logger.info(f"Calculated word target: {target} words for {total_articles} articles")
        return target

    def get_week_context(self) -> Dict[str, Any]:
        """Get context from the past week for meta-summary generation"""
        if not self.history:
            return {
                'days_analyzed': 0,
                'total_articles': 0,
                'top_themes': [],
                'active_categories': [],
                'daily_summaries': []
            }

        # Analyze history
        all_themes = []
        all_categories = set()
        total_articles = 0
        daily_data = []

        for date, data in sorted(self.history.items()):
            all_themes.extend(data.get('themes', []))
            all_categories.update(data.get('categories', []))
            total_articles += data.get('article_count', 0)

            daily_data.append({
                'date': date,
                'article_count': data.get('article_count', 0),
                'top_categories': list(data.get('category_counts', {}).keys())[:3]
            })

        # Count theme frequency
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        # Get top themes (appeared multiple times)
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        recurring_themes = [theme for theme, count in top_themes if count >= 2]

        return {
            'days_analyzed': len(self.history),
            'total_articles': total_articles,
            'top_themes': recurring_themes[:8],  # Top 8 recurring themes
            'active_categories': list(all_categories),
            'daily_summaries': daily_data[-7:]  # Last 7 days
        }

    def generate_meta_summary_prompt(self,
                                     categorized_articles: Dict[str, List[Dict]],
                                     summaries: Dict[str, str]) -> str:
        """Generate prompt for AI meta-summary with week context, variable length, and category weighting"""

        week_context = self.get_week_context()

        # Calculate today's article count and category weights
        category_counts = {cat: len(articles) for cat, articles in categorized_articles.items() if articles}
        total_articles_today = sum(category_counts.values())

        # Calculate target word count based on article volume
        word_target = self._calculate_word_target(total_articles_today)

        # Get top 3 categories by article count (weighted focus)
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_category_names = [cat for cat, _ in top_categories]

        # Build context string
        context_str = ""
        if week_context['days_analyzed'] > 0:
            context_str = f"""
PAST WEEK CONTEXT ({week_context['days_analyzed']} days analyzed):
- Total articles analyzed: {week_context['total_articles']}
- Recurring themes: {', '.join(week_context['top_themes'])}
- Active categories: {', '.join(week_context['active_categories'])}
"""
            # Add daily breakdown
            for day in week_context['daily_summaries']:
                context_str += f"\n- {day['date']}: {day['article_count']} articles ({', '.join(day['top_categories'][:2])})"

        # Build today's summary context with weighted focus
        today_context = f"\n\nTODAY'S SUMMARIES ({total_articles_today} articles):\n"
        today_context += f"\nHIGHEST VOLUME CATEGORIES (focus here): {', '.join(top_category_names)}\n"

        for category, summary in summaries.items():
            if summary:
                article_count = category_counts.get(category, 0)
                today_context += f"\n{category.upper()} ({article_count} articles):\n{summary[:300]}...\n"

        # Tone-specific instructions
        tone_instructions = {
            'analytical': 'Use a rigorous, data-driven tone like The Economist. Focus on implications and underlying trends.',
            'conversational': 'Use an accessible, engaging tone like Morning Brew. Make complex topics relatable.',
            'mixed': 'Blend analytical depth with accessible language. Think Stratechery or Axios.'
        }
        tone_guide = tone_instructions.get(self.tone, tone_instructions['mixed'])

        prompt = f"""You are analyzing a week of daily news updates to identify key themes and patterns.

{context_str}

{today_context}

Based on the past week's coverage and today's updates, write a compelling {word_target}-word meta-summary that:

1. PRIORITIZE IMPACT: Focus on the most important/impactful stories, especially from high-volume categories ({', '.join(top_category_names)})
2. WITHIN-CATEGORY ANALYSIS: For each major category, show how articles within THAT SAME category relate to each other and build a cohesive narrative
3. SEPARATE INSIGHTS: Provide separate observations for each category - DO NOT connect or compare articles from different categories
4. NEW vs ONGOING: For each category, highlight what's NEW today vs. ongoing stories from the past week
5. ACTIONABLE INSIGHTS: Include 1-2 specific takeaways per category when relevant
6. HISTORICAL CONTEXT: When relevant within a category, connect to broader trends in that domain

IMPORTANT CONSTRAINT: Analyze each category independently. Do NOT draw connections, comparisons, or patterns between different categories (e.g., do NOT connect AI with Research, or Tech with Markets). Each category stands alone.

TONE: {tone_guide}

Start directly with the insights, organized by category. Be specific with examples when possible. Avoid generic phrases like "This week's updates reveal..."

TARGET: Approximately {word_target} words (±10% acceptable)

Meta-summary:"""

        return prompt

    def format_meta_summary(self, ai_summary: str, week_context: Dict[str, Any]) -> str:
        """Format the meta-summary with metadata"""

        # Add subtle metadata footer
        articles_analyzed = week_context.get('total_articles', 0)
        days_analyzed = week_context.get('days_analyzed', 0)

        footer = f"\n\n*Based on {articles_analyzed} articles analyzed over {days_analyzed} days*"

        return ai_summary.strip() + footer

# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test theme tracker
    tracker = ThemeTracker()

    # Mock data
    mock_articles = {
        'ai_technology': [
            {'title': 'OpenAI Releases GPT-5', 'content': 'Major AI advancement...'},
            {'title': 'Anthropic Claude Updates', 'content': 'New features...'}
        ],
        'space_news': [
            {'title': 'SpaceX Starship Launch', 'content': 'Historic moment...'}
        ]
    }

    mock_summaries = {
        'ai_technology': 'AI developments this week focus on...',
        'space_news': 'Space exploration advances with...'
    }

    # Store themes
    tracker.store_today_themes(mock_articles, mock_summaries)

    # Get context
    context = tracker.get_week_context()
    print(f"\nWeek context: {json.dumps(context, indent=2)}")

    # Generate prompt
    prompt = tracker.generate_meta_summary_prompt(mock_articles, mock_summaries)
    print(f"\nGenerated prompt:\n{prompt}")
