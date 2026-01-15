"""
Grant Matcher

Matches grant opportunities against organization profile.
Filters out ineligible grants and scores relevance.

Reference implementations:
- https://github.com/vanderbilt-data-science/grant-match (AI matching)
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrgProfile:
    """Organization profile for grant matching"""
    entity_type: str  # "university", "nonprofit", etc.
    location: str  # State for geographic restrictions
    focus_areas: List[str]  # Keywords for relevance matching
    grant_size_min: int
    grant_size_max: int


class GrantMatcher:
    """Matches grants against organization profile"""

    def __init__(self, org_profile: OrgProfile):
        self.profile = org_profile

    def is_eligible(self, grant: Dict[str, Any]) -> bool:
        """
        Check if org is eligible for this grant

        Checks:
        - Entity type (university, nonprofit, etc.)
        - Geographic restrictions
        - Grant size range
        """
        # TODO: Implement eligibility checking
        # Parse grant eligibility field and match against profile
        logger.warning("GrantMatcher.is_eligible() not implemented")
        return True

    def calculate_relevance_score(self, grant: Dict[str, Any]) -> float:
        """
        Calculate relevance score (0-10) based on focus area alignment

        Uses keyword matching and optionally LLM for semantic matching.
        """
        # TODO: Implement scoring
        # Options:
        # 1. Simple keyword overlap
        # 2. TF-IDF similarity
        # 3. LLM-based semantic matching (see Vanderbilt grant-match)
        logger.warning("GrantMatcher.calculate_relevance_score() not implemented")
        return 5.0

    def filter_and_rank(self, grants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter for eligible grants and rank by relevance

        Returns grants sorted by relevance score with eligibility confirmed.
        """
        eligible = [g for g in grants if self.is_eligible(g)]
        for grant in eligible:
            grant['relevance_score'] = self.calculate_relevance_score(grant)
        return sorted(eligible, key=lambda g: g['relevance_score'], reverse=True)
