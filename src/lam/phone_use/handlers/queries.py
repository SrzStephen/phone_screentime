from ..helpers import query_between
from ..models.queries import GenericQueryRequest
from pydantic import ValidationError
from os import environ
from json import dumps
import math


def sankey(event, context):
    fallback_phone_id = environ.get("DEFAULT_PHONE_ID", None)
    try:
        e = GenericQueryRequest(**event)
    except ValidationError as ve:
        return dict(statusCode=400, body=ve.json())
    qs = e.queryStringParameters

    if qs.phone_id is None and fallback_phone_id is None:
        return dict(statusCode=500, body="No Phone ID to fall back to")
    if qs.phone_id is None:
        qs.phone_id = fallback_phone_id

    data = query_between(
        qs.phone_id, qs.start_time, qs.stop_time, attributes=["epoch", "screen_state"]
    )
    on_time = [x.screen_state for x in data]
    time_response = dict(
        total_time=math.ceil((qs.stop_time - qs.start_time) / 120)
        * 120,  # prevent negatives from being possible
        on_time=sum(on_time) * 120,
        off_time=on_time.count(0) * 120,
    )
    time_response["unknown_time"] = (
        time_response["total_time"]
        - time_response["on_time"]
        - time_response["off_time"]
    )
    return dict(statusCode=200, body=dumps(time_response))
