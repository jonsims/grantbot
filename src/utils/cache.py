"""
Simple File-Based Caching System
Provides TTL-based caching for API responses and processed data
"""

import os
import json
import pickle
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Simple file-based cache with TTL support
    
    Usage:
        cache = SimpleCache(cache_dir="cache")
        
        # Store data
        cache.set("my_key", {"data": "value"}, ttl_hours=1)
        
        # Retrieve data
        data = cache.get("my_key")
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl_hours: float = 1.0):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_hours = default_ttl_hours
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats tracking
        self.hits = 0
        self.misses = 0
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key"""
        # Hash the key to handle special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _get_metadata_path(self, key: str) -> Path:
        """Generate metadata file path from key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.meta"
    
    def set(self, key: str, value: Any, ttl_hours: Optional[float] = None) -> bool:
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_hours: Time-to-live in hours (None = use default)
        
        Returns:
            True if successfully cached
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)
            
            # Store the data
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Store metadata
            ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours
            metadata = {
                'key': key,
                'created': datetime.now().isoformat(),
                'expires': (datetime.now() + timedelta(hours=ttl)).isoformat(),
                'ttl_hours': ttl
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)
            
            logger.debug(f"Cached {key} with TTL of {ttl} hours")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)
            
            # Check if cache exists
            if not cache_path.exists() or not meta_path.exists():
                self.misses += 1
                logger.debug(f"Cache miss for {key}: files not found")
                return None
            
            # Check metadata
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            # Check expiration
            expires = datetime.fromisoformat(metadata['expires'])
            if datetime.now() > expires:
                self.misses += 1
                logger.debug(f"Cache miss for {key}: expired")
                # Clean up expired cache
                self.delete(key)
                return None
            
            # Load and return data
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            self.hits += 1
            logger.debug(f"Cache hit for {key}")
            return value
            
        except Exception as e:
            logger.error(f"Failed to retrieve {key} from cache: {str(e)}")
            self.misses += 1
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted successfully
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)
            
            if cache_path.exists():
                cache_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            
            logger.debug(f"Deleted cache for {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete {key} from cache: {str(e)}")
            return False
    
    def clear(self) -> int:
        """
        Clear all cache files
        
        Returns:
            Number of items cleared
        """
        count = 0
        
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
                count += 1
            
            for meta_file in self.cache_dir.glob("*.meta"):
                meta_file.unlink()
            
            logger.info(f"Cleared {count} items from cache")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return count
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items from cache
        
        Returns:
            Number of expired items removed
        """
        count = 0
        
        try:
            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    expires = datetime.fromisoformat(metadata['expires'])
                    if datetime.now() > expires:
                        key = metadata['key']
                        if self.delete(key):
                            count += 1
                            
                except Exception as e:
                    logger.debug(f"Error checking {meta_file}: {str(e)}")
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired cache items")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {str(e)}")
            return count
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_files = len(list(self.cache_dir.glob("*.cache")))
        
        # Calculate cache size
        total_size = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            total_size += cache_file.stat().st_size
        
        hit_rate = (self.hits / (self.hits + self.misses) * 100) if (self.hits + self.misses) > 0 else 0
        
        return {
            'total_items': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'cache_dir': str(self.cache_dir)
        }


class APIResponseCache(SimpleCache):
    """
    Specialized cache for API responses with automatic key generation
    
    Usage:
        cache = APIResponseCache()
        
        # Cache an API response
        response = cache.get_or_fetch(
            "weather",
            {"zip": "01701"},
            fetch_func=lambda: weather_api.get_forecast("01701"),
            ttl_hours=1
        )
    """
    
    def make_key(self, api_name: str, params: dict) -> str:
        """Generate cache key from API name and parameters"""
        # Sort params for consistent keys
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params)
        return f"{api_name}:{param_str}"
    
    def get_or_fetch(self, 
                     api_name: str,
                     params: dict,
                     fetch_func: callable,
                     ttl_hours: Optional[float] = None) -> Any:
        """
        Get from cache or fetch from API
        
        Args:
            api_name: Name of the API
            params: API parameters
            fetch_func: Function to call if cache miss
            ttl_hours: Cache TTL in hours
        
        Returns:
            Cached or fetched data
        """
        key = self.make_key(api_name, params)
        
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            logger.debug(f"Using cached response for {api_name}")
            return cached
        
        # Fetch from API
        logger.debug(f"Fetching fresh data for {api_name}")
        try:
            data = fetch_func()
            
            # Cache the response
            if data is not None:
                self.set(key, data, ttl_hours)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch {api_name}: {str(e)}")
            return None


class ContentCache(SimpleCache):
    """
    Specialized cache for processed content with deduplication
    
    Usage:
        cache = ContentCache()
        
        # Check if content already processed
        if not cache.is_duplicate(article_url):
            process_article(article)
            cache.mark_processed(article_url)
    """
    
    def __init__(self, cache_dir: str = "cache/content", default_ttl_hours: float = 24.0):
        super().__init__(cache_dir, default_ttl_hours)
        self.processed_urls = set()
        self._load_processed_urls()
    
    def _load_processed_urls(self):
        """Load set of processed URLs"""
        urls_file = self.cache_dir / "processed_urls.json"
        if urls_file.exists():
            try:
                with open(urls_file, 'r') as f:
                    self.processed_urls = set(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load processed URLs: {str(e)}")
    
    def _save_processed_urls(self):
        """Save set of processed URLs"""
        urls_file = self.cache_dir / "processed_urls.json"
        try:
            with open(urls_file, 'w') as f:
                json.dump(list(self.processed_urls), f)
        except Exception as e:
            logger.error(f"Failed to save processed URLs: {str(e)}")
    
    def is_duplicate(self, url: str) -> bool:
        """Check if URL has been processed recently"""
        return url in self.processed_urls
    
    def mark_processed(self, url: str):
        """Mark URL as processed"""
        self.processed_urls.add(url)
        self._save_processed_urls()
    
    def clear_old_urls(self, days: int = 7):
        """Clear URLs older than specified days"""
        # For simplicity, just clear all if set is too large
        if len(self.processed_urls) > 10000:
            self.processed_urls.clear()
            self._save_processed_urls()
            logger.info("Cleared processed URLs cache")


# Test the cache system
if __name__ == "__main__":
    import time
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Simple Cache...")
    
    # Test SimpleCache
    cache = SimpleCache(cache_dir="test_cache", default_ttl_hours=0.001)  # 3.6 seconds
    
    # Store data
    test_data = {"name": "test", "value": 42, "list": [1, 2, 3]}
    cache.set("test_key", test_data)
    
    # Retrieve immediately
    retrieved = cache.get("test_key")
    print(f"Retrieved: {retrieved}")
    assert retrieved == test_data
    
    # Wait for expiration
    print("Waiting for cache to expire...")
    time.sleep(4)
    
    # Try to retrieve expired
    expired = cache.get("test_key")
    print(f"After expiration: {expired}")
    assert expired is None
    
    # Test API cache
    print("\nTesting API Response Cache...")
    api_cache = APIResponseCache(cache_dir="test_cache/api")
    
    class CallCounter:
        def __init__(self):
            self.count = 0
    
    counter = CallCounter()
    def mock_api():
        counter.count += 1
        return {"response": "data", "call": counter.count}
    
    # First call - should fetch
    result1 = api_cache.get_or_fetch("test_api", {"param": "value"}, mock_api, ttl_hours=1)
    print(f"First call: {result1}")
    
    # Second call - should use cache
    result2 = api_cache.get_or_fetch("test_api", {"param": "value"}, mock_api, ttl_hours=1)
    print(f"Second call: {result2}")
    
    assert result1 == result2
    assert call_count == 1  # Should only call API once
    
    # Get stats
    stats = api_cache.get_stats()
    print(f"\nCache stats: {stats}")
    
    # Cleanup
    cache.clear()
    api_cache.clear()
    
    print("\nAll cache tests passed!")