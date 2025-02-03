from dataclasses import dataclass, field

from jobs import JobPost, JobResponse


@dataclass
class ScraperResponse:
    remaining_jobs: list[JobPost] = field(default_factory=list)
    filtered_jobs: list[JobPost] = field(default_factory=list)
    site_to_error_dict: dict[str, JobResponse] = field(default_factory=dict)