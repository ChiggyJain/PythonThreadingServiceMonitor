from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class ServiceConfig:
    name: str
    url: str
    timeout: int
    interval: int
    alert_threshold: dict


@dataclass
class CheckResult:
    service: str
    status_code: Optional[int]
    response_time_ms: Optional[float]
    error: Optional[str]
    timestamp: float = time.time()
