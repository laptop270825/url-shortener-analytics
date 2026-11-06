from pydantic import BaseModel, ConfigDict,HttpUrl

class URLCreate(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str