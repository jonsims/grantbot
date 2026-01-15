#!/usr/bin/env python3
"""
GrantBot - AI-powered grant discovery and analysis

Usage:
    python src/main.py              # Run full discovery
    python src/main.py --test       # Test mode (no email)
"""

import os
import sys
import yaml
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.grants_gov import GrantsGovCollector
from collectors.nsf import NSFCollector
from collectors.foundations import FoundationCollector
from processors.matcher import GrantMatcher, OrgProfile
from processors.analyzer import GrantAnalyzer
from generators.digest import DigestGenerator
from utils.deduplication import ArticleDeduplicator
from utils.version import VersionManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrantBot:
    """Main GrantBot application"""

    def __init__(self, config_path: str = "config/sources-grants.yaml"):
        load_dotenv()

        self.config = self._load_config(config_path)
        self.org_profile = self._load_org_profile()

        # Initialize collectors
        self.grants_gov = GrantsGovCollector()
        self.nsf = NSFCollector()
        self.foundations = FoundationCollector()

        # Initialize processors
        self.matcher = GrantMatcher(self.org_profile)
        self.analyzer = GrantAnalyzer()

        # Initialize generators
        self.digest = DigestGenerator()

        # Utils
        self.deduplicator = ArticleDeduplicator()
        self.version = VersionManager()

        logger.info(f"GrantBot initialized - {self.version.get_version_string()}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load sources configuration"""
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_path)
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _load_org_profile(self) -> OrgProfile:
        """Load organization profile"""
        profile_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config/org-profile.yaml"
        )
        try:
            with open(profile_path, 'r') as f:
                data = yaml.safe_load(f)
            return OrgProfile(
                entity_type=data['entity']['type'],
                location=data['location']['state'],
                focus_areas=data['focus_areas']['primary'] + data['focus_areas']['secondary'],
                grant_size_min=data['grant_preferences']['size_min'],
                grant_size_max=data['grant_preferences']['size_max']
            )
        except Exception as e:
            logger.error(f"Failed to load org profile: {e}")
            # Return default profile
            return OrgProfile(
                entity_type="university",
                location="Massachusetts",
                focus_areas=["entrepreneurship", "AI", "innovation"],
                grant_size_min=1000,
                grant_size_max=1000000
            )

    def collect_grants(self) -> List[Dict[str, Any]]:
        """Collect grants from all enabled sources"""
        all_grants = []

        # Collect from grants.gov
        if self.config.get('sources', {}).get('federal', {}).get('grants_gov', {}).get('enabled'):
            logger.info("Collecting from grants.gov...")
            grants = self.grants_gov.fetch_opportunities(
                keywords=self.org_profile.focus_areas
            )
            all_grants.extend(grants)
            logger.info(f"Found {len(grants)} grants from grants.gov")

        # Collect from NSF
        if self.config.get('sources', {}).get('federal', {}).get('nsf', {}).get('enabled'):
            logger.info("Collecting from NSF...")
            grants = self.nsf.fetch_opportunities(
                keywords=self.org_profile.focus_areas
            )
            all_grants.extend(grants)
            logger.info(f"Found {len(grants)} grants from NSF")

        # Collect from foundations
        if self.config.get('sources', {}).get('foundations', {}).get('kauffman', {}).get('enabled'):
            logger.info("Collecting from Kauffman Foundation...")
            grants = self.foundations.fetch_kauffman_opportunities()
            all_grants.extend(grants)
            logger.info(f"Found {len(grants)} grants from Kauffman")

        logger.info(f"Total grants collected: {len(all_grants)}")
        return all_grants

    def run(self, test_mode: bool = False) -> str:
        """
        Run full grant discovery and analysis pipeline

        Args:
            test_mode: If True, skip email delivery

        Returns:
            Path to generated digest file
        """
        logger.info("=" * 50)
        logger.info("Starting GrantBot run")
        logger.info("=" * 50)

        # Step 1: Collect grants
        all_grants = self.collect_grants()

        # Step 2: Filter and match
        matched_grants = self.matcher.filter_and_rank(all_grants)
        logger.info(f"Matched grants after filtering: {len(matched_grants)}")

        # Step 3: Deduplicate (skip already-seen grants)
        new_grants = []
        for grant in matched_grants:
            grant_id = grant.get('opportunity_id') or grant.get('title', '')
            if not self.deduplicator.is_duplicate(grant_id, grant_id):
                new_grants.append(grant)
                self.deduplicator.mark_seen(grant_id, grant_id)
        logger.info(f"New grants after deduplication: {len(new_grants)}")

        # Step 4: Deep analysis (top grants only to save API calls)
        analyzed_grants = []
        for grant in new_grants[:10]:  # Analyze top 10
            analysis = self.analyzer.analyze_grant(grant, vars(self.org_profile))
            grant.update(analysis)
            analyzed_grants.append(grant)

        # Step 5: Generate digest
        markdown = self.digest.generate_markdown(analyzed_grants)

        # Save to file
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{date_str}-grant-digest.md")

        with open(output_path, 'w') as f:
            f.write(markdown)
        logger.info(f"Digest saved to {output_path}")

        # Step 6: Send email (unless test mode)
        if not test_mode and analyzed_grants:
            # TODO: Implement email sending
            logger.info("Email sending not yet implemented")

        logger.info("GrantBot run complete")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="GrantBot - AI-powered grant discovery")
    parser.add_argument('--test', action='store_true', help="Test mode (no email)")
    args = parser.parse_args()

    bot = GrantBot()
    output = bot.run(test_mode=args.test)
    print(f"Digest generated: {output}")


if __name__ == "__main__":
    main()
