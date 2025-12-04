"""QA/Safety Agent - Validates content and enforces guardrails."""
from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class QASafetyAgent:
    """
    Specialized agent for quality assurance and safety.

    Responsibilities:
    - Check ad copy for policy violations
    - Validate budget against limits
    - Ensure content meets guidelines
    - Flag potential issues before publishing
    """

    # Facebook prohibited/restricted content keywords
    PROHIBITED_WORDS = [
        'cure', 'miracle', 'guaranteed', 'risk-free', 'no risk',
        'get rich', 'make money fast', 'weight loss guarantee'
    ]

    SENSITIVE_WORDS = [
        'diet', 'weight', 'body', 'skin', 'age', 'beauty',
        'health', 'medicine', 'treatment', 'doctor'
    ]

    # Character limits
    CHAR_LIMITS = {
        'primary_text': 300,
        'headline': 40,
        'description': 90
    }

    def __init__(self, preferences: Optional[Any] = None):
        """Initialize the QA/Safety agent."""
        self.preferences = preferences
        self.default_budget = preferences.default_daily_budget if preferences else 50

    def validate_ad(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive ad validation."""
        issues = []
        warnings = []

        # Check character limits
        char_issues = self._check_character_limits(draft)
        issues.extend(char_issues)

        # Check for policy violations
        policy_issues = self._check_policy_violations(draft)
        issues.extend(policy_issues['violations'])
        warnings.extend(policy_issues['warnings'])

        # Check budget
        budget_issues = self._check_budget(draft)
        warnings.extend(budget_issues)

        # Check targeting
        targeting_issues = self._check_targeting(draft)
        warnings.extend(targeting_issues)

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'can_publish': len(issues) == 0,
            'requires_confirmation': len(warnings) > 0
        }

    def _check_character_limits(self, draft: Dict[str, Any]) -> List[str]:
        """Check if copy exceeds character limits."""
        issues = []

        fields = ['primary_text', 'headline', 'description']
        for field in fields:
            content = draft.get(field, '')
            limit = self.CHAR_LIMITS.get(field, 300)

            if len(content) > limit:
                issues.append(
                    f"{field.replace('_', ' ').title()} exceeds limit "
                    f"({len(content)}/{limit} characters)"
                )

        return issues

    def _check_policy_violations(self, draft: Dict[str, Any]) -> Dict[str, List[str]]:
        """Check for Facebook ad policy violations."""
        violations = []
        warnings = []

        # Combine all text for checking
        all_text = ' '.join([
            draft.get('primary_text', ''),
            draft.get('headline', ''),
            draft.get('description', '')
        ]).lower()

        # Check prohibited words
        for word in self.PROHIBITED_WORDS:
            if word.lower() in all_text:
                violations.append(
                    f"Potential policy violation: '{word}' may not be allowed in ads"
                )

        # Check sensitive words (warnings only)
        for word in self.SENSITIVE_WORDS:
            if word.lower() in all_text:
                warnings.append(
                    f"Sensitive content detected: '{word}' may require additional review"
                )

        # Check for excessive punctuation
        if all_text.count('!') > 3:
            warnings.append("Excessive exclamation marks may reduce ad quality")

        # Check for all caps
        words = all_text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        if len(caps_words) > 3:
            warnings.append("Excessive capitalization may violate ad policies")

        # Check for emojis (not prohibited but worth noting)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE
        )
        if emoji_pattern.search(all_text):
            warnings.append("Contains emojis - ensure they're appropriate for your audience")

        return {'violations': violations, 'warnings': warnings}

    def _check_budget(self, draft: Dict[str, Any]) -> List[str]:
        """Check budget against user's typical spending."""
        warnings = []

        budget = draft.get('budget', 0)

        if budget <= 0:
            warnings.append("No budget specified - using default")
        elif budget > self.default_budget * 5:
            warnings.append(
                f"Budget (${budget}) is significantly higher than your usual "
                f"(${self.default_budget}). Are you sure?"
            )
        elif budget > self.default_budget * 2:
            warnings.append(
                f"Budget (${budget}) is higher than your typical daily budget"
            )

        return warnings

    def _check_targeting(self, draft: Dict[str, Any]) -> List[str]:
        """Check targeting for potential issues."""
        warnings = []

        audience = draft.get('target_audience', {})

        if not audience:
            warnings.append("No targeting specified - ad will use broad targeting")
            return warnings

        # Check for very narrow targeting
        interests = audience.get('interests', [])
        if len(interests) > 10:
            warnings.append("Many interests selected - this may limit reach")

        # Check for age restrictions
        age_min = audience.get('age_min', 18)
        age_max = audience.get('age_max', 65)

        if age_max - age_min < 10:
            warnings.append("Very narrow age range may limit reach")

        # Check for geographic targeting
        countries = audience.get('countries', [])
        if not countries:
            warnings.append("No geographic targeting - consider specifying regions")

        return warnings

    def check_media(self, media_url: str, media_type: str = 'image') -> Dict[str, Any]:
        """Check media for policy compliance."""
        # In production, this would analyze the image/video
        warnings = []
        issues = []

        if not media_url:
            warnings.append("No media attached - text-only ads may perform worse")

        # Mock checks - in production, use vision API
        return {
            'is_valid': True,
            'issues': issues,
            'warnings': warnings,
            'recommendations': [
                "Ensure image has less than 20% text",
                "Use high-resolution images (1200x628 recommended)",
                "Avoid stock photo watermarks"
            ]
        }

    def pre_publish_check(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Final check before publishing."""
        ad_validation = self.validate_ad(draft)
        media_validation = self.check_media(
            draft.get('media_url', ''),
            draft.get('media_type', 'image')
        )

        all_issues = ad_validation['issues'] + media_validation['issues']
        all_warnings = ad_validation['warnings'] + media_validation['warnings']

        # Generate confirmation message
        if all_issues:
            message = "Cannot publish due to the following issues:\n"
            message += "\n".join(f"- {issue}" for issue in all_issues)
        elif all_warnings:
            message = "Ready to publish with the following notes:\n"
            message += "\n".join(f"- {warning}" for warning in all_warnings)
            message += "\n\nDo you want to proceed?"
        else:
            message = "All checks passed. Ready to publish!"

        return {
            'can_publish': len(all_issues) == 0,
            'requires_confirmation': len(all_warnings) > 0,
            'issues': all_issues,
            'warnings': all_warnings,
            'message': message
        }

    def suggest_fixes(self, issues: List[str]) -> List[Dict[str, str]]:
        """Suggest fixes for identified issues."""
        suggestions = []

        for issue in issues:
            if 'character' in issue.lower():
                suggestions.append({
                    'issue': issue,
                    'suggestion': 'Shorten the text while keeping the key message'
                })
            elif 'policy' in issue.lower():
                suggestions.append({
                    'issue': issue,
                    'suggestion': 'Remove or rephrase the flagged content'
                })
            elif 'budget' in issue.lower():
                suggestions.append({
                    'issue': issue,
                    'suggestion': 'Confirm this is intentional or adjust to a lower amount'
                })
            else:
                suggestions.append({
                    'issue': issue,
                    'suggestion': 'Review and address the concern'
                })

        return suggestions
