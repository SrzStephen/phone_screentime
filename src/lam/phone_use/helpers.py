from .models.dynamo import DynamoModel
from typing import List, Optional, TypedDict
from os import environ


class TotalTime(TypedDict):
    unknown: int
    active: int
    inactive: int


def query_between(
    phone_id: str, time_start: int, time_stop: int, attributes: Optional[List[str]]
) -> List[DynamoModel]:
    query_params = dict(
        hash_key=phone_id,
        range_key_condition=DynamoModel.epoch.between(time_start, time_stop),
    )
    if query_params:
        query_params["attributes_to_get"] = attributes

    return sorted(
        [r for r in DynamoModel.query(**query_params)],
        key=lambda x: x.epoch,
        reverse=False,
    )


def time_from_query(
    datapoints: List[DynamoModel],
    time_start: int,
    time_stop: int,
    dp_time=environ.get("TIME_BETWEEN_DPS", 120),
    tolerance=environ.get("TIME_TOLERANCE", 15),
) -> TotalTime:
    def add_state(value: int, state: bool, state_dict: TotalTime) -> None:
        if state:
            state_dict["active"] += value
        else:
            state_dict["inactive"] += value

    # mostly useful for sankey diagram, essentially the assumption is there will be 120s+-15s between data points
    # if it calls outside that time then it's unknown
    if datapoints.__len__() == 0:
        return TotalTime(active=0, inactive=0, unknown=time_stop - time_start)

    time_dict = TotalTime(
        active=0,
        inactive=0,
        # start off with unknowable edge time
        unknown=(datapoints[0].epoch - time_start),
    )

    for index, point in enumerate(datapoints):
        point: DynamoModel
        try:
            # datapoints[index+1]
            time_interval = datapoints[index + 1].epoch - point.epoch
            if (dp_time + tolerance) > time_interval > (dp_time - tolerance):
                add_state(time_interval, point.screen_state, time_dict)
            else:
                time_dict["unknown"] += time_interval
        except IndexError:
            pass

    # Final DP calculation
    # Stop time: Take either dp_time
    time_to_stop = time_stop - datapoints[-1].epoch
    if time_to_stop > dp_time:
        time_dict["unknown"] += time_to_stop - dp_time
        add_state(dp_time, datapoints[-1].screen_state, time_dict)
    else:
        add_state(time_to_stop, datapoints[-1].screen_state, time_dict)
    return time_dict
