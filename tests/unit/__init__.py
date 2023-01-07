from pathlib import Path
from random import choice

from _pytest.fixtures import fixture
from moto import mock_dynamodb
from datetime import datetime
from src.lam.phone_use.models.dynamo import DynamoModel

test_path = Path(__file__).parent

test_phone_id = "aaaa"
test_time = datetime.now()
test_time_int = int(test_time.timestamp())
time_range_bucket = 120
time_intervals = 200
time_range = [
    test_time_int - x
    for x in range(0, time_range_bucket * time_intervals, time_range_bucket)
]


@fixture(scope="function")
def dynamo_table() -> DynamoModel:
    with mock_dynamodb():
        DynamoModel.create_table(read_capacity_units=1, write_capacity_units=1)
        assert DynamoModel.exists()
        yield DynamoModel


@fixture(scope="function")
def create_table_with_data(dynamo_table) -> None:
    with mock_dynamodb():
        DynamoModel.create_table(read_capacity_units=1, write_capacity_units=1)

        with DynamoModel.batch_write() as batch:
            for t in range(0, time_range_bucket * time_intervals, time_range_bucket):
                data = dict(
                    phone_id=test_phone_id,
                    epoch=test_time_int - t,
                    uptime=t,
                    battery=10,
                    screen_state=choice([0, 1]),
                )
                batch.save(DynamoModel(**data))
        yield
