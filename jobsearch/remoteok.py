from dataclasses import dataclass
from datetime import datetime
import httpx


# Change to automatically filter jobs by tags
# https://remoteok.io/api?tags=php,database,xpath
REMOTEOK_API_URL = "https://remoteok.io/api"


@dataclass(frozen=True)
class RemoteOkJobPost:
    id: int
    url: str
    company: str
    position: str
    description: str
    location: str
    tags: list[str]
    date: datetime

    @staticmethod
    def from_json(json):
        return RemoteOkJobPost(
            id=int(json['id']),
            url=json['url'],
            company=json['company'],
            position=json['position'],
            description=json['description'],
            location=json['location'],
            tags=json['tags'],
            date=datetime.fromisoformat(json['date'])
        )


def fetch_jobs() -> list[RemoteOkJobPost]:
    job_list = httpx.get(REMOTEOK_API_URL).json()[1:]
    return [RemoteOkJobPost.from_json(job_post) for job_post in job_list]