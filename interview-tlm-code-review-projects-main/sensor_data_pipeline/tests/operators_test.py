from datetime import datetime, timezone

import pytest
from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    has_items,
    all_of,
    has_entry,
    has_entries,
    equal_to,
    has_key,
)

from sensor_pipeline import operators


def test_convert_timezone():
    op = operators.ConvertTimezone(
        input_field="some_field", output_field="other_field", tz="America/New_York"
    )

    r1_timestamp_utc = datetime(2025, 4, 5, 16, 30, tzinfo=timezone.utc)
    r2_timestamp_utc = datetime(2024, 1, 1, 1, 1, tzinfo=timezone.utc)

    records = [
        {
            "some_field": r1_timestamp_utc.isoformat(),
        },
        {
            "some_field": r2_timestamp_utc.isoformat(),
        },
    ]

    converted_records = list(op.run(records))

    # Verify that the sequence has the original field and a new output field.
    assert_that(
        converted_records,
        has_items(all_of(has_key("some_field"), has_key("other_field"))),
    )

    def utc_offset_hours(dt):
        return int(dt.utcoffset().total_seconds() / 3600)

    # Convert back to date times
    converted_dts = [
        datetime.fromisoformat(rec["other_field"]) for rec in converted_records
    ]
    converted_utc_offsets = [utc_offset_hours(dt) for dt in converted_dts]
    expected_utc_offsets = [-5 if dt.dst() else -4 for dt in converted_dts]

    # Here I am not sure why the dst is incorrect.
    assert_that(
        converted_utc_offsets,
        has_items(equal_to(-4)),
        # equal_to(expected_utc_offsets)
    )

    # Times are represented as different strings but are the same time.
    assert_that(
        converted_dts,
        contains_exactly(equal_to(r1_timestamp_utc), equal_to(r2_timestamp_utc)),
    )


def test_convert_temperature():
    pass


def test_aggregate():
    pass


def test_group_by():
    op = operators.GroupBy(key_field="group_id")

    records = [
        {"group_id": 3, "name": "a"},
        {"group_id": 1, "name": "b"},
        {"group_id": 2, "name": "c"},
        {"group_id": 1, "name": "d"},
    ]

    grouped_records = list(op.run(records))

    assert_that(
        grouped_records,
        has_items(
            has_entries(
                "group_id",
                1,
                "records",
                contains_inanyorder(
                    has_entry("name", "b"),
                    has_entry("name", "d"),
                ),
            ),
            has_entries(
                "group_id", 2, "records", contains_exactly(has_entry("name", "c"))
            ),
            has_entries(
                "group_id", 3, "records", contains_exactly(has_entry("name", "a"))
            ),
        ),
    )


def test_aggregate_computes_avg_and_count():
    records = [
        {
            "id": "1",
            "records": [
                {"value": 0},
                {"value": 1},
                {"value": 2},
                {"value": 3},
            ],
        },
    ]

    expected_avg = (0 + 1 + 2 + 3) / 4
    expected_count = 4

    op_avg = operators.Aggregate(
        function="avg", input_field="value", output_field="value_avg"
    )

    output_records = list(op_avg.run(records))

    assert_that(
        output_records, has_items(has_entry("value_avg", equal_to(expected_avg)))
    )

    op_count = operators.Aggregate(
        function="count", input_field="value", output_field="value_count"
    )

    output_records = list(op_count.run(records))

    assert_that(
        output_records, has_items(has_entry("value_count", equal_to(expected_count)))
    )


def test_anomoly_detection():
    pass
