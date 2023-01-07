from src.lam.phone_use.handlers.file import DynamoModel
from datetime import datetime
from src.lam.phone_use.helpers import query_between, time_from_query
from os import environ
from . import (
    test_time_int,
    test_phone_id,
    time_range_bucket,
    time_intervals,
    create_table_with_data,
    dynamo_table,
)
from freezegun import freeze_time


def test_basic_query(create_table_with_data):
    results = query_between(
        phone_id=test_phone_id,
        time_start=test_time_int - time_range_bucket * time_intervals,
        time_stop=test_time_int,
        attributes=["epoch", "screen_state"],
    )
    for r in results:
        assert r.screen_state in [True, False]
        assert r.epoch in [
            test_time_int - x
            for x in range(0, time_range_bucket * time_intervals, time_range_bucket)
        ]

    assert results[0].epoch < results[-1].epoch  # should be sorted
    assert len(results) == time_intervals


class FakeDBModel:
    epoch: int
    screen_state: bool


def test_totals_no_data():
    query_time = time_from_query([], test_time_int, test_time_int + 120)
    assert query_time["unknown"] == 120
    assert query_time["active"] == 0
    assert query_time["inactive"] == 0


def test_totals_with_gap():
    # Example:
    # Time 0
    # 0 -> 120 is unknown
    # 120 -> 355 is active
    # There's a huge gap between 355 and 600 so this time is unknown (eg: device offline so no data)
    # 600 -> 721 is inactive
    # 721 -> 800 (120 sec env var) is inactive

    times = []
    for time in [120, 245, 355, 600, 721]:
        m = DynamoModel()
        m.epoch = test_time_int + time
        m.screen_state = True
        times.append(m)
    times[-2].screen_state = False
    times[-1].screen_state = False

    active_time = 125 + 110
    off_time = 121

    end_test_time = test_time_int + 800
    query_time = time_from_query(times, test_time_int, end_test_time)
    assert query_time["active"] == active_time
    assert query_time["inactive"] == off_time + (800 - 721)
    assert 800 == query_time["active"] + query_time["inactive"] + query_time["unknown"]

    # Check that the last datapoint works as it should if it goes out of bounds
    # we don't know beyond then so the rest of the time (841 -> 900) is unknown
    end_test_time = test_time_int + 900
    query_time = time_from_query(times, test_time_int, end_test_time)
    assert query_time["inactive"] == off_time + environ.get("TIME_BETWEEN_DPS", 120)
    assert query_time["active"] == active_time
    assert 900 == query_time["active"] + query_time["inactive"] + query_time["unknown"]


def test_totals_single_value():
    m = DynamoModel()
    m.epoch = test_time_int + 60
    m.screen_state = True
    query_time = time_from_query([m], test_time_int, test_time_int + 121)
    assert query_time["unknown"] == 60
    assert query_time["active"] == 61
    assert query_time["inactive"] == 0
