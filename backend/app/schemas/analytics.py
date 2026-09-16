from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MetricCard(BaseModel):
    title: str
    value: str
    trend: str
    trend_positive: bool
    description: str

class TimeSeriesPoint(BaseModel):
    timestamp: str
    count: int

class ConversationSplit(BaseModel):
    bot_percentage: float
    ai_percentage: float
    human_percentage: float

class DashboardMetrics(BaseModel):
    total_conversations: int
    active_conversations: int
    unread_messages: int
    new_leads: int
    qualified_leads: int
    converted_leads: int
    bot_replies: int
    ai_replies: int
    human_handovers: int
    
    cards: List[MetricCard]
    messages_chart: List[TimeSeriesPoint]
    leads_chart: List[TimeSeriesPoint]
    conversation_split: ConversationSplit
    recent_activities: List[Dict[str, Any]]
