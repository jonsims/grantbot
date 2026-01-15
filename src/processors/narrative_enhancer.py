"""
Narrative Enhancement Processor for v3
Creates rich, contextual narratives that weave articles together
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import yaml
import os

logger = logging.getLogger(__name__)

class NarrativeEnhancer:
    def __init__(self, config_path: str = None):
        """Initialize the narrative enhancer with content priorities"""
        self.config_path = config_path or "config/content_priorities_v3.yaml"
        self.priorities = self._load_priorities()
        self.article_types = self.priorities.get('article_types', {})
        
        # Source abbreviations for cleaner formatting
        self.source_abbreviations = {
            'Strategic Management Journal': 'SMJ',
            'Academy of Management Journal': 'AMJ',
            'Academy of Management Review': 'AMR',
            'Administrative Science Quarterly': 'ASQ',
            'Organization Science': 'OS',
            'Journal of Business Venturing': 'JBV',
            'Research Policy': 'RP',
            'MIT Sloan Management Review': 'MIT SMR',
            'Harvard Business Review': 'HBR',
            'The Wall Street Journal': 'WSJ',
            'The New York Times': 'NYTimes',
            'Financial Times': 'FT',
            'Business Insider': 'BI',
            'MIT Technology Review': 'MIT Tech Review',
            'Nature': 'Nature',
            'Science': 'Science',
            'Proceedings of the National Academy of Sciences': 'PNAS',
            'Journal of the American Medical Association': 'JAMA',
            'New England Journal of Medicine': 'NEJM',
            'The Lancet': 'Lancet',
            'Artificial Intelligence': 'AI Journal',
            'Journal of Machine Learning Research': 'JMLR',
            'International Conference on Machine Learning': 'ICML',
            'Neural Information Processing Systems': 'NeurIPS',
            'Association for Computing Machinery': 'ACM',
            'Institute of Electrical and Electronics Engineers': 'IEEE',
            'Communications of the ACM': 'CACM',
            'Harvard Business School': 'HBS',
            'Stanford Business School': 'Stanford GSB',
            'Wharton School': 'Wharton',
            'McKinsey & Company': 'McKinsey',
            'Boston Consulting Group': 'BCG',
            'Bain & Company': 'Bain',
            'National Aeronautics and Space Administration': 'NASA',
            'European Space Agency': 'ESA',
            'Massachusetts Institute of Technology': 'MIT',
            'Stanford University': 'Stanford',
            'Harvard University': 'Harvard',
            'University of California': 'UC',
            'Carnegie Mellon University': 'CMU'
        }
        
    def _load_priorities(self) -> Dict:
        """Load content priorities from config"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            logger.error(f"Error loading priorities: {e}")
            return {}
    
    def detect_article_type(self, article: Dict) -> Tuple[str, int]:
        """
        Detect article type and estimate read time
        Returns: (type, read_time_minutes)
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        combined_text = f"{title} {description}"
        
        # Detect type based on indicators
        detected_type = "article"  # default
        for type_name, type_config in self.article_types.items():
            indicators = type_config.get('indicators', [])
            for indicator in indicators:
                if indicator.lower() in combined_text:
                    detected_type = type_name
                    break
        
        # Estimate read time (rough: 200 words per minute)
        word_count = len(description.split())
        if detected_type == "research":
            read_time = max(10, word_count // 150)  # Research papers are slower
        elif detected_type in ["essay", "analysis"]:
            read_time = max(7, word_count // 180)
        else:
            read_time = max(3, word_count // 200)
        
        return detected_type, read_time
    
    def score_article_novelty(self, article: Dict) -> float:
        """
        Score article based on novelty and interest factors
        Higher score = more interesting/novel
        """
        score = 0.0
        
        title = article.get('title', '').lower()
        source = article.get('source', '').lower()
        description = article.get('description', '').lower()
        
        # Apply novelty factors
        novelty = self.priorities.get('article_scoring', {}).get('novelty_factors', {})
        
        # Check for unknown/niche sources
        mainstream_sources = ['cnn', 'fox', 'msnbc', 'bloomberg', 'reuters', 'ap news']
        if not any(ms in source for ms in mainstream_sources):
            score += novelty.get('unknown_source', 3.0)
        
        # Check for innovative keywords
        innovative_keywords = ['breakthrough', 'first', 'novel', 'unprecedented', 'discovery']
        for keyword in innovative_keywords:
            if keyword in title or keyword in description:
                score += novelty.get('innovative_approach', 1.5)
                break
        
        # Apply penalties
        penalties = self.priorities.get('article_scoring', {}).get('penalty_factors', {})
        
        # Political content
        political_keywords = ['democrat', 'republican', 'congress', 'senate', 'election']
        if any(pk in title for pk in political_keywords):
            score += penalties.get('political_content', -2.5)
        
        # Clickbait detection
        clickbait_patterns = ['you won\'t believe', 'this one trick', 'shocking', 'destroyed']
        if any(cb in title for cb in clickbait_patterns):
            score += penalties.get('clickbait_title', -3.0)
        
        # Boost personal interests
        personal_interests = self.priorities.get('personal_interests', {}).get('boost_keywords', [])
        for interest in personal_interests:
            if interest.lower() in title or interest.lower() in description:
                score += 2.0
                break
        
        return score
    
    def select_top_articles(self, articles: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Select top articles based on novelty scoring
        """
        # Score and sort articles
        scored_articles = []
        for article in articles:
            score = self.score_article_novelty(article)
            article_type, read_time = self.detect_article_type(article)
            
            article_with_metadata = article.copy()
            article_with_metadata['novelty_score'] = score
            article_with_metadata['article_type'] = article_type
            article_with_metadata['read_time'] = read_time
            
            scored_articles.append(article_with_metadata)
        
        # Sort by novelty score
        scored_articles.sort(key=lambda x: x['novelty_score'], reverse=True)
        
        # Return top articles with metadata
        return scored_articles[:limit]
    
    def generate_enhanced_narrative(self, 
                                   section_name: str,
                                   articles: List[Dict],
                                   ai_summary: str = None) -> str:
        """
        Generate adaptive narrative that scales complexity based on article count
        """
        if not articles:
            return ""
        
        # Select and enhance top articles
        top_articles = self.select_top_articles(articles, limit=5)
        
        if not top_articles:
            return ""
        
        article_count = len(top_articles)
        
        # Route to appropriate narrative template based on article count
        if article_count == 1:
            return self._generate_minimal_narrative(section_name, top_articles[0])
        elif article_count == 2:
            return self._generate_connection_narrative(section_name, top_articles)
        else:  # 3+ articles
            return self._generate_full_narrative(section_name, top_articles)
    
    def _generate_minimal_narrative(self, section_name: str, article: Dict) -> str:
        """Generate minimal narrative for single article (2-3 sentences)"""
        title = article.get('title', 'Untitled')
        link = article.get('link', '#')
        source = article.get('source', 'Unknown')
        article_type = article.get('article_type', 'Article')
        description = article.get('description', '')
        
        abbreviated_source = self._abbreviate_source(source)
        type_tag = ""
        if self._should_show_article_type(article_type):
            type_tag = f" [{article_type.capitalize()}]"
        
        # Brief domain context (1 sentence)
        domain_context = self._get_minimal_domain_context(section_name)
        
        # Article presentation with brief technical context
        brief_context = self._extract_brief_technical_context(description)
        context_phrase = f", {brief_context}" if brief_context else ""
        
        # Single practical implication
        implication = self._extract_single_implication(section_name, description)
        
        return f"{domain_context} {abbreviated_source} examines [{title}]({link}){type_tag}{context_phrase}. {implication}"
    
    def _generate_connection_narrative(self, section_name: str, articles: List[Dict]) -> str:
        """Generate connection-focused narrative for 2 articles (1 short paragraph)"""
        article1, article2 = articles[0], articles[1]
        
        # Brief domain context
        domain_context = self._get_connection_domain_context(section_name)
        
        # Present first article
        title1 = article1.get('title', 'Untitled')
        link1 = article1.get('link', '#')
        source1 = self._abbreviate_source(article1.get('source', 'Unknown'))
        type1 = f" [{article1.get('article_type', '').capitalize()}]" if self._should_show_article_type(article1.get('article_type', '')) else ""
        context1 = self._extract_brief_technical_context(article1.get('description', ''))
        context1_phrase = f", {context1}" if context1 else ""
        
        # Present second article with connection
        title2 = article2.get('title', 'Untitled')
        link2 = article2.get('link', '#')
        source2 = self._abbreviate_source(article2.get('source', 'Unknown'))
        type2 = f" [{article2.get('article_type', '').capitalize()}]" if self._should_show_article_type(article2.get('article_type', '')) else ""
        context2 = self._extract_brief_technical_context(article2.get('description', ''))
        context2_phrase = f", {context2}" if context2 else ""
        
        # Simple connection between articles
        connection = self._find_simple_connection(article1, article2)
        
        # Brief synthesis of what their relationship reveals
        relationship_insight = self._synthesize_two_article_relationship(section_name, articles)
        
        return f"{domain_context} {source1} examines [{title1}]({link1}){type1}{context1_phrase}. {connection} {source2} reports on [{title2}]({link2}){type2}{context2_phrase}. {relationship_insight}"
    
    def _generate_full_narrative(self, section_name: str, articles: List[Dict]) -> str:
        """Generate simplified narrative for 3+ articles (1-2 paragraphs, clearer language)"""
        # 1. Opening - Brief context (1-2 sentences)
        opening_context = self._generate_simple_opening(section_name, articles)
        
        # 2. Body - Simple narrative linking articles with clear explanations
        narrative_body = self._weave_articles_simply(section_name, articles)
        
        # 3. Closing - Brief implications (1-2 sentences) 
        synthesis_closing = self._simple_synthesis(section_name, articles)
        
        # Combine all parts into flowing narrative (shorter than v3)
        return f"{opening_context} {narrative_body} {synthesis_closing}"
    
    def _generate_simple_opening(self, section_name: str, articles: List[Dict]) -> str:
        """Generate simple 1-2 sentence opening with clear language"""
        themes = self._extract_common_themes(articles)
        
        simple_openings = {
            'moonshot_frontiers': f"Major breakthroughs in {themes.get('domain_focus', 'technology')} are showing new approaches to difficult challenges. These developments demonstrate how collaboration and systematic thinking can solve problems once thought impossible.",
            
            'ai_future_computing': f"New developments in AI are changing how we think about machine learning and computing. Recent advances suggest that {themes.get('key_insight', 'current approaches')} may need significant changes to remain effective.",
            
            'academic_research': f"Recent academic research is revealing new insights about {themes.get('core_concept', 'innovation and strategy')}. These studies are challenging traditional assumptions and offering fresh perspectives.",
            
            'space_frontier_science': f"Space exploration is advancing through new technologies and methods. Recent missions are providing data that {themes.get('space_concept', 'changes our understanding')} of the universe.",
            
            'strategic_thinking': f"Business strategy is evolving to handle today's complex challenges. New frameworks are emerging that go beyond traditional approaches to {themes.get('strategic_domain', 'competitive dynamics')}.",
            
            'from_reddit': f"Interesting discussions and discoveries from Reddit communities are highlighting {themes.get('topic_area', 'unexpected insights')}. These conversations reveal perspectives often missed by mainstream sources.",
            
            'cool_news': f"This week's developments reveal unexpected connections between different fields. These stories show how innovation often comes from unexpected places."
        }
        
        return simple_openings.get(section_name, f"This week's developments in {section_name} show interesting new trends. These changes may have broader implications going forward.")
    
    def _weave_articles_simply(self, section_name: str, articles: List[Dict]) -> str:
        """Simple article weaving with clear explanations"""
        if len(articles) <= 1:
            return self._format_single_article_narrative(articles[0] if articles else {})
        
        # Take up to 5 articles and present them simply
        selected_articles = articles[:5]
        parts = []
        
        for i, article in enumerate(selected_articles):
            title = article.get('title', 'Untitled')
            link = article.get('link', '#')
            source = self._abbreviate_source(article.get('source', 'Unknown'))
            
            if i == 0:
                parts.append(f"{source} examines [{title}]({link})")
            elif i == 1:
                parts.append(f"Meanwhile, {source} reports on [{title}]({link})")
            elif i == 2:
                parts.append(f"From a complementary angle, {source} explores [{title}]({link})")
            else:
                parts.append(f"{source}'s [{title}]({link})")
        
        # Join with simple connecting phrases
        if len(parts) <= 2:
            return ". ".join(parts) + "."
        else:
            # Break into two sentences for readability
            first_part = ". ".join(parts[:2]) + "."
            additional = "Additional research provides complementary insights: " + " and ".join(parts[2:]) + "."
            return f"{first_part} {additional}"
    
    def _simple_synthesis(self, section_name: str, articles: List[Dict]) -> str:
        """Simple 1-2 sentence synthesis"""
        simple_closings = {
            'moonshot_frontiers': "These developments show how systematic approaches can tackle major challenges.",
            'ai_future_computing': "These advances suggest AI development may need new approaches to remain effective.",
            'academic_research': "This research provides new tools for understanding complex problems.",
            'space_frontier_science': "These discoveries expand our understanding of space and improve future missions.",
            'strategic_thinking': "These frameworks offer practical guidance for navigating today's business challenges.", 
            'from_reddit': "These discussions highlight valuable insights often overlooked by traditional media.",
            'cool_news': "These stories demonstrate how innovation emerges from unexpected connections."
        }
        
        return simple_closings.get(section_name, "These developments suggest important changes ahead.")
    
    def _generate_thematic_opening(self, section_name: str, articles: List[Dict]) -> str:
        """Generate 2-3 sentence thematic opening that sets broader context"""
        # Analyze common themes in the articles
        themes = self._extract_common_themes(articles)
        
        openings = {
            'moonshot_frontiers': f"Several breakthrough initiatives this week demonstrate systematic approaches to previously intractable problems, building on the risk management frameworks that emerged from the 2020-2023 deep tech investment cycle. The methodologies emerging from {themes.get('domain_focus', 'deep tech ventures')} suggest a maturation in how organizations structure high-uncertainty, high-reward ventures, moving beyond the traditional 'fail fast' paradigm toward what venture analysts now term 'structured uncertainty navigation.' These projects share technical rigor in their approach to scaling challenges, moving beyond proof-of-concept toward industrial viability through integrated approaches that combine advanced manufacturing capabilities, computational modeling, and risk capital allocation. This convergence represents a fundamental shift from the Silicon Valley software model to what researchers call 'hardtech industrialization'—ventures that would have been prohibitively complex just five years ago but are now enabled by advances in simulation, materials science, and distributed manufacturing systems.",
            
            'ai_future_computing': f"Recent advances in machine learning architectures are revealing emergent properties that weren't anticipated in the theoretical frameworks established during the transformer revolution of 2017-2022. The research indicates that {themes.get('key_insight', 'scaling laws')} may not follow the power-law relationships that have guided recent development strategies, challenging the assumptions underlying the 'scaling hypothesis' that dominated industry thinking since GPT-3. These findings have profound implications for compute allocation, model architecture design, and the fundamental question of whether current transformer-based approaches will continue to yield performance gains at economically viable scales. The technical literature suggests we may be approaching what complexity theorists call 'architectural phase transitions'—inflection points that will require new mathematical foundations and possibly entirely different computational paradigms. This shift echoes the transition from symbolic AI to connectionist approaches in the 1980s, but with far greater economic and infrastructural stakes involved.",
            
            'research_discoveries': f"Cross-disciplinary research is uncovering mechanisms that challenge established paradigms in {themes.get('field_count', 'multiple domains')}, extending the methodological pluralism that gained momentum following the replication crisis of the 2010s. The innovations in these studies represent advances in experimental design and analytical techniques that enable previously impossible investigations, particularly in areas where traditional disciplinary boundaries have proven limiting. What's particularly noteworthy is how computational approaches are being integrated with traditional empirical methods to reveal patterns in {themes.get('core_concept', 'complex adaptive systems')}—a convergence that reflects the growing influence of complexity science on mainstream research methodologies. These findings suggest that phenomena previously attributed to separate causal mechanisms may actually reflect unified underlying processes, supporting the theoretical frameworks developed by systems thinkers like Herbert Simon and Stuart Kauffman, but now with empirical validation through big data approaches and machine learning techniques.",
            
            'space_frontier_science': f"Space science is experiencing a methodological transformation driven by new observational capabilities and computational approaches, building on the data-rich environment created by the 2020s satellite constellation boom and the James Webb Space Telescope's operational capacity. The data from recent missions is revealing {themes.get('space_concept', 'planetary formation mechanisms')} that weren't detectable with previous instrumentation, challenging models established during the Hubble era and requiring integration with theoretical frameworks developed since the exoplanet discoveries of the 1990s. What's significant is how advances in signal processing and machine learning—particularly techniques borrowed from terrestrial pattern recognition—are enabling extraction of scientific insights from previously noise-limited observations. These technological capabilities are fundamentally expanding the parameter space of observable phenomena, leading to discoveries that require updates to existing theoretical models and creating what astronomers call 'computational astronomy'—a field that would have been unrecognizable to researchers working even a decade ago.",
            
            'strategic_thinking': f"Strategic analysis frameworks are being stress-tested by the complexity of modern interconnected systems, pushing beyond the Porter Five Forces model that dominated business school curricula since the 1980s toward what complexity economists call 'adaptive strategy.' Traditional approaches to {themes.get('strategic_domain', 'competitive dynamics')} were developed for more linear, predictable environments and are proving inadequate for conditions where network effects, platform dynamics, and algorithmic mediation create unprecedented feedback loops. The most insightful analyses are developing new models that account for these emergent properties—drawing from game theory, complex systems research, and behavioral economics—that weren't central to earlier strategic thinking rooted in industrial-era competitive dynamics. These frameworks suggest that competitive advantage increasingly depends on understanding system-level dynamics rather than individual firm capabilities, echoing the shift from resource-based view to dynamic capabilities theory, but now applied to digitally-mediated ecosystems where traditional industry boundaries have become largely meaningless.",
            
            'hidden_gems': f"Significant developments often emerge from specialized communities or niche applications before gaining broader recognition, following the innovation diffusion patterns that Everett Rogers identified in the 1960s but now accelerated by digital communication networks and open-source collaboration tools. This week's selection highlights innovations in {themes.get('assumption_area', 'emerging fields')} that address fundamental technical or social challenges, representing what innovation theorists call 'weak signals'—early indicators of potentially transformative trends. These stories matter because they represent early indicators of trends that may become mainstream within 2-3 years, similar to how concepts like DevOps, microservices, and user experience design migrated from niche technical communities to standard business practice. The pattern suggests that innovation continues to emerge from the periphery, where practitioners have different constraints and incentives than established players in mature markets, operating in what Clayton Christensen termed 'asymmetric competitive environments' where incumbents' traditional advantages become irrelevant."
        }
        
        return openings.get(section_name, f"This week's developments in {section_name} reveal unexpected connections between seemingly disparate fields. The emerging patterns suggest fundamental shifts in how we approach these challenges. These stories matter because they illuminate possibilities that conventional thinking overlooks.")
    
    def _weave_articles_into_story(self, section_name: str, articles: List[Dict]) -> str:
        """Weave articles into structured narrative with information-dense paragraphs followed by synthesis"""
        if len(articles) <= 1:
            return self._format_single_article_narrative(articles[0] if articles else {})
        
        narrative_parts = []
        
        # First paragraph: Information-dense with frequent links (articles 1-3)
        primary_articles = articles[:3]
        narrative_parts.append(self._create_information_dense_paragraph(primary_articles))
        
        # Second paragraph: Additional perspectives (articles 4-5 if they exist)
        if len(articles) > 3:
            remaining_articles = articles[3:5]  # Limit to 5 total articles
            narrative_parts.append("\n\n")
            narrative_parts.append(self._create_supporting_paragraph(remaining_articles))
        
        return ''.join(narrative_parts)
    
    def _create_information_dense_paragraph(self, articles: List[Dict]) -> str:
        """Create information-dense paragraph with frequent embedded links"""
        if not articles:
            return ""
        
        parts = []
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')
            link = article.get('link', '#')
            source = article.get('source', 'Unknown')
            article_type = article.get('article_type', 'Article')
            description = article.get('description', '')
            
            abbreviated_source = self._abbreviate_source(source)
            type_tag = ""
            if self._should_show_article_type(article_type):
                type_tag = f" [{article_type.capitalize()}]"
            
            if i == 0:
                # Start with primary article and immediate context
                parts.append(f"{abbreviated_source} examines [{title}]({link}){type_tag}")
                context = self._extract_brief_technical_context(description)
                if context:
                    parts.append(f", {context}")
                
            elif i == 1:
                # Add connection and second article within same paragraph
                connection = self._find_explicit_connection(articles[0], article)
                parts.append(f" {connection} {abbreviated_source} reports on [{title}]({link}){type_tag}")
                
                # Add brief context to maintain information density
                brief_context = self._extract_brief_insight(description)
                if brief_context:
                    parts.append(f", {brief_context}")
                    
            elif i == 2:
                # Third article with contrasting or supporting view
                relationship = self._analyze_relationship_to_previous(articles[:2], article)
                parts.append(f" {relationship} {abbreviated_source} explores [{title}]({link}){type_tag}")
                
                # Brief insight to close the paragraph
                insight = self._extract_brief_insight(description)
                if insight:
                    parts.append(f", {insight}")
        
        return ''.join(parts) + "."
    
    def _create_supporting_paragraph(self, articles: List[Dict]) -> str:
        """Create supporting paragraph with additional articles"""
        if not articles:
            return ""
        
        parts = ["Additional research provides complementary insights: "]
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')
            link = article.get('link', '#')
            source = article.get('source', 'Unknown')
            article_type = article.get('article_type', 'Article')
            
            abbreviated_source = self._abbreviate_source(source)
            type_tag = ""
            if self._should_show_article_type(article_type):
                type_tag = f" [{article_type.capitalize()}]"
            
            if i == 0:
                parts.append(f"{abbreviated_source}'s [{title}]({link}){type_tag}")
            else:
                parts.append(f" and {abbreviated_source}'s [{title}]({link}){type_tag}")
        
        parts.append(".")
        return ''.join(parts)
    
    def _find_explicit_connection(self, prev_article: Dict, current_article: Dict) -> str:
        """Find and articulate sophisticated connections between articles with dialogue focus"""
        prev_title = prev_article.get('title', '').lower()
        current_title = current_article.get('title', '').lower()
        prev_desc = prev_article.get('description', '').lower()
        current_desc = current_article.get('description', '').lower()
        prev_source = prev_article.get('source', '').lower()
        current_source = current_article.get('source', '').lower()
        
        # Look for shared concepts with enhanced sophistication
        shared_concepts = self._identify_shared_concepts(prev_title + prev_desc, current_title + current_desc)
        
        if shared_concepts:
            return f"Complementing this analysis, research examining the same {shared_concepts[0]} mechanisms"
        
        # Cross-institutional dialogue patterns
        if 'nature' in prev_source and any(word in current_source for word in ['mckinsey', 'harvard', 'mit']):
            return "Translating these scientific findings into strategic frameworks,"
        elif any(word in prev_source for word in ['mckinsey', 'bcg', 'bain']) and 'nature' in current_source:
            return "Providing empirical validation for these strategic insights,"
        elif 'harvard' in prev_source and 'mit' in current_source:
            return "Extending this Harvard framework through MIT's technical lens,"
        
        # Look for contrasting methodological approaches
        if any(word in current_title for word in ['different', 'alternative', 'opposite', 'versus']):
            return "However, challenging this conventional approach,"
        elif any(word in current_desc for word in ['contradicts', 'disputes', 'questions']):
            return "Presenting a competing perspective,"
            
        # Look for building/extending relationships
        if any(word in current_title for word in ['extends', 'builds', 'advances']):
            return "Extending these theoretical foundations,"
        elif any(word in current_title for word in ['validates', 'confirms', 'supports']):
            return "Providing empirical support for these findings,"
        
        # Look for temporal/evolutionary relationships
        if any(word in current_title for word in ['next', 'future', 'following', 'after']):
            return "Anticipating the next phase of these developments,"
        elif any(word in current_title for word in ['evolution', 'progression', 'development']):
            return "Tracing the evolutionary trajectory of these concepts,"
        
        # Enhanced source-based connections
        prev_type = prev_article.get('article_type', 'article')
        current_type = current_article.get('article_type', 'article')
        
        if prev_type == 'research' and current_type == 'analysis':
            return "Bridging academic insights with practical implementation,"
        elif prev_type == 'analysis' and current_type == 'research':
            return "Grounding strategic analysis in empirical research,"
        elif prev_type == 'news' and current_type == 'opinion':
            return "Contextualizing these developments within broader strategic implications,"
        elif prev_type == 'opinion' and current_type == 'research':
            return "Testing these theoretical propositions against empirical evidence,"
        else:
            return "Examining these interconnected developments from a complementary angle,"
    
    def _analyze_relationship_to_previous(self, prev_articles: List[Dict], current_article: Dict) -> str:
        """Analyze how current article relates to the emerging narrative"""
        current_title = current_article.get('title', '').lower()
        current_desc = current_article.get('description', '').lower()
        
        # Check if it supports the trend
        if any(word in current_title for word in ['confirms', 'supports', 'validates', 'proves']):
            return "Confirming this emerging pattern,"
        
        # Check if it challenges or contradicts
        if any(word in current_title for word in ['challenges', 'contradicts', 'questions', 'disputes']):
            return "However, challenging this conventional wisdom,"
        
        # Check if it expands scope
        if any(word in current_title for word in ['global', 'worldwide', 'international', 'broader']):
            return "Expanding the scope of these findings,"
        
        # Look for methodology differences
        prev_sources = [a.get('source', '').lower() for a in prev_articles]
        current_source = current_article.get('source', '').lower()
        
        if 'academic' in current_source or 'university' in current_source:
            return "From an academic perspective,"
        elif 'industry' in current_source or 'company' in current_source:
            return "From an industry viewpoint,"
        
        return "From a complementary angle,"
    
    def _extract_contextual_insight(self, description: str, is_primary: bool = False, 
                                  is_connecting: bool = False, is_supporting: bool = False) -> str:
        """Extract contextual insight based on narrative role"""
        if not description:
            return ""
        
        # Clean and parse description
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        if not sentences:
            return ""
        
        if is_primary:
            # Primary article gets detailed technical context
            key_points = self._extract_key_points(sentences)
            technical_details = self._extract_technical_context(sentences)
            
            if key_points and technical_details:
                return f"which demonstrates {key_points[0].lower()}. The methodology employed {technical_details.lower()}, with implications for {self._extract_implications(sentences)}"
            elif key_points:
                return f"demonstrating {key_points[0].lower()}. The analysis reveals methodological advances that could influence {self._extract_domain_applications(sentences)}"
            else:
                return f"addressing fundamental questions about {self._extract_core_problem(sentences)}. The approach represents a significant advancement in analytical techniques"
        
        elif is_connecting:
            # Connecting article shows deeper relationship with technical context
            if len(sentences) >= 2:
                technical_link = self._find_technical_connection(sentences)
                return f". This work {technical_link.lower()}, suggesting {sentences[1].lower()[:80]}{'...' if len(sentences[1]) > 80 else ''}. The convergence of these approaches indicates {self._extract_convergence_insight(sentences)}"
            else:
                return f", providing complementary evidence through {self._extract_methodology_type(sentences)}. The findings align with emerging patterns in {self._extract_field_context(sentences)}"
        
        elif is_supporting:
            # Supporting article provides substantial additional evidence
            evidence = self._find_supporting_evidence(sentences)
            methodology = self._extract_methodology_type(sentences)
            if evidence and methodology:
                return f". The {methodology.lower()} approach validates {evidence.lower()[:90]}{'...' if len(evidence) > 90 else ''}, reinforcing the broader theoretical framework"
            elif evidence:
                return f", corroborating {evidence.lower()[:100]}{'...' if len(evidence) > 100 else ''}. These results strengthen the empirical foundation for {self._extract_theoretical_implications(sentences)}"
        
        return ""
    
    def _synthesize_implications(self, section_name: str, articles: List[Dict]) -> str:
        """Generate synthesis of what these stories mean together"""
        # Analyze the collective themes
        all_themes = []
        for article in articles:
            themes = self._extract_article_themes(article)
            all_themes.extend(themes)
        
        # Find the most significant shared theme
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        dominant_theme = max(theme_counts.keys(), key=theme_counts.get) if theme_counts else "innovation"
        
        syntheses = {
            'moonshot_frontiers': f"The convergence of these initiatives reveals a fundamental shift in how deep tech ventures approach the valley of death between research and commercialization. Rather than relying purely on vision and traditional venture capital playbooks, these projects demonstrate mature processes for navigating uncertainty that draw from complexity science, systems engineering, and adaptive management theory. What's particularly notable is how insights from MIT's technological innovation systems research are being operationalized by firms backed by a16z and other sophisticated investors, creating what venture analysts are calling the 'third wave of deep tech'—after the materials revolution of the 2000s and the biotech surge of the 2010s. The methodologies being developed here represent a synthesis of academic research on innovation systems with practical experience from failed moonshots of the previous decade, suggesting that the high failure rates that characterized earlier deep tech cycles may finally be addressable through more systematic approaches.",
            
            'ai_future_computing': f"The technical implications of these developments extend beyond immediate applications to fundamental questions about the sustainability of current AI development paradigms, connecting insights from computational complexity theory with practical infrastructure constraints in ways that echo the semiconductor industry's approach to Moore's Law limitations. The research suggests that current approaches to {dominant_theme} may require significant modifications as we encounter what researchers are calling 'the efficiency wall'—similar to the power wall that drove multicore architecture adoption in the 2000s. Notably, the convergence between academic research (particularly from institutions like Stanford and MIT) and industry practice (reflected in Meta's and Google's recent architectural explorations) suggests that the field is approaching what Thomas Kuhn would recognize as a paradigm crisis. Organizations planning AI infrastructure investments should consider how these findings might affect their technology roadmaps over the next 2-3 years, particularly as the cost structure of current approaches becomes increasingly prohibitive for all but the most well-resourced organizations.",
            
            'research_discoveries': f"What's significant about these studies is their methodological contributions to understanding {dominant_theme} in complex systems, representing a convergence of insights from multiple research traditions that have historically operated in isolation. The analytical techniques being developed here provide new tools for investigating phenomena that were previously difficult to study empirically, drawing from advances in computational social science, machine learning, and traditional econometric approaches in ways that would have been impossible before the big data revolution of the 2010s. Particularly notable is how research from management schools like Harvard Business School and Wharton is increasingly incorporating methods from physics and biology to study organizational phenomena, while traditionally quantitative fields are adopting ethnographic and qualitative approaches. These cross-disciplinary methods may prove more broadly applicable to other domains facing similar measurement and causal inference challenges, suggesting that the methodological pluralism that emerged from the replication crisis is finally producing practical dividends in the form of more robust and generalizable findings.",
            
            'space_frontier_science': f"These findings represent advances in both observational capabilities and data analysis methods that expand what's scientifically accessible in space research, but more importantly, they demonstrate how terrestrial AI breakthroughs are being rapidly adapted for astronomical applications in ways that would have seemed like science fiction during the Hubble era. The integration of machine learning techniques—particularly those developed for medical imaging and autonomous systems—with traditional astronomical methods is enabling detection of signals and patterns that would have been impossible to identify just a few years ago. What's particularly striking is how NASA's methodological innovations are being adopted by ESA and other space agencies, creating what amounts to a global convergence in computational astronomy approaches. This methodological progress has implications for mission planning and instrument design across multiple space agencies, but also suggests that the traditional boundaries between Earth-based and space-based scientific methods are dissolving, potentially accelerating discovery rates across multiple domains.",
            
            'strategic_thinking': f"The frameworks emerging from this analysis work provide more sophisticated tools for understanding competitive dynamics in networked environments, synthesizing insights from game theory, complexity economics, and behavioral psychology in ways that transcend the limitations of traditional Porter-style competitive analysis. Traditional strategic models assumed relatively static industry structures and rational actors, while these approaches account for the feedback effects, algorithmic mediation, and emergent properties that characterize platform-driven competition. What's particularly notable is how business schools (Harvard, Stanford, INSEAD) are incorporating insights from complexity science that were developed in physics and biology departments, creating truly interdisciplinary approaches to strategic analysis. The practical applications extend to investment strategy, organizational design, and policy development in complex systems, but also suggest that the distinction between 'strategy' and 'systems design' is becoming increasingly meaningless in digitally-mediated environments where traditional industry boundaries have collapsed.",
            
            'hidden_gems': f"These developments highlight the continued importance of monitoring innovation at the edges of established fields, but more importantly, they demonstrate how digital communication networks are accelerating the diffusion of innovations in ways that compress Rogers' traditional adoption timelines from decades to years or even months. The stories selected here represent what complexity theorists call 'weak signals'—early indicators of potentially transformative trends that emerge from asymmetric competitive environments where traditional performance metrics don't apply. What's particularly interesting is how innovations that emerge in specialized technical communities (like the open-source software community that developed container technologies) are being rapidly adopted by mainstream organizations, creating what innovation researchers term 'punctuated diffusion'—rapid adoption phases that follow long periods of niche development. For practitioners in related areas, these cases provide insight into how innovation emerges and scales in specialized communities before gaining broader adoption, suggesting that monitoring peripheral communities may be more valuable than tracking mainstream competitive intelligence in environments characterized by exponential technological change."
        }
        
        return syntheses.get(section_name, f"These developments collectively suggest that {dominant_theme} will be a defining force in shaping the future. The patterns emerging point toward fundamental shifts that extend far beyond any single domain, promising to reshape how we understand and interact with the world.")
    
    def _extract_common_themes(self, articles: List[Dict]) -> Dict[str, str]:
        """Extract common themes from article set"""
        themes = {}
        all_text = ' '.join([
            f"{article.get('title', '')} {article.get('description', '')}"
            for article in articles
        ]).lower()
        
        # Domain analysis
        if any(word in all_text for word in ['space', 'cosmic', 'galaxy', 'orbit']):
            themes['domain_focus'] = 'space exploration'
        elif any(word in all_text for word in ['ai', 'machine', 'algorithm', 'neural']):
            themes['domain_focus'] = 'artificial intelligence'
        elif any(word in all_text for word in ['research', 'study', 'analysis', 'discovery']):
            themes['domain_focus'] = 'scientific research'
        
        # Key insights
        if 'breakthrough' in all_text:
            themes['key_insight'] = 'breakthrough technologies'
        elif 'challenge' in all_text:
            themes['key_insight'] = 'challenging assumptions'
        
        return themes
    
    def _abbreviate_source(self, source: str) -> str:
        """Convert source names to abbreviations where appropriate"""
        # Direct lookup first
        if source in self.source_abbreviations:
            return self.source_abbreviations[source]
        
        # Pattern matching for common cases
        source_lower = source.lower()
        
        # NYTimes patterns
        if 'nytimes' in source_lower or 'new york times' in source_lower:
            if 'business' in source_lower:
                return 'NYTimes'
            elif 'science' in source_lower:
                return 'NYTimes'
            elif 'education' in source_lower:
                return 'NYTimes'
            elif 'space' in source_lower:
                return 'NYTimes'
            else:
                return 'NYTimes'
        
        # Academic patterns
        if 'journal' in source_lower and len(source) > 25:
            # Try to create meaningful abbreviations for long journal names
            words = source.split()
            if len(words) >= 3:
                return ''.join(word[0].upper() for word in words if len(word) > 2)
        
        # Business/tech publications
        common_patterns = {
            'techcrunch': 'TechCrunch',
            'ars technica': 'Ars Technica',
            'the verge': 'The Verge',
            'wired': 'Wired',
            'bloomberg': 'Bloomberg',
            'fortune': 'Fortune',
            'cnbc': 'CNBC',
            'reuters': 'Reuters',
            'associated press': 'AP',
            'the guardian': 'Guardian',
            'the atlantic': 'The Atlantic',
            'harvard gazette': 'Harvard',
            'mit news': 'MIT',
            'stanford': 'Stanford',
            'carnegie mellon': 'CMU'
        }
        
        for pattern, abbrev in common_patterns.items():
            if pattern in source_lower:
                return abbrev
        
        # If no abbreviation found, return original
        return source
    
    def _should_show_article_type(self, article_type: str) -> bool:
        """Determine if article type should be shown (only for research/analysis)"""
        important_types = {'research', 'analysis', 'opinion', 'essay', 'review'}
        return article_type.lower() in important_types
    
    def _format_single_article_narrative(self, article: Dict) -> str:
        """Format narrative for a single article"""
        if not article:
            return ""
        
        title = article.get('title', 'Untitled')
        link = article.get('link', '#')
        source = article.get('source', 'Unknown')
        article_type = article.get('article_type', 'Article')
        read_time = article.get('read_time', 5)
        description = article.get('description', '')
        
        type_tag = f"[{article_type.capitalize()}, ~{read_time} min]"
        
        # Create simple narrative for single article
        context = self._extract_contextual_insight(description, is_primary=True)
        return f"{source} examines [{title}]({link}) {type_tag} {context}"
    
    def _identify_shared_concepts(self, text1: str, text2: str) -> List[str]:
        """Identify shared concepts between two texts"""
        # Simple keyword matching for shared concepts
        concepts = []
        
        # Look for technical terms
        tech_terms = ['ai', 'machine learning', 'neural', 'algorithm', 'data', 'research', 
                     'study', 'analysis', 'space', 'cosmic', 'discovery', 'breakthrough']
        
        for term in tech_terms:
            if term in text1 and term in text2:
                concepts.append(term)
        
        return concepts[:3]  # Return top 3 matches
    
    def _extract_key_points(self, sentences: List[str]) -> List[str]:
        """Extract key points from sentences"""
        key_points = []
        for sentence in sentences[:3]:  # Look at first 3 sentences
            if any(word in sentence.lower() for word in ['discover', 'reveal', 'show', 'find', 'demonstrate']):
                # Extract the main point after the discovery verb
                parts = sentence.split()
                for i, part in enumerate(parts):
                    if part.lower() in ['discover', 'reveals', 'shows', 'finds', 'demonstrates']:
                        remaining = ' '.join(parts[i+1:])
                        if len(remaining) > 10:
                            key_points.append(remaining)
                        break
        
        return key_points[:2]
    
    def _find_supporting_evidence(self, sentences: List[str]) -> str:
        """Find supporting evidence in sentences"""
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['evidence', 'data', 'results', 'findings']):
                if len(sentence) < 120:
                    return sentence
                else:
                    return sentence[:117] + "..."
        
        # Fallback to first substantial sentence
        for sentence in sentences:
            if len(sentence) > 30:
                return sentence[:100] + ("..." if len(sentence) > 100 else "")
        
        return ""
    
    def _extract_article_themes(self, article: Dict) -> List[str]:
        """Extract themes from individual article"""
        themes = []
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        combined = f"{title} {description}"
        
        # Technical themes
        if any(word in combined for word in ['ai', 'artificial intelligence', 'machine learning']):
            themes.append('artificial intelligence')
        if any(word in combined for word in ['space', 'cosmic', 'galaxy', 'universe']):
            themes.append('space exploration')
        if any(word in combined for word in ['research', 'study', 'academic']):
            themes.append('research')
        if any(word in combined for word in ['innovation', 'breakthrough', 'novel']):
            themes.append('innovation')
        if any(word in combined for word in ['strategy', 'strategic', 'framework']):
            themes.append('strategic thinking')
        
        return themes
    
    def _get_minimal_domain_context(self, section_name: str) -> str:
        """Get brief domain context for single article narrative"""
        contexts = {
            'moonshot_frontiers': "Deep tech ventures continue pursuing ambitious technical challenges.",
            'ai_future_computing': "Machine learning research reveals new architectural insights.",
            'research_discoveries': "Recent academic research challenges established assumptions.",
            'space_frontier_science': "Space science capabilities continue expanding observational reach.",
            'strategic_thinking': "Strategic frameworks evolve to address modern competitive dynamics.",
            'hidden_gems': "Innovation emerges from specialized communities and niche applications."
        }
        return contexts.get(section_name, "Recent developments highlight emerging trends.")
    
    def _get_connection_domain_context(self, section_name: str) -> str:
        """Get brief domain context for two-article narrative"""
        contexts = {
            'moonshot_frontiers': "Two recent developments illustrate evolving approaches to deep tech ventures.",
            'ai_future_computing': "Parallel advances in machine learning are revealing related insights.",
            'research_discoveries': "Complementary academic studies are uncovering connected mechanisms.",
            'space_frontier_science': "Recent space science findings demonstrate converging methodologies.",
            'strategic_thinking': "Strategic analysis frameworks are being refined through related approaches.", 
            'hidden_gems': "Emerging innovations from different domains share common characteristics."
        }
        return contexts.get(section_name, "Related developments reveal connected insights.")
    
    def _extract_single_implication(self, section_name: str, description: str) -> str:
        """Extract single practical implication for minimal narrative"""
        if not description:
            return "This development has practical implications for the field."
        
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        
        # Look for implication indicators
        implication_words = ['implications', 'suggests', 'indicates', 'means', 'enables', 'allows']
        
        for sentence in sentences[:3]:
            for word in implication_words:
                if word in sentence.lower():
                    if len(sentence) < 120:
                        return sentence.strip() + "."
                    else:
                        return sentence[:117].strip() + "..."
        
        # Fallback based on section type
        fallbacks = {
            'moonshot_frontiers': "This approach could influence future deep tech venture strategies.",
            'ai_future_computing': "These findings may affect AI development approaches.",
            'research_discoveries': "This research provides new tools for empirical investigation.",
            'space_frontier_science': "This capability expands what's scientifically accessible.",
            'strategic_thinking': "This framework offers new strategic analysis tools.",
            'hidden_gems': "This innovation may gain broader adoption over time."
        }
        
        return fallbacks.get(section_name, "This development warrants continued attention.")
    
    def _find_simple_connection(self, article1: Dict, article2: Dict) -> str:
        """Find simple connection between two articles (no sophisticated analysis)"""
        title1 = article1.get('title', '').lower()
        title2 = article2.get('title', '').lower()
        
        # Simple connection phrases for two articles
        if any(word in title2 for word in ['similar', 'related', 'parallel']):
            return "Similarly,"
        elif any(word in title2 for word in ['different', 'alternative', 'contrast']):
            return "In contrast,"
        elif any(word in title2 for word in ['building', 'extending', 'expanding']):
            return "Building on this,"
        else:
            return "Meanwhile,"
    
    def _synthesize_two_article_relationship(self, section_name: str, articles: List[Dict]) -> str:
        """Brief synthesis of what relationship between two articles reveals"""
        synthesis_templates = {
            'moonshot_frontiers': "Together, these approaches suggest maturing methodologies in deep tech development.",
            'ai_future_computing': "These parallel developments indicate broader shifts in AI architectural thinking.",
            'research_discoveries': "The convergence of these findings points to evolving research methodologies.",
            'space_frontier_science': "These complementary capabilities demonstrate expanding scientific reach.", 
            'strategic_thinking': "These frameworks reflect the increasing complexity of modern strategic challenges.",
            'hidden_gems': "Both developments exemplify innovation emerging from specialized contexts."
        }
        
        return synthesis_templates.get(section_name, "These related developments suggest broader trends in the field.")
    
    def _extract_brief_technical_context(self, description: str) -> str:
        """Extract brief technical context for information-dense paragraphs"""
        if not description:
            return ""
        
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        if not sentences:
            return ""
        
        # Look for key technical terms in first 2 sentences
        for sentence in sentences[:2]:
            if any(word in sentence.lower() for word in ['method', 'approach', 'demonstrates', 'reveals', 'shows']):
                # Extract key insight, keep brief (under 80 chars)
                if len(sentence) < 80:
                    return sentence.strip()
                else:
                    return sentence[:77].strip() + "..."
        
        # Fallback to first sentence if no technical terms
        if sentences and len(sentences[0]) < 100:
            return sentences[0].strip()
        
        return ""
    
    def _extract_brief_insight(self, description: str) -> str:
        """Extract brief insight for maintaining information density"""
        if not description:
            return ""
        
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        if not sentences:
            return ""
        
        # Look for findings, implications, or key results
        insight_indicators = ['finding', 'result', 'suggest', 'indicate', 'reveal', 'show', 'demonstrate']
        
        for sentence in sentences[:3]:
            for indicator in insight_indicators:
                if indicator in sentence.lower():
                    if len(sentence) < 90:
                        return sentence.strip()
                    else:
                        return sentence[:87].strip() + "..."
        
        # Fallback to a brief version of the first substantial sentence
        for sentence in sentences[:2]:
            if len(sentence) > 30 and len(sentence) < 100:
                return sentence.strip()
        
        return ""
    
    def _extract_technical_context(self, sentences: List[str]) -> str:
        """Extract technical methodology or context from sentences"""
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['method', 'approach', 'technique', 'analysis', 'model', 'framework']):
                # Extract key technical terms
                if len(sentence) < 100:
                    return sentence.strip()
                else:
                    return sentence[:97].strip() + "..."
        return "novel analytical methods"
    
    def _extract_implications(self, sentences: List[str]) -> str:
        """Extract implications or applications from sentences"""
        implications = ['applications', 'implications', 'impact', 'effects', 'consequences']
        for sentence in sentences:
            if any(word in sentence.lower() for word in implications):
                # Extract the implication part
                words = sentence.split()
                for i, word in enumerate(words):
                    if word.lower() in implications and i < len(words) - 3:
                        return ' '.join(words[i+1:i+8]).lower()
        return "future research directions"
    
    def _extract_domain_applications(self, sentences: List[str]) -> str:
        """Extract domain-specific applications"""
        domains = ['industry', 'research', 'policy', 'practice', 'development', 'innovation']
        for sentence in sentences:
            for domain in domains:
                if domain in sentence.lower():
                    return f"{domain} applications"
        return "practical applications"
    
    def _extract_core_problem(self, sentences: List[str]) -> str:
        """Extract the core problem being addressed"""
        problem_indicators = ['problem', 'challenge', 'question', 'issue', 'difficulty']
        for sentence in sentences[:2]:
            for indicator in problem_indicators:
                if indicator in sentence.lower():
                    # Extract context around the problem
                    words = sentence.lower().split()
                    try:
                        idx = words.index(indicator)
                        if idx < len(words) - 3:
                            return ' '.join(words[idx:idx+5])
                    except ValueError:
                        continue
        return "complex system behavior"
    
    def _find_technical_connection(self, sentences: List[str]) -> str:
        """Find technical connection between works"""
        connections = ['builds on', 'extends', 'validates', 'challenges', 'complements', 'refines']
        for sentence in sentences:
            for conn in connections:
                if conn in sentence.lower():
                    return conn
        return "complements"
    
    def _extract_convergence_insight(self, sentences: List[str]) -> str:
        """Extract insight about convergence of approaches"""
        convergence_terms = ['convergence', 'alignment', 'consistency', 'pattern', 'trend']
        for sentence in sentences:
            if any(term in sentence.lower() for term in convergence_terms):
                return "systematic alignment across methodologies"
        return "emerging consensus in the field"
    
    def _extract_methodology_type(self, sentences: List[str]) -> str:
        """Extract the type of methodology used"""
        methods = {
            'empirical': ['data', 'survey', 'experiment', 'study'],
            'computational': ['model', 'simulation', 'algorithm', 'computational'],
            'analytical': ['analysis', 'framework', 'theoretical', 'analytical'],
            'observational': ['observation', 'case study', 'longitudinal', 'ethnographic']
        }
        
        text = ' '.join(sentences).lower()
        for method_type, indicators in methods.items():
            if any(indicator in text for indicator in indicators):
                return f"{method_type} analysis"
        return "systematic analysis"
    
    def _extract_field_context(self, sentences: List[str]) -> str:
        """Extract field or domain context"""
        fields = {
            'machine learning', 'artificial intelligence', 'computer science',
            'management', 'strategy', 'organization', 'economics',
            'physics', 'biology', 'chemistry', 'materials science',
            'psychology', 'sociology', 'political science'
        }
        
        text = ' '.join(sentences).lower()
        for field in fields:
            if field in text:
                return field
        return "interdisciplinary research"
    
    def _extract_theoretical_implications(self, sentences: List[str]) -> str:
        """Extract theoretical implications"""
        theory_indicators = ['theory', 'model', 'framework', 'paradigm', 'concept']
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in theory_indicators):
                return "theoretical development"
        return "conceptual advancement"
    
    def _get_article_intro(self, article: Dict, is_first: bool = False) -> str:
        """Generate contextual introduction for an article"""
        article_type = article.get('article_type', 'article')
        source = article.get('source', 'Unknown')
        
        intros = {
            'research': f"A new study from {source} reveals",
            'analysis': f"A thoughtful analysis explores",
            'opinion': f"{source} argues",
            'news': f"{source} reports",
            'essay': f"In a reflective piece,",
            'interview': f"In conversation,"
        }
        
        return intros.get(article_type, f"{source} examines")
    
    def _get_bridge_phrase(self, prev_article: Dict, next_article: Dict) -> str:
        """Generate bridging phrase between articles"""
        bridges = [
            "Meanwhile,",
            "In parallel,",
            "Complementing this,",
            "From a different angle,",
            "Building on similar themes,",
            "Separately,",
        ]
        
        # Choose bridge based on article relationships
        if prev_article.get('article_type') == next_article.get('article_type'):
            return "Similarly,"
        else:
            import random
            return random.choice(bridges)
    
    def _extract_key_insight(self, description: str) -> str:
        """Extract and format key insight from description"""
        if not description:
            return ""
        
        # Take first sentence and clean it up
        sentences = description.split('.')
        if sentences:
            insight = sentences[0].strip()
            if len(insight) > 150:
                insight = insight[:147] + "..."
            return f"explores {insight.lower()}. "
        return ""
    
    def _extract_brief_insight(self, description: str) -> str:
        """Extract very brief insight"""
        if not description:
            return ""
        
        # Extract key phrases
        key_phrases = re.findall(r'(breakthrough|discovery|reveals|shows|demonstrates)', 
                                description.lower())
        if key_phrases:
            snippet = description.split('.')[0]
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            return f"— {snippet.lower()}"
        return ""
    
    def _get_closing_thought(self, section_name: str, articles: List[Dict]) -> str:
        """Generate closing thought for section"""
        closings = {
            'moonshot_frontiers': ", each pushing the boundaries of ambition.",
            'ai_future_computing': ", signaling AI's evolution beyond current paradigms.",
            'research_discoveries': ", advancing our understanding through rigorous inquiry.",
            'space_frontier_science': ", expanding humanity's cosmic horizons.",
            'strategic_thinking': ", offering frameworks for navigating complexity.",
            'from_reddit': ", highlighting valuable community insights.",
            'cool_news': ", proving innovation thrives in unexpected places."
        }
        
        return closings.get(section_name, ".")
    
    def filter_by_novelty(self, categorized_articles: Dict[str, List]) -> Dict[str, List]:
        """
        Filter articles by novelty score, keeping only interesting ones
        """
        filtered = {}
        
        for category, articles in categorized_articles.items():
            # Score all articles
            scored = []
            for article in articles:
                article_copy = article.copy()
                article_copy['novelty_score'] = self.score_article_novelty(article)
                scored.append(article_copy)
            
            # Sort by score and take top performers
            scored.sort(key=lambda x: x['novelty_score'], reverse=True)
            
            # Get limits from config
            category_config = None
            for priority_level in ['high_priority', 'medium_priority', 'low_priority']:
                if category in self.priorities.get('content_priorities', {}).get(priority_level, {}):
                    category_config = self.priorities['content_priorities'][priority_level][category]
                    break
            
            if category_config:
                max_articles = category_config.get('max_articles', 5)
                min_score = category_config.get('min_novelty_score', 0)
            else:
                max_articles = 5
                min_score = 0
            
            # Filter by score and limit
            filtered[category] = [
                article for article in scored[:max_articles]
                if article['novelty_score'] >= min_score
            ]
        
        return filtered