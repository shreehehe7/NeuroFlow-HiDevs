import pytest
import asyncio
from fastapi import HTTPException
from ..resilience.circuit_breaker import circuit_breaker, CircuitOpenError
from ..resilience.rate_limiter import TokenBucketRateLimiter, check_rate_limit

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = circuit_breaker("test")
    
    # 5 failures
    for _ in range(5):
        try:
            async with cb:
                raise ValueError("Fail")
        except ValueError:
            pass
            
    # 6th call should raise CircuitOpenError
    with pytest.raises(CircuitOpenError):
        async with cb:
            pass

def test_rate_limiter():
    limiter = TokenBucketRateLimiter(capacity=60, refill_rate=1.0)
    
    # Consume 60 tokens successfully
    for _ in range(60):
        check_rate_limit(limiter)
        
    # 61st token should fail
    with pytest.raises(HTTPException) as excinfo:
        check_rate_limit(limiter)
    
    assert excinfo.value.status_code == 429
