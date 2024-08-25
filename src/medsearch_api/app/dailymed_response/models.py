from datetime import date, datetime
from dateutil import parser
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class SPLListItemResponse(BaseModel):
    """Represents a single SPL (Structured Product Label) entry in JSON format."""

    set_id: str = Field(alias="setid")
    spl_version: int
    title: str
    published_date: date

    @field_validator("published_date", mode="before")
    def parse_published_date(cls, value):
        """Convert the published_date string to a date object."""
        if isinstance(value, str):
            return parser.parse(value).date()
        return value

    @field_validator("set_id", "title", mode="before")
    def remove_leading_and_trailing_spaces(cls, value):
        """Strips leading and trailing spaces from set_id and title."""
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("set_id", "title", mode="before")
    def convert_empty_string_to_none(cls, value):
        """Converts empty strings to None for set_id and title."""
        if value == "":
            return None
        return value


class SPLListMetadata(BaseModel):
    """Metadata for the SPL list response."""

    db_published_date: datetime
    elements_per_page: int
    next_page_url: Optional[str]
    total_pages: int
    total_elements: int
    current_url: str
    next_page: Optional[int]
    previous_page: Optional[int]
    previous_page_url: Optional[str]
    current_page: int

    @field_validator("*", mode="before")
    def convert_string_null_to_none(cls, value):
        """Converts 'null' strings or None values to None for all fields."""
        if isinstance(value, str) and value.strip().lower() == "null":
            return None
        return value

    @field_validator("db_published_date", mode="before")
    def parse_db_published_date(cls, value):
        """Convert the db_published_date string to a datetime object."""
        if isinstance(value, str):
            return parser.parse(value)
        return value

    @field_validator("next_page_url", "previous_page_url", mode="before")
    def convert_empty_string_to_none(cls, value):
        """Converts empty strings to for optional str fields."""
        if value == "":
            return None
        return value


class SPLListResponse(BaseModel):
    """Represents a response containing a list of SPL (Structured Product Label) entries."""

    metadata: SPLListMetadata
    data: List[SPLListItemResponse]

    @property
    def has_more_pages(self) -> bool:
        """Checks if there are more pages of results available."""
        return self.metadata.current_page < self.metadata.total_pages


class SPLDetailModel(BaseModel):
    med_code: Optional[str]
    med_code_system: Optional[str]
    med_name: Optional[str]
    med_effective_date: Optional[str]
    med_version_number: Optional[str]
    med_generic_name: Optional[str]
    med_form_name: Optional[str]
    med_form_code: Optional[str]
    med_form_code_system: Optional[str]
    org_name: Optional[str]
    org_id_extension: Optional[str]
    org_id_root: Optional[str]
