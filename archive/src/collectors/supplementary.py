"""
Supplementary Content Collectors
Handles Wikipedia "On This Day" and other API-based content
"""

import requests
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class WikipediaCollector:
    def __init__(self):
        self.base_url = "https://api.wikimedia.org/feed/v1/wikipedia/en"
    
    def get_on_this_day(self, date: datetime = None) -> Dict[str, Any]:
        """Get 'On This Day' events from Wikipedia"""
        if date is None:
            date = datetime.now()
        
        month = date.strftime("%m").lstrip('0')
        day = date.strftime("%d").lstrip('0')
        
        try:
            url = f"{self.base_url}/onthisday/all/{month}/{day}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract interesting events (not just deaths/births)
            events = []
            for event_type in ['events', 'selected']:
                if event_type in data:
                    for event in data[event_type][:3]:  # Top 3 events
                        events.append({
                            'year': event.get('year'),
                            'text': event.get('text'),
                            'type': event_type,
                            'pages': event.get('pages', [])
                        })
            
            return {
                'date': date.strftime("%B %d"),
                'events': events
            }
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia 'On This Day': {str(e)}")
            return {'date': date.strftime("%B %d"), 'events': []}

class MarketDataCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get basic market overview"""
        if not self.api_key:
            return self._get_mock_market_data()
        
        try:
            # Get major indices (simplified for demo)
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'SPY',  # S&P 500 ETF
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': 'S&P 500',
                    'price': quote.get('05. price'),
                    'change': quote.get('09. change'),
                    'change_percent': quote.get('10. change percent'),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
        
        return self._get_mock_market_data()
    
    def _get_mock_market_data(self) -> Dict[str, Any]:
        """Mock market data for testing"""
        return {
            'symbol': 'Market Overview',
            'status': 'Market data unavailable',
            'note': 'Connect Alpha Vantage API for live data',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

class SupplementaryCollector:
    def __init__(self, market_api_key: str = None):
        self.wikipedia = WikipediaCollector()
        self.market = MarketDataCollector(market_api_key)
    
    def collect_all_supplementary(self) -> Dict[str, Any]:
        """Collect all supplementary content"""
        return {
            'on_this_day': self.wikipedia.get_on_this_day(),
            'market_overview': self.market.get_market_overview()
        }

# Test function
if __name__ == "__main__":
    collector = SupplementaryCollector()
    data = collector.collect_all_supplementary()
    
    print("=== ON THIS DAY ===")
    otd = data['on_this_day']
    print(f"Date: {otd['date']}")
    for event in otd['events'][:2]:
        print(f"- {event['year']}: {event['text']}")
    
    print("\n=== MARKET OVERVIEW ===")
    market = data['market_overview']
    print(f"Status: {market.get('status', market.get('symbol'))}")
    if 'price' in market:
        print(f"Price: {market['price']} ({market['change_percent']})")