class CircuitOpenError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5,
                 recovery_timeout: int = 60, half_open_max_calls: int = 3):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # Mock internal state for testing without redis
        self.failures = 0
        self.state = "closed"
        self.half_open_calls = 0

    async def __aenter__(self):
        if self.state == "open":
            raise CircuitOpenError(f"Circuit {self.name} is OPEN")
        if self.state == "half-open":
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitOpenError(f"Circuit {self.name} is HALF-OPEN limit reached")
            self.half_open_calls += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "open"
            if self.state == "half-open":
                self.state = "open"
        else:
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
                self.half_open_calls = 0
        return False

def circuit_breaker(name: str):
    return CircuitBreaker(name)
