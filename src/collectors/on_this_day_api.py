"""
On This Day API Integration
Uses multiple free APIs to get historical events for the current date
"""

import requests
from typing import Dict, Any, List
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class OnThisDayCollector:
    def __init__(self):
        # Multiple API options for reliability
        self.apis = [
            {
                'name': 'History API',
                'base_url': 'http://history.muffinlabs.com/date',
                'type': 'muffinlabs'
            },
            {
                'name': 'Today in History',
                'base_url': 'https://byabbe.se/on-this-day',
                'type': 'byabbe'
            }
        ]
    
    def _call_muffinlabs_api(self, month: int, day: int) -> List[Dict[str, Any]]:
        """Call the Muffin Labs History API"""
        try:
            url = f"http://history.muffinlabs.com/date/{month}/{day}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = []
            if data.get('data') and data['data'].get('Events'):
                for event in data['data']['Events'][:10]:  # Limit to 10 events
                    events.append({
                        'year': event.get('year', 'Unknown'),
                        'text': event.get('text', 'No description available'),
                        'source': 'Muffin Labs History API'
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Muffin Labs API error: {str(e)}")
            return []
    
    def _call_byabbe_api(self, month: int, day: int) -> List[Dict[str, Any]]:
        """Call the Byabbe On This Day API"""
        try:
            url = f"https://byabbe.se/on-this-day/{month}/{day}/events.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = []
            if data.get('events'):
                for event in data['events'][:10]:  # Limit to 10 events
                    events.append({
                        'year': event.get('year', 'Unknown'),
                        'text': event.get('description', 'No description available'),
                        'source': 'Byabbe On This Day API'
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Byabbe API error: {str(e)}")
            return []
    
    def _get_fallback_events(self, month: int, day: int) -> List[Dict[str, Any]]:
        """Fallback historical events for common dates"""
        fallback_events = {
            (9, 10): [
                {'year': '1608', 'text': 'John Smith was elected council president of Jamestown.', 'source': 'Historical Archive'},
                {'year': '1813', 'text': 'The United States defeated the British fleet at the Battle of Lake Erie.', 'source': 'Historical Archive'},
                {'year': '1977', 'text': 'The last guillotine execution took place in France.', 'source': 'Historical Archive'}
            ],
            (1, 1): [
                {'year': '1502', 'text': 'Portuguese explorers landed on the coast of Brazil.', 'source': 'Historical Archive'},
                {'year': '1863', 'text': 'The Emancipation Proclamation went into effect in the United States.', 'source': 'Historical Archive'},
                {'year': '1959', 'text': 'Fidel Castro\'s forces took control of Cuba.', 'source': 'Historical Archive'}
            ]
        }
        
        return fallback_events.get((month, day), [
            {'year': 'Various', 'text': 'Many significant events have occurred on this day throughout history.', 'source': 'Historical Archive'}
        ])
    
    def get_events_for_today(self, date: datetime = None) -> Dict[str, Any]:
        """Get historical events for the current date"""
        if date is None:
            date = datetime.now()
        
        month = date.month
        day = date.day
        date_str = date.strftime("%B %d")
        
        events = []
        
        # Try each API until we get results
        for api_config in self.apis:
            try:
                if api_config['type'] == 'muffinlabs':
                    events = self._call_muffinlabs_api(month, day)
                elif api_config['type'] == 'byabbe':
                    events = self._call_byabbe_api(month, day)
                
                if events:
                    logger.info(f"Successfully fetched {len(events)} events from {api_config['name']}")
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_config['name']}: {str(e)}")
                continue
        
        # Use fallback if no API worked
        if not events:
            logger.warning("All APIs failed, using fallback events")
            events = self._get_fallback_events(month, day)
        
        # Filter for events within last 300 years and select most interesting
        if events:
            current_year = date.year
            recent_events = []
            
            for event in events:
                year_str = str(event.get('year', ''))
                if year_str.isdigit():
                    year = int(year_str)
                    if current_year - year <= 300:  # Last 300 years
                        recent_events.append(event)
            
            # Sort by year (most recent first) and pick the most interesting one
            if recent_events:
                recent_events = sorted(recent_events, key=lambda x: int(x.get('year', 0)), reverse=True)
                selected_event = recent_events[0]  # Take the most recent one
                
                return {
                    'date': date_str,
                    'events': [selected_event],  # Single event
                    'source': 'Historical APIs',
                    'total_found': len(events)
                }
            else:
                # Fallback to most recent event if none in last 300 years
                sorted_events = sorted(events, key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0, reverse=True)
                return {
                    'date': date_str,
                    'events': [sorted_events[0]] if sorted_events else [],
                    'source': 'Historical APIs',
                    'total_found': len(events)
                }
        
        return {}

# Test function
if __name__ == "__main__":
    collector = OnThisDayCollector()
    events_data = collector.get_events_for_today()
    
    print("=== ON THIS DAY TEST ===")
    if events_data.get('events'):
        print(f"Date: {events_data['date']}")
        print(f"Found {events_data.get('total_found', 0)} total events")
        print("\nSelected Events:")
        for event in events_data['events']:
            print(f"**{event['year']}**: {event['text']}")
    else:
        print("No historical events found")