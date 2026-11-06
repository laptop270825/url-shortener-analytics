from pydantic import BaseModel, ConfigDict,HttpUrl
from datetime import datetime

class URLCreate(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str

class ClickInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clicked_at: datetime
    user_agent: str | None = None
    referrer: str | None = None


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    recent_clicks: list[ClickInfo]