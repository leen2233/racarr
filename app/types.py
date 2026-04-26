from dataclasses import dataclass
from typing import Optional

@dataclass 
class RemoteComic:
    name: Optional[str]
    url: str
    cover: Optional[str]
    publisher: Optional[str]
    genres: list
    year: Optional[int]
    total_issues: Optional[int]

    def serialize(self):
        return {
            "name": self.name,
            "url": self.url,
            "cover": self.cover,
            "publisher": self.publisher,
            "genres": self.genres,
            "year": self.year,
            "total_issues": self.total_issues
        }


