from typing import List, Optional
from backend.app.models.automation import AutomationFlow, AutomationRule

class PriorityResolver:
    @staticmethod
    def sort_rules(rules: List[AutomationRule]) -> List[AutomationRule]:
        """Sort rules ascending by priority (1 is highest priority)."""
        return sorted(rules, key=lambda r: r.priority)

    @staticmethod
    def sort_flows(flows: List[AutomationFlow]) -> List[AutomationFlow]:
        """Sort flows ascending by priority (1 is highest priority)."""
        return sorted(flows, key=lambda f: f.priority)
