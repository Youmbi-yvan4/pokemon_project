from dataclasses import dataclass, field


@dataclass
class RequestResult:
    success: bool
    route: str
    final_status_code: int | None
    duration_seconds: float
    attempts: int
    retries: int
    status_counts: dict[int, int] = field(
        default_factory=dict
    )
    error: str | None = None


@dataclass
class LoadTestMetrics:
    total_requested: int
    completed_requests: int
    successful_requests: int
    failed_requests: int
    total_attempts: int
    total_retries: int
    status_counts: dict[int, int]
    route_counts: dict[str, int]
    route_success_counts: dict[str, int]
    route_failure_counts: dict[str, int]
    duration_seconds: float
    average_response_time_seconds: float
    requests_per_second: float
    concurrency_limit: int
    batch_size: int
    max_retries: int

    def to_dict(self):
        return {
            "total_requested": self.total_requested,
            "completed_requests": self.completed_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_attempts": self.total_attempts,
            "total_retries": self.total_retries,
            "status_counts": self.status_counts,
            "route_counts": self.route_counts,
            "route_success_counts": self.route_success_counts,
            "route_failure_counts": self.route_failure_counts,
            "duration_seconds": self.duration_seconds,
            "average_response_time_seconds": (
                self.average_response_time_seconds
            ),
            "requests_per_second": self.requests_per_second,
            "concurrency_limit": self.concurrency_limit,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
        }