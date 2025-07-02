import re
import json
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        if not isinstance(text, str):
            return 0
        return len(text.split())

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_transcript_structure(data: Dict) -> bool:
        """Validate transcript data structure"""
        required_fields = ['content']
        
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate content structure
        content = data.get('content', [])
        if not isinstance(content, list):
            return False
        
        for message in content:
            if not isinstance(message, dict):
                return False
            if 'message' not in message or 'agent' not in message:
                return False
        
        return True
    
    @staticmethod
    def validate_json_data(json_str: str) -> Optional[Dict]:
        """Validate and parse JSON string"""
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            return None

class StatisticsCalculator:
    """Statistical calculation utilities"""
    
    @staticmethod
    def calculate_basic_stats(data: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for numerical data"""
        if not data:
            return {}
        
        data_array = np.array(data)
        
        return {
            'mean': float(np.mean(data_array)),
            'median': float(np.median(data_array)),
            'std': float(np.std(data_array)),
            'min': float(np.min(data_array)),
            'max': float(np.max(data_array)),
            'count': len(data)
        }
    
    @staticmethod
    def calculate_sentiment_distribution(sentiments: List[str]) -> Dict[str, int]:
        """Calculate sentiment distribution"""
        from collections import Counter
        return dict(Counter(sentiments))

class FileHandler:
    """File handling utilities"""
    
    @staticmethod
    def safe_read_json(file_path: str) -> Optional[Dict]:
        """Safely read JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def safe_write_json(data: Dict, file_path: str) -> bool:
        """Safely write JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            return False

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_time = datetime.now()
        self.metrics[operation] = {'start': self.start_time}
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        if operation in self.metrics and self.start_time:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.metrics[operation]['end'] = end_time
            self.metrics[operation]['duration'] = duration
            logger.info(f"Operation '{operation}' completed in {duration:.2f} seconds")
            return duration
        return None
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        return self.metrics

def format_response(status: str, data: Any = None, message: str = "", error: str = "") -> Dict:
    """Format API response"""
    response = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if error:
        response["error"] = error
    
    return response

def paginate_data(data: List, page: int = 1, page_size: int = 10) -> Dict:
    """Paginate data"""
    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_data = data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
