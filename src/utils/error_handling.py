"""
Enhanced Error Handling Utilities
Provides retry logic, circuit breakers, and robust error recovery
"""

import time
import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject calls
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker pattern implementation to prevent cascading failures
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        result = breaker.call(risky_function, arg1, arg2)
    """
    
    def __init__(self, 
                 failure_threshold: int = 3,
                 recovery_timeout: int = 30,
                 expected_exception: Type[Exception] = Exception):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout))
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count > 2:  # Require multiple successes
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed after successful recovery")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_state(self) -> str:
        """Get current circuit state"""
        return self.state.value
    
    def reset(self):
        """Manually reset the circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0


def with_retry(max_attempts: int = 3,
               delay: float = 1.0,
               backoff: float = 2.0,
               exceptions: Tuple[Type[Exception], ...] = (Exception,),
               on_retry: Optional[Callable] = None):
    """
    Decorator for automatic retry with exponential backoff
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    
    Usage:
        @with_retry(max_attempts=3, delay=1, backoff=2)
        def risky_function():
            # May fail temporarily
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Max retries ({max_attempts}) exceeded for {func.__name__}")
                        raise e
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.1f} seconds..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            
            return None  # Should never reach here
        
        return wrapper
    return decorator


def with_timeout(timeout: int = 30):
    """
    Decorator to add timeout to function calls
    
    Args:
        timeout: Timeout in seconds
    
    Note: This uses threading and may not work with all functions
    """
    import signal
    
    def decorator(func: Callable) -> Callable:
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the timeout handler
            old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(timeout)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the old handler and cancel the alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        
        return wrapper
    return decorator


class RateLimiter:
    """
    Rate limiter to prevent overwhelming external services
    
    Usage:
        limiter = RateLimiter(max_calls=10, time_window=60)
        if limiter.can_call('api_name'):
            limiter.record_call('api_name')
            # Make API call
    """
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}  # service_name -> list of timestamps
    
    def can_call(self, service_name: str) -> bool:
        """Check if call is allowed"""
        now = time.time()
        
        if service_name not in self.calls:
            self.calls[service_name] = []
        
        # Remove old calls outside time window
        self.calls[service_name] = [
            t for t in self.calls[service_name]
            if now - t < self.time_window
        ]
        
        return len(self.calls[service_name]) < self.max_calls
    
    def record_call(self, service_name: str):
        """Record that a call was made"""
        if service_name not in self.calls:
            self.calls[service_name] = []
        
        self.calls[service_name].append(time.time())
    
    def wait_if_needed(self, service_name: str) -> float:
        """
        Wait if rate limit exceeded
        
        Returns:
            Time waited in seconds
        """
        wait_time = 0
        
        while not self.can_call(service_name):
            wait_time = 1.0
            logger.debug(f"Rate limit reached for {service_name}, waiting {wait_time}s")
            time.sleep(wait_time)
        
        return wait_time


class ErrorCollector:
    """
    Collects and categorizes errors for reporting
    
    Usage:
        collector = ErrorCollector()
        try:
            risky_operation()
        except Exception as e:
            collector.add_error('operation_name', e)
        
        collector.get_summary()
    """
    
    def __init__(self):
        self.errors = []
        self.error_counts = {}
    
    def add_error(self, operation: str, error: Exception, context: dict = None):
        """Add an error to the collection"""
        error_type = type(error).__name__
        
        self.errors.append({
            'operation': operation,
            'error_type': error_type,
            'message': str(error),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        })
        
        # Track error counts by type
        key = f"{operation}:{error_type}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def get_summary(self) -> dict:
        """Get error summary"""
        return {
            'total_errors': len(self.errors),
            'error_counts': self.error_counts,
            'recent_errors': self.errors[-10:],  # Last 10 errors
            'most_common': sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 error types
        }
    
    def clear(self):
        """Clear all collected errors"""
        self.errors = []
        self.error_counts = {}


# Example of combined usage
def safe_api_call(circuit_breaker: Optional[CircuitBreaker] = None):
    """
    Decorator combining retry and circuit breaker patterns
    
    Usage:
        breaker = CircuitBreaker()
        
        @safe_api_call(circuit_breaker=breaker)
        def call_external_api():
            # May fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @with_retry(max_attempts=3, delay=1, backoff=2)
        def wrapper(*args, **kwargs):
            if circuit_breaker:
                return circuit_breaker.call(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Test the error handling utilities
if __name__ == "__main__":
    import random
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test retry decorator
    @with_retry(max_attempts=3, delay=0.5)
    def flaky_function():
        if random.random() < 0.7:
            raise ConnectionError("Random failure")
        return "Success!"
    
    # Test circuit breaker
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
    
    def unstable_service():
        if random.random() < 0.8:
            raise Exception("Service unavailable")
        return "Service response"
    
    # Test rate limiter
    limiter = RateLimiter(max_calls=3, time_window=5)
    
    print("Testing error handling utilities...")
    
    # Test retry
    try:
        result = flaky_function()
        print(f"Retry test: {result}")
    except Exception as e:
        print(f"Retry test failed: {e}")
    
    # Test circuit breaker
    for i in range(5):
        try:
            result = breaker.call(unstable_service)
            print(f"Circuit breaker test {i}: {result}")
        except Exception as e:
            print(f"Circuit breaker test {i}: {e} (State: {breaker.get_state()})")
        time.sleep(1)
    
    # Test rate limiter
    for i in range(5):
        if limiter.can_call('test_api'):
            limiter.record_call('test_api')
            print(f"Rate limiter test {i}: Call allowed")
        else:
            print(f"Rate limiter test {i}: Rate limit exceeded")
        time.sleep(0.5)