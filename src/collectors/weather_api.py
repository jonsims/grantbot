"""
Weather API Integration
Uses Open-Meteo free API for weather forecast data
"""

import requests
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherCollector:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    
    def _get_coordinates(self, zip_code: str) -> tuple[float, float]:
        """Convert zip code to coordinates using Open-Meteo geocoding"""
        try:
            # For US zip codes, append country code
            search_query = f"{zip_code} USA"
            
            params = {
                'name': search_query,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                location = data['results'][0]
                return location['latitude'], location['longitude']
            else:
                logger.warning(f"No coordinates found for zip code {zip_code}")
                # Fallback coordinates for Framingham, MA (01701 area)
                return 42.2793, -71.4162
                
        except Exception as e:
            logger.error(f"Error geocoding zip code {zip_code}: {str(e)}")
            # Fallback coordinates for Framingham, MA
            return 42.2793, -71.4162
    
    def get_weather_forecast(self, zip_code: str = "01701") -> Dict[str, Any]:
        """Get weather forecast for zip code"""
        try:
            # Get coordinates
            lat, lon = self._get_coordinates(zip_code)
            
            # Get weather forecast with hourly data
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code',
                'hourly': 'temperature_2m,precipitation_probability,weather_code',
                'temperature_unit': 'fahrenheit',
                'timezone': 'America/New_York',
                'forecast_days': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('daily') and data.get('hourly'):
                daily = data['daily']
                hourly = data['hourly']
                
                # Get hourly breakdowns (morning: 6AM, afternoon: 2PM, evening: 8PM, overnight: 2AM next day)
                morning_temp = int(hourly['temperature_2m'][6]) if len(hourly['temperature_2m']) > 6 else None
                afternoon_temp = int(hourly['temperature_2m'][14]) if len(hourly['temperature_2m']) > 14 else None
                evening_temp = int(hourly['temperature_2m'][20]) if len(hourly['temperature_2m']) > 20 else None
                overnight_temp = int(hourly['temperature_2m'][2]) if len(hourly['temperature_2m']) > 2 else None
                
                morning_precip = hourly['precipitation_probability'][6] if len(hourly['precipitation_probability']) > 6 else 0
                afternoon_precip = hourly['precipitation_probability'][14] if len(hourly['precipitation_probability']) > 14 else 0
                evening_precip = hourly['precipitation_probability'][20] if len(hourly['precipitation_probability']) > 20 else 0
                overnight_precip = hourly['precipitation_probability'][2] if len(hourly['precipitation_probability']) > 2 else 0
                
                today_data = {
                    'high_temp': int(daily['temperature_2m_max'][0]),
                    'low_temp': int(daily['temperature_2m_min'][0]),
                    'precipitation': daily['precipitation_sum'][0],
                    'weather_code': daily['weather_code'][0],
                    'location': f"Framingham, MA ({zip_code})",
                    'date': datetime.now().strftime("%B %d"),
                    'hourly_breakdown': {
                        'morning': {
                            'temp': morning_temp,
                            'precip_prob': morning_precip,
                            'condition': self._weather_code_to_description(hourly['weather_code'][6] if len(hourly['weather_code']) > 6 else daily['weather_code'][0])
                        },
                        'afternoon': {
                            'temp': afternoon_temp,
                            'precip_prob': afternoon_precip,
                            'condition': self._weather_code_to_description(hourly['weather_code'][14] if len(hourly['weather_code']) > 14 else daily['weather_code'][0])
                        },
                        'evening': {
                            'temp': evening_temp,
                            'precip_prob': evening_precip,
                            'condition': self._weather_code_to_description(hourly['weather_code'][20] if len(hourly['weather_code']) > 20 else daily['weather_code'][0])
                        },
                        'overnight': {
                            'temp': overnight_temp,
                            'precip_prob': overnight_precip,
                            'condition': self._weather_code_to_description(hourly['weather_code'][2] if len(hourly['weather_code']) > 2 else daily['weather_code'][0])
                        }
                    }
                }
                
                # Convert weather code to description
                today_data['condition'] = self._weather_code_to_description(today_data['weather_code'])
                
                return {
                    'forecast': today_data,
                    'source': 'Open-Meteo API'
                }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
        
        return {}
    
    def _weather_code_to_description(self, code: int) -> str:
        """Convert weather code to readable description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy", 
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers", 
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        return weather_codes.get(code, "Unknown conditions")

# Test function
if __name__ == "__main__":
    collector = WeatherCollector()
    forecast = collector.get_weather_forecast("01701")
    
    print("=== WEATHER FORECAST TEST ===")
    if forecast.get('forecast'):
        data = forecast['forecast']
        print(f"Location: {data['location']}")
        print(f"Date: {data['date']}")
        print(f"Condition: {data['condition']}")
        print(f"High: {data['high_temp']}°F")
        print(f"Low: {data['low_temp']}°F")
        if data['precipitation'] > 0:
            print(f"Precipitation: {data['precipitation']} inches")
    else:
        print("No weather data available")