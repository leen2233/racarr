from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchItem:
    name: Optional[str]
    id: str  # 'id' means unique identificator, can be url for comic, pk in database etc.
    cover: Optional[str]
    publisher: Optional[str]
    genres: list
    year: Optional[int]
    total_issues: Optional[int]

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "cover": self.cover,
            "publisher": self.publisher,
            "genres": self.genres,
            "year": self.year,
            "total_issues": self.total_issues,
        }


@dataclass
class Issue:
    volume = int
    issue = int
    name = Optional[str]
    file = Optional[str]
    id = str  # 'id' means unique identificator, can be url for comic, pk in database etc.

    def serialize(self):
        return {
            "name": self.name,
            "volume": self.volume,
            "issue": self.issue,
            "id": self.id,
        }


@dataclass
class Comic:
    name: Optional[str]
    id: str  # 'id' means unique identificator, can be url for comic, pk in database etc.
    description: Optional[str]
    cover: Optional[str]
    publisher: Optional[str]
    genres: list
    year: Optional[int]
    total_issues: Optional[int]
    issues: list[Issue]

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "cover": self.cover,
            "publisher": self.publisher,
            "genres": self.genres,
            "year": self.year,
            "total_issues": self.total_issues,
            "issues": [issue.serialize() for issue in self.issues],
        }
