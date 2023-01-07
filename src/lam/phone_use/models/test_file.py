from pydantic import BaseModel, Field


class RequiredHeaders(BaseModel):
    Device_Model: str = Field(alias="Device-Model")
    Password: str
    User_Agent: str = Field(alias="User-Agent")
