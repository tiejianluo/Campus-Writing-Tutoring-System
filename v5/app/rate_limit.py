import time
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class FixedWindowRateLimiter:
    limit: int
    window_seconds: int = 60
    _events: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))

    def allow(self, key: str, now: float | None = None) -> bool:
        if self.limit <= 0:
            return False
        current = time.monotonic() if now is None else now
        events = self._events[key]
        cutoff = current - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(current)
        return True

