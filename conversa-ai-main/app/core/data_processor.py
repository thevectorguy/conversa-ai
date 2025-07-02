import pandas as pd
import numpy as np
import json
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import re
from collections import Counter

from app.core.config import settings
from app.core.llm_analyzer import LLMAnalyzer
from app.core.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles data loading operations"""
    
    @staticmethod
    def load_json_data(file_path: str) -> Dict:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded data from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise

class DataCleaner:
    """Handles data cleaning operations"""
    
    @staticmethod
    def clean_transcript_data(data: Dict) -> Dict:
        """Clean and validate transcript data"""
        cleaned_data = {}
        
        for transcript_id, transcript in data.items():
            if not isinstance(transcript, dict):
                continue
                
            # Validate required fields
            if 'content' not in transcript or not transcript['content']:
                continue
                
            # Clean content
            cleaned_content = []
            for message in transcript['content']:
                if isinstance(message, dict) and 'message' in message and 'agent' in message:
                    cleaned_message = {
                        'message': DataCleaner._clean_text(message['message']),
                        'agent': message['agent'],
                        'sentiment': message.get('sentiment', 'Neutral'),
                        'knowledge_source': message.get('knowledge_source', []),
                        'turn_rating': message.get('turn_rating', 'Good')
                    }
                    cleaned_content.append(cleaned_message)
            
            if cleaned_content:
                cleaned_data[transcript_id] = {
                    'article_url': transcript.get('article_url', ''),
                    'config': transcript.get('config', ''),
                    'content': cleaned_content
                }
        
        logger.info(f"Cleaned {len(cleaned_data)} transcripts")
        return cleaned_data
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean individual text messages"""
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text

class DataTransformer:
    """Handles data transformation operations"""
    
    def __init__(self):
        self.sentiment_mapping = {
            'Curious to dive deeper': 1,
            'Neutral': 0,
            'Surprised': 1,
            'Positive': 1,
            'Negative': -1
        }
    
    def transform_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """Convert cleaned data to pandas DataFrame"""
        records = []
        
        for transcript_id, transcript in data.items():
            for i, message in enumerate(transcript['content']):
                record = {
                    'transcript_id': transcript_id,
                    'article_url': transcript['article_url'],
                    'config': transcript['config'],
                    'message_id': i,
                    'message': message['message'],
                    'agent': message['agent'],
                    'sentiment': message['sentiment'],
                    'sentiment_score': self.sentiment_mapping.get(message['sentiment'], 0),
                    'knowledge_source': ','.join(message['knowledge_source']),
                    'turn_rating': message['turn_rating'],
                    'message_length': len(message['message']),
                    'word_count': len(message['message'].split())
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        logger.info(f"Created DataFrame with {len(df)} records")
        return df

class DataProcessor:
    """Main data processing orchestrator"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.data_transformer = DataTransformer()
        self.llm_analyzer = LLMAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        
        self.raw_data = None
        self.cleaned_data = None
        self.df = None
        self.summary_stats = None
    
    async def initialize(self):
        """Initialize the data processor"""
        try:
            await self.load_and_process_data()
            await self.llm_analyzer.initialize()
            
            # Set reference to data processor in LLM analyzer
            self.llm_analyzer.data_processor = self
            
            await self.sentiment_analyzer.initialize()
            logger.info("DataProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DataProcessor: {str(e)}")
            raise
    
    async def load_and_process_data(self):
        """Load and process the dataset"""
        try:
            # Load raw data
            self.raw_data = await asyncio.to_thread(
                self.data_loader.load_json_data, 
                settings.DATA_PATH
            )
            
            # Clean data
            self.cleaned_data = await asyncio.to_thread(
                self.data_cleaner.clean_transcript_data,
                self.raw_data
            )
            
            # Transform to DataFrame
            self.df = await asyncio.to_thread(
                self.data_transformer.transform_to_dataframe,
                self.cleaned_data
            )
            
            # Generate summary statistics
            await self._generate_summary_stats()
            
        except Exception as e:
            logger.error(f"Error in load_and_process_data: {str(e)}")
            raise
    
    async def _generate_summary_stats(self):
        """Generate summary statistics"""
        if self.df is None:
            return
        
        # Overall statistics
        total_transcripts = self.df['transcript_id'].nunique()
        total_messages = len(self.df)
        
        # Agent-wise statistics
        agent_stats = self.df.groupby('agent').agg({
            'message': 'count',
            'word_count': 'mean',
            'sentiment_score': 'mean',
            'transcript_id': 'nunique'
        }).round(2)
        
        # Article-wise statistics
        article_stats = self.df.groupby('transcript_id').agg({
            'message': 'count',
            'agent': lambda x: x.nunique(),
            'sentiment_score': 'mean'
        }).round(2)
        
        # Compute actual sentiment distribution from the full dataset (cleaned/transformed)
        from collections import Counter
        # normalize to lowercase keys and handle various sentiment formats
        all_sents = self.df['sentiment'].dropna().str.lower().tolist()
        counter = Counter(all_sents)
        
        # Map various sentiment formats to standard categories
        sentiment_mapping = {
            'neutral': ['neutral', 'normal'],
            'positive': ['positive', 'curious to dive deeper', 'surprised'],
            'negative': ['negative', 'angry'],
            'very_positive': ['very_positive', 'very positive', 'excellent'],
            'very_negative': ['very_negative', 'very negative', 'terrible']
        }
        
        # Initialize with zeros
        sentiment_dist = {
            'neutral': 0,
            'positive': 0,
            'negative': 0,
            'very_positive': 0,
            'very_negative': 0
        }
        
        # Map actual sentiments to categories
        for sentiment, count in counter.items():
            mapped = False
            for category, variants in sentiment_mapping.items():
                if sentiment in variants:
                    sentiment_dist[category] += count
                    mapped = True
                    break
            if not mapped:
                # Default unmapped sentiments to neutral
                sentiment_dist['neutral'] += count
        
        self.summary_stats = {
            'total_transcripts': total_transcripts,
            'total_messages': total_messages,
            'agent_stats': agent_stats.to_dict(),
            'article_stats': article_stats.to_dict(),
            'sentiment_distribution': sentiment_dist,
            'avg_messages_per_transcript': round(total_messages / total_transcripts, 2),
            'unique_articles': self.df['article_url'].nunique(),
            'dataset_summary': None  # Not used for transcript-only summary
        }
        
        logger.info("Summary statistics generated")
    
    async def analyze_transcript(self, transcript_data: Dict) -> Dict:
        """Analyze a single transcript using LLM"""
        try:
            logger.info(f"Analyzing transcript data: {type(transcript_data)}")
            
            # Handle different JSON structures
            # If the data is a collection of transcripts (like the dataset file)
            if isinstance(transcript_data, dict) and all(isinstance(k, str) and isinstance(v, dict) for k, v in transcript_data.items()):
                # Take the first transcript if multiple are provided
                if len(transcript_data) > 0:
                    logger.info(f"Multiple transcripts detected, using the first one of {len(transcript_data)}")
                    transcript_id = next(iter(transcript_data))
                    transcript_data = transcript_data[transcript_id]
                    logger.info(f"Selected transcript ID: {transcript_id}")
                else:
                    raise ValueError("Empty transcript data")
            
            # Extract messages
            if 'content' not in transcript_data:
                logger.warning("No 'content' field in transcript data, checking for alternative structure")
                # Try to adapt to different JSON structures
                if isinstance(transcript_data, list):
                    # If it's a list of messages directly
                    messages = transcript_data
                    logger.info("Using list of messages directly")
                else:
                    # If we can't find a valid structure
                    raise ValueError("Invalid transcript format: missing 'content' field")
            else:
                messages = transcript_data.get('content', [])
            
            logger.info(f"Found {len(messages)} messages to analyze")
            
            # Count messages by agent
            agent_counts = Counter()
            agent_messages = {'agent_1': [], 'agent_2': []}
            
            for msg in messages:
                if not isinstance(msg, dict):
                    logger.warning(f"Skipping non-dict message: {msg}")
                    continue
                    
                agent = msg.get('agent', '')
                message_text = msg.get('message', '')
                
                if not agent:
                    logger.warning(f"Message missing agent field: {msg}")
                    continue
                    
                # Map agent names to standard format if needed
                if agent not in ['agent_1', 'agent_2']:
                    if agent.lower() in ['agent1', 'agent 1', 'agent-1']:
                        agent = 'agent_1'
                    elif agent.lower() in ['agent2', 'agent 2', 'agent-2']:
                        agent = 'agent_2'
                
                agent_counts[agent] += 1
                if agent in agent_messages:
                    agent_messages[agent].append(message_text)
            
            logger.info(f"Agent message counts: {dict(agent_counts)}")
            
            # Analyze sentiments
            agent1_sentiment = await self.sentiment_analyzer.analyze_agent_sentiment(
                agent_messages['agent_1']
            )
            agent2_sentiment = await self.sentiment_analyzer.analyze_agent_sentiment(
                agent_messages['agent_2']
            )
            
            # Extract article URL (if available)
            article_url = transcript_data.get('article_url', 'Unknown')
            
            # If no article URL, try to infer from content
            if not article_url or article_url == 'Unknown':
                article_url = await self.llm_analyzer.extract_article_topic(messages)
            
            # Generate transcript summary from the actual messages
            msgs = [msg.get('message', '') for msg in messages if isinstance(msg, dict) and msg.get('message')]
            summary_text = await self.llm_analyzer.summarize_conversation(msgs)
            
            # Compute sentiment distribution for this single transcript
            all_messages = agent_messages['agent_1'] + agent_messages['agent_2']
            conv_sent = await self.sentiment_analyzer.analyze_agent_sentiment(all_messages)
            transcript_dist = conv_sent.get('sentiment_distribution', {})
            
            # Normalize distribution keys to match frontend expectations
            normalized_dist = {
                'neutral': transcript_dist.get('neutral', 0),
                'positive': transcript_dist.get('positive', 0),
                'negative': transcript_dist.get('negative', 0),
                'very_positive': transcript_dist.get('very_positive', 0),
                'very_negative': transcript_dist.get('very_negative', 0)
            }
            
            result = {
                'article_url': article_url,
                'agent_1_messages': agent_counts.get('agent_1', 0),
                'agent_2_messages': agent_counts.get('agent_2', 0),
                'agent_1_sentiment': agent1_sentiment,
                'agent_2_sentiment': agent2_sentiment,
                'total_messages': sum(agent_counts.values()),
                'analysis_confidence': 0.85,  # Placeholder for model confidence
                'transcript_summary': summary_text,  # NEW: LLM-generated summary
                'sentiment_distribution': normalized_dist  # NEW: Actual sentiment distribution
            }
            
            logger.info(f"Analysis completed successfully: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            raise
    
    def get_summary_stats(self) -> Dict:
        """Get processed summary statistics"""
        return self.summary_stats or {}
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the processed DataFrame"""
        return self.df
    
    async def transform_raw_input(self, raw_input: Dict) -> Dict:
        """Transform raw input into processed form"""
        try:
            # Clean the input
            cleaned_input = self.data_cleaner.clean_transcript_data({'temp': raw_input})
            
            if 'temp' not in cleaned_input:
                raise ValueError("Invalid input format")
            
            # Analyze the transcript
            analysis = await self.analyze_transcript(cleaned_input['temp'])
            
            return {
                'processed_input': cleaned_input['temp'],
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error transforming raw input: {str(e)}")
            raise
