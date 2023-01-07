from ..models.file import BaseRequest
from ..models.dynamo import DynamoModel
from pydantic import ValidationError
from logging import getLogger

logger = getLogger(__name__)


def write_series(event: BaseRequest):
    with DynamoModel.batch_write() as batch:
        for line in BaseRequest.to_body_format(event.body):
            line.screen_state = 1 if line.screen_state == "on" else 0
            line_dict = line.dict()
            line_dict["phone_id"] = event.headers.Device_Model
            batch.save(DynamoModel(**line_dict))


def lambda_handler(event, context):
    try:
        input_event = BaseRequest(**event)
    except ValidationError as ve:
        logger.info(ve.errors())
        return dict(statusCode=400, body=ve.json())
    write_series(input_event)
    return dict(statusCode=200, body="success")
