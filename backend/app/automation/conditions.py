import re
from typing import Optional, List
from backend.app.models.contact import Contact
from backend.app.models.conversation import Conversation

class ConditionEvaluator:
    @staticmethod
    def match_text(input_text: str, pattern: str, match_type: str = "contains") -> bool:
        if not input_text or not pattern:
            return False

        text_lower = input_text.strip().lower()
        pat_lower = pattern.strip().lower()

        if match_type == "exact" or match_type == "equals":
            return text_lower == pat_lower
        elif match_type == "contains":
            return pat_lower in text_lower
        elif match_type == "starts_with":
            return text_lower.startswith(pat_lower)
        elif match_type == "ends_with":
            return text_lower.endswith(pat_lower)
        elif match_type == "regex":
            try:
                return bool(re.search(pattern, input_text, re.IGNORECASE))
            except Exception:
                return False
        return False

    @staticmethod
    def match_any_keyword(input_text: str, keywords: List[str], match_type: str = "contains") -> bool:
        for kw in keywords:
            if ConditionEvaluator.match_text(input_text, kw, match_type):
                return True
        return False

    @staticmethod
    def is_new_contact(contact: Contact) -> bool:
        return contact.conversation_count <= 1
