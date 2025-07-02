from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

# Authentication schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"

# Analysis request/response schemas
class TranscriptAnalysisRequest(BaseModel):
    transcript_data: Dict[str, Any]

class TranscriptAnalysisResponse(BaseModel):
    status: str
    message: str
    analysis: Dict[str, Any]
    # analysis will contain:
    # - article_url: str
    # - agent_1_messages: int, agent_2_messages: int
    # - agent_1_sentiment: Dict, agent_2_sentiment: Dict
    # - total_messages: int, analysis_confidence: float
    # - transcript_summary: str (NEW)
    # - sentiment_distribution: Dict[str, int] (NEW)

class DataSummaryResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class RawInputRequest(BaseModel):
    raw_data: Dict[str, Any]

class RawInputResponse(BaseModel):
    status: str
    message: str
    processed_data: Dict[str, Any]
    analysis: Dict[str, Any]

# Agent and Article statistics
class AgentStatsResponse(BaseModel):
    status: str
    message: str
    agent_statistics: Dict[str, Any]
    total_agents: int

class ArticleStatsResponse(BaseModel):
    status: str
    message: str
    article_statistics: Dict[str, Any]
    total_articles: int

# Health check
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: Optional[str] = None
