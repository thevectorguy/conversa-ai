import asyncio
import logging
from typing import List, Dict, Optional
from textblob import TextBlob
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Advanced sentiment analysis for agent conversations"""
    
    def __init__(self):
        self.sentiment_thresholds = {
            'very_positive': 0.5,
            'positive': 0.1,
            'neutral': 0.0,
            'negative': -0.1,
            'very_negative': -0.5
        }
    
    async def initialize(self):
        """Initialize the sentiment analyzer"""
        logger.info("SentimentAnalyzer initialized successfully")
    
    async def analyze_agent_sentiment(self, messages: List[str]) -> Dict:
        """Analyze overall sentiment for an agent's messages"""
        try:
            if not messages:
                return {
                    'overall_sentiment': 'neutral',
                    'confidence': 0.0,
                    'sentiment_distribution': {},
                    'average_polarity': 0.0,
                    'average_subjectivity': 0.0
                }
            
            polarities = []
            subjectivities = []
            sentiments = []
            
            for message in messages:
                if not message or not isinstance(message, str):
                    continue
                
                blob = TextBlob(message)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                polarities.append(polarity)
                subjectivities.append(subjectivity)
                
                # Classify sentiment
                if polarity >= self.sentiment_thresholds['very_positive']:
                    sentiments.append('very_positive')
                elif polarity >= self.sentiment_thresholds['positive']:
                    sentiments.append('positive')
                elif polarity <= self.sentiment_thresholds['very_negative']:
                    sentiments.append('very_negative')
                elif polarity <= self.sentiment_thresholds['negative']:
                    sentiments.append('negative')
                else:
                    sentiments.append('neutral')
            
            if not polarities:
                return {
                    'overall_sentiment': 'neutral',
                    'confidence': 0.0,
                    'sentiment_distribution': {},
                    'average_polarity': 0.0,
                    'average_subjectivity': 0.0
                }
            
            # Calculate averages
            avg_polarity = np.mean(polarities)
            avg_subjectivity = np.mean(subjectivities)
            
            # Determine overall sentiment
            overall_sentiment = self._classify_overall_sentiment(avg_polarity)
            
            # Calculate confidence based on consistency
            confidence = self._calculate_confidence(sentiments, avg_subjectivity)
            
            # Sentiment distribution
            sentiment_dist = dict(Counter(sentiments))
            
            return {
                'overall_sentiment': overall_sentiment,
                'confidence': round(confidence, 3),
                'sentiment_distribution': sentiment_dist,
                'average_polarity': round(avg_polarity, 3),
                'average_subjectivity': round(avg_subjectivity, 3),
                'message_count': len(messages),
                'analyzed_messages': len(polarities)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing agent sentiment: {str(e)}")
            return {
                'overall_sentiment': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _classify_overall_sentiment(self, avg_polarity: float) -> str:
        """Classify overall sentiment based on average polarity"""
        if avg_polarity >= self.sentiment_thresholds['very_positive']:
            return 'very_positive'
        elif avg_polarity >= self.sentiment_thresholds['positive']:
            return 'positive'
        elif avg_polarity <= self.sentiment_thresholds['very_negative']:
            return 'very_negative'
        elif avg_polarity <= self.sentiment_thresholds['negative']:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, sentiments: List[str], avg_subjectivity: float) -> float:
        """Calculate confidence score based on sentiment consistency and subjectivity"""
        if not sentiments:
            return 0.0
        
        # Consistency score (how often the most common sentiment appears)
        sentiment_counts = Counter(sentiments)
        most_common_count = sentiment_counts.most_common(1)[0][1]
        consistency_score = most_common_count / len(sentiments)
        
        # Subjectivity score (higher subjectivity can indicate more confident sentiment)
        subjectivity_score = min(avg_subjectivity * 2, 1.0)  # Cap at 1.0
        
        # Combine scores
        confidence = (consistency_score * 0.7) + (subjectivity_score * 0.3)
        
        return min(confidence, 1.0)
    
    async def compare_agent_sentiments(self, agent1_messages: List[str], 
                                     agent2_messages: List[str]) -> Dict:
        """Compare sentiments between two agents"""
        try:
            agent1_analysis = await self.analyze_agent_sentiment(agent1_messages)
            agent2_analysis = await self.analyze_agent_sentiment(agent2_messages)
            
            # Calculate sentiment difference
            polarity_diff = abs(
                agent1_analysis.get('average_polarity', 0) - 
                agent2_analysis.get('average_polarity', 0)
            )
            
            # Determine interaction dynamic
            dynamic = self._determine_interaction_dynamic(
                agent1_analysis.get('overall_sentiment', 'neutral'),
                agent2_analysis.get('overall_sentiment', 'neutral')
            )
            
            return {
                'agent_1': agent1_analysis,
                'agent_2': agent2_analysis,
                'polarity_difference': round(polarity_diff, 3),
                'interaction_dynamic': dynamic,
                'sentiment_alignment': 'aligned' if polarity_diff < 0.2 else 'divergent'
            }
            
        except Exception as e:
            logger.error(f"Error comparing agent sentiments: {str(e)}")
            return {'error': str(e)}
    
    def _determine_interaction_dynamic(self, agent1_sentiment: str, 
                                     agent2_sentiment: str) -> str:
        """Determine the dynamic between two agents based on their sentiments"""
        positive_sentiments = {'positive', 'very_positive'}
        negative_sentiments = {'negative', 'very_negative'}
        
        if agent1_sentiment in positive_sentiments and agent2_sentiment in positive_sentiments:
            return 'collaborative_positive'
        elif agent1_sentiment in negative_sentiments and agent2_sentiment in negative_sentiments:
            return 'collaborative_negative'
        elif (agent1_sentiment in positive_sentiments and agent2_sentiment in negative_sentiments) or \
             (agent1_sentiment in negative_sentiments and agent2_sentiment in positive_sentiments):
            return 'contrasting'
        elif agent1_sentiment == 'neutral' and agent2_sentiment == 'neutral':
            return 'neutral_discussion'
        else:
            return 'mixed_dynamic'
