import math

import pytest
from src.lam.phone_use.handlers.queries import sankey
from json import load, loads
from . import test_path, create_table_with_data, dynamo_table, test_time, test_phone_id
from os import environ
from src.lam.phone_use.models.dynamo import DynamoModel
from datetime import datetime, timedelta
from freezegun import freeze_time
from typing import List


@pytest.fixture(scope="function")  # in case something tries to mutate state
def sankey_query_template() -> dict:
    with open(test_path / "test_data/sankey_query_request.json") as fp:
        yield load(fp)


@pytest.mark.parametrize("query_length", [1, 70, 121])
def test_sankey_no_data(sankey_query_template: dict, dynamo_table, query_length: int):
    # Query should work and clamp to the max resolution that i've got (120s)
    time_between_dps = environ.get("TIME_BETWEEN_DPS", 120)
    assert time_between_dps != 0
    query_data = sankey_query_template["queryStringParameters"]
    sankey_query_template["queryStringParameters"]["stop_time"] = str(
        int(query_data["start_time"]) + query_length
    )
    sankey_response = sankey(sankey_query_template, None)
    assert sankey_response["statusCode"] == 200
    data = loads(sankey_response["body"])
    assert data["unknown_time"] == math.ceil(query_length / 120) * time_between_dps
    assert data["total_time"] == math.ceil(query_length / 120) * time_between_dps
    assert data["on_time"] == 0
    assert data["off_time"] == 0


dummy_data_last_time = 900


@pytest.fixture(scope="function")
def dummy_data(dynamo_table, sankey_query_template: dict) -> List[dict]:
    return [
        dict(
            epoch=int((test_time + timedelta(seconds=time)).timestamp()),
            screen_state=True,
            uptime=1,
            battery=10,
            phone_id=sankey_query_template["queryStringParameters"]["phone_id"],
        )
        for time in range(5, dummy_data_last_time, 120)
    ]


@freeze_time(time_to_freeze=test_time)
def test_sankey_all_active(
    sankey_query_template: dict, dummy_data, dynamo_table: DynamoModel
):
    with DynamoModel.batch_write() as batch:
        [batch.save(DynamoModel(**data)) for data in dummy_data]
    assert len([x for x in DynamoModel().scan()]) == len(dummy_data)
    query_data = sankey_query_template["queryStringParameters"]
    query_data["start_time"] = int(test_time.timestamp())
    query_data["stop_time"] = int(test_time.timestamp()) + dummy_data_last_time
    sankey_response = sankey(sankey_query_template, None)
    assert sankey_response["statusCode"] == 200
    response = loads(sankey_response["body"])
    num_on_times = int(math.floor(dummy_data_last_time / 120))
    raise NotImplementedError("TODO")
