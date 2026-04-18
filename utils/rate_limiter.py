import time


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        """
        max_calls: allowed calls
        period: time window in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def allow(self):
        now = time.time()

        # Remove old calls
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) >= self.max_calls:
            return False

        self.calls.append(now)
        return True