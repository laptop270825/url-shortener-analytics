from pydantic import BaseModel, ConfigDict

class URLCreate(BaseModel):
    url: str

class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str