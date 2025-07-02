from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from typing import Dict, List, Optional
import logging
import asyncio
from pydantic import BaseModel

from app.models.schemas import (
    TranscriptAnalysisRequest, TranscriptAnalysisResponse,
    DataSummaryResponse, RawInputRequest, RawInputResponse
)
from app.api.auth import get_current_user
from app.core.data_processor import DataProcessor

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Dependency to get data processor
async def get_data_processor():
    from app.main import app
    return app.state.data_processor

@router.get("/summary", response_model=DataSummaryResponse)
async def get_dataset_summary(
    current_user: dict = Depends(get_current_user),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Endpoint 1: Fetch and return processed dataset summary"""
    try:
        summary_stats = data_processor.get_summary_stats()
        
        if not summary_stats:
            raise HTTPException(status_code=404, detail="No summary statistics available")
        
        # Check if dataset_summary is requested and not already generated
        generate_summary = False
        if 'generate_summary' in summary_stats:
            generate_summary = summary_stats['generate_summary']
            
        if generate_summary and (summary_stats.get('dataset_summary') is None):
            # Generate dataset summary using LLM
            llm_analyzer = data_processor.llm_analyzer
            summary_text = await llm_analyzer.generate_dataset_summary(summary_stats)
            summary_stats['dataset_summary'] = summary_text
            
            # Update the stored summary stats
            data_processor.summary_stats['dataset_summary'] = summary_text
            data_processor.summary_stats['generate_summary'] = False
        
        return DataSummaryResponse(
            status="success",
            data=summary_stats,
            message="Dataset summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting dataset summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/transform", response_model=RawInputResponse)
async def transform_raw_input(
    request: RawInputRequest,
    current_user: dict = Depends(get_current_user),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Endpoint 2: Perform real-time data transformation"""
    try:
        result = await data_processor.transform_raw_input(request.raw_data)
        
        return RawInputResponse(
            status="success",
            processed_data=result.get("processed_input", {}),
            analysis=result.get("analysis", {}),
            message="Raw input transformed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error transforming raw input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transformation error: {str(e)}")

@router.post("/analyze", response_model=TranscriptAnalysisResponse)
async def analyze_transcript(
    request: TranscriptAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Endpoint 3: Allow users to send input and receive processed insights"""
    try:
        logger.info(f"Received analysis request from user: {current_user.get('username')}")
        logger.info(f"Transcript data type: {type(request.transcript_data)}")
        
        # Validate the transcript data
        if not request.transcript_data:
            raise HTTPException(status_code=400, detail="Empty transcript data")
            
        # Perform analysis
        analysis = await data_processor.analyze_transcript(request.transcript_data)
        
        # No more dataset-wide post-analysis mutations;
        # we just send back exactly what DataProcessor.analyze_transcript returned
        background_tasks.add_task(log_analysis_request, current_user.get("username", "unknown"))
        
        return TranscriptAnalysisResponse(
            status="success",
            analysis=analysis,
            message="Transcript analyzed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error in transcript analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid transcript format: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-07-01T00:00:00Z"}

@router.get("/stats/agents")
async def get_agent_statistics(
    current_user: dict = Depends(get_current_user),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Get detailed agent statistics"""
    try:
        df = data_processor.get_dataframe()
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Agent-wise detailed statistics
        agent_stats = {}
        
        # Check if we should reset sentiment counts
        reset_counts = getattr(data_processor, 'reset_sentiment_counts', False)
        
        for agent in df['agent'].unique():
            agent_data = df[df['agent'] == agent]
            
            agent_stats[agent] = {
                "total_messages": len(agent_data),
                "avg_message_length": round(agent_data['message_length'].mean(), 2),
                "avg_word_count": round(agent_data['word_count'].mean(), 2),
                "avg_sentiment_score": round(agent_data['sentiment_score'].mean(), 3),
                "unique_transcripts": agent_data['transcript_id'].nunique()
            }
        
        return {
            "status": "success",
            "agent_statistics": agent_stats,
            "total_agents": len(agent_stats),
            "message": "Agent statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting agent statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.get("/stats/articles")
async def get_article_statistics(
    current_user: dict = Depends(get_current_user),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Get article-wise statistics"""
    try:
        df = data_processor.get_dataframe()
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Article-wise statistics
        article_stats = df.groupby('transcript_id').agg({
            'message': 'count',
            'agent': lambda x: x.nunique(),
            'word_count': 'sum',
            'sentiment_score': 'mean',
            'article_url': 'first'
        }).round(3)
        
        article_stats.columns = ['total_messages', 'unique_agents', 'total_words', 'avg_sentiment', 'url']
        
        return {
            "status": "success",
            "article_statistics": article_stats.to_dict('index'),
            "total_articles": len(article_stats),
            "message": "Article statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting article statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

async def log_analysis_request(username: str):
    """Background task to log analysis requests"""
    logger.info(f"Analysis request completed for user: {username}")
