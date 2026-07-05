from fastapi import HTTPException
import time

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        
        # Refill tokens
        refill = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + refill)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

def check_rate_limit(limiter: TokenBucketRateLimiter):
    if not limiter.consume(1):
        raise HTTPException(status_code=429, detail="Too Many Requests")
