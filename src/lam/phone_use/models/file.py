from pydantic import BaseModel, validator
from typing import Literal, List

from src.lam.phone_use.models.test_file import RequiredHeaders


class BodyFormat(BaseModel):
    epoch: int
    uptime: int
    battery: int
    screen_state: Literal["on", "off"]


class BaseRequest(BaseModel):
    httpMethod: Literal["POST"]
    headers: RequiredHeaders
    body: str
    isBase64Encoded: Literal[False]

    @staticmethod
    def to_body_format(body: str) -> List[BodyFormat]:

        return [
            BodyFormat(epoch=x[0], uptime=x[1], battery=x[2], screen_state=x[3],)
            for x in [line.split(",") for line in body.split("\n") if line != ""]
        ]

    @validator("body")
    def body_formatted_correctly(cls, v):
        for line in v.split("\n"):
            if line != "":
                val = line.split(",")
                if not len(val) == len(BodyFormat.__fields__):
                    raise ValueError(
                        f"Didn't get expected number of fields from {line}. Expected {BodyFormat.__fields__.keys()}"
                    )
                # Check that each line meets my meta format
        cls.to_body_format(v)
        return v

    @validator("User_Agent", check_fields=False)
    def user_agent_is_tasker(cls, v):
        if not v.startswith("Tasker"):
            raise ValueError("User agent appears to not have come from tasker.")
