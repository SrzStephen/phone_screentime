from json import load

from src.lam.phone_use.handlers.file import lambda_handler, write_series
from src.lam.phone_use.models.file import BaseRequest
from src.lam.phone_use.models.dynamo import DynamoModel
from pydantic import ValidationError
import pytest
from random import randrange
from . import dynamo_table, create_table_with_data

from tests.unit import test_path


def envs():
    return dict(
        AWS_REGION="ap-southeast-2", DYNAMO_TABLE=f"TestTable-{randrange(999, 9999)}"
    )


def test_schema_works(test_file: dict):
    br = BaseRequest(**test_file)
    assert len(br.body.split("\n")) > 0
    assert len(BaseRequest.to_body_format(br.body)) > 0


def test_schema_fails_too_many(test_file: dict):
    test_file["body"] = "1,2,3,off,4,5\n"
    with pytest.raises(ValidationError):
        BaseRequest(**test_file)


# This can't be a fixture due to some annoying stuff with pytest:(
def create_db():
    DynamoModel.create_table(read_capacity_units=1, write_capacity_units=1)


def test_insert(test_obj, dynamo_table):
    write_series(test_obj)
    results = [x for x in DynamoModel.scan()]
    assert len(results) == 3
    for r in results:
        assert isinstance(r.epoch, int)
        assert isinstance(r.screen_state, bool)


def test_lambda_handler(test_file, create_table_with_data):
    ret = lambda_handler(test_file, "")
    assert ret["statusCode"] == 200


def test_lambda_handler_2(test_file, create_table_with_data):
    test_file["body"] = "1,2,3,off,4,5\n"
    ret = lambda_handler(test_file, "")
    assert ret["statusCode"] == 400


@pytest.fixture(scope="function")
def test_obj(test_file) -> BaseRequest:
    return BaseRequest(**test_file)


@pytest.fixture(scope="function")  # in case something tries to mutate state
def test_file() -> dict:
    with open(test_path / "test_data/file_test.json") as fp:
        yield load(fp)
