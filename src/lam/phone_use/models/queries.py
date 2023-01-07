from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class GenericTimeQueryParams(BaseModel):
    phone_id: Optional[str]
    start_time: int
    stop_time: int


class GenericQueryRequest(BaseModel):
    queryStringParameters: GenericTimeQueryParams


class HeatmapQueryParams(BaseModel):
    phone_id: Optional[str]
    start_time: int
    stop_time: int
    scale: Literal["linear", "logarithmic", "raw"]


class HeatmapQueryRequest(BaseModel):
    queryStringParameters: HeatmapQueryParams
