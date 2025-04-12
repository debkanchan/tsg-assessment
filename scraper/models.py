from datetime import datetime
from pydantic import BaseModel, Field

class Media(BaseModel, frozen=True):
	"""
	Represents a media object.
	"""
	title: str
	url: str
	date: datetime
	source_type: str = Field("video")

class ScrapeResult(BaseModel, arbitrary_types_allowed=True):
	"""
	Represents the result of a scrape operation.
	"""
	base_url: str
	medias: list[Media] = Field(default_factory=list)
	error: Exception | None = Field(default=None)	
