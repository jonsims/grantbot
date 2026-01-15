#!/usr/bin/env python3
"""
Quick test runner for v3 that uses existing v2 infrastructure
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Run v2 to collect articles first
from main_v2 import DailyNewsAgentV2

# Then use v3 components for enhanced processing
from generators.markdown_v3 import MarkdownGeneratorV3
from processors.narrative_enhancer import NarrativeEnhancer
from utils.email_sender import EmailSender
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_v3_test():
    """Run a quick v3 test using v2 infrastructure"""
    
    # Use v2 to collect articles
    logger.info("Using v2 to collect articles...")
    agent_v2 = DailyNewsAgentV2()
    
    # Collect content
    categorized_articles, supplementary_data = agent_v2.collect_all_content()
    
    # Use v3 components
    logger.info("Processing with v3 components...")
    narrative_enhancer = NarrativeEnhancer()
    markdown_generator = MarkdownGeneratorV3()
    
    # Filter by novelty
    filtered_articles = narrative_enhancer.filter_by_novelty(categorized_articles)
    
    # Generate v3 markdown
    summaries = {}  # Skip AI summaries for speed
    markdown_content = markdown_generator.generate_daily_update(
        summaries,
        filtered_articles,
        supplementary_data
    )
    
    # Save file
    filepath = markdown_generator.save_to_file(markdown_content)
    logger.info(f"V3 update saved to: {filepath}")
    
    # Send email
    email_sender = EmailSender()
    if email_sender.sender_email:
        subject = f"Morning Discoveries (v3 Test) - {os.path.basename(filepath)}"
        html_content = email_sender._markdown_to_html(markdown_content)
        email_sender.send_daily_update(
            markdown_content=markdown_content,
            recipient=email_sender.sender_email,
            subject=subject
        )
        logger.info(f"V3 test email sent to {email_sender.sender_email}")
    
    return filepath

if __name__ == "__main__":
    try:
        filepath = run_v3_test()
        print(f"\n✅ V3 test complete: {filepath}")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()