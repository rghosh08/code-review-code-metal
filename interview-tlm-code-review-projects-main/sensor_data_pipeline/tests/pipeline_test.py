import pytest
from unittest.mock import patch
from pathlib import Path
import io
import yaml
from hamcrest import assert_that, equal_to, has_length, instance_of, calling, raises

from sensor_pipeline import pipeline
from sensor_pipeline import operators


# Helper function to mock a yaml file read from a string
def load_test_pipeline_helper(yaml_str: str):
    with patch.object(Path, "open") as mock_open:
        mock_open.return_value = io.StringIO(yaml_str)

        patched_path = Path("test_pipeline.yaml")
        return pipeline.load(patched_path)


def test_valid_pipeline_parsed():

    test_pipeline_yaml = """
- operator:
    name: "Convert from UTC to EST"
    class: ConvertTimezone
    input_field: a_field
    output_field: another_field
    tz: "America/New_York"
"""

    test_pipeline = load_test_pipeline_helper(test_pipeline_yaml)

    assert_that(test_pipeline, has_length(1))

    name, op = test_pipeline[0]
    assert_that(name, equal_to("Convert from UTC to EST"))
    assert_that(op, instance_of(operators.ConvertTimezone))


def test_valid_pipeline_with_two_ops_parsed():

    test_pipeline_yaml = """
- operator:
    name: "Convert Celcius to Fahrenheit"
    class: ConvertTemperatureCToF
    input_field: temperature_c
    output_field: temperature_f

- operator:
    name: "Group by mesh_id"
    class: GroupBy
    key_field: mesh_id
"""

    test_pipeline = load_test_pipeline_helper(test_pipeline_yaml)

    assert_that(test_pipeline, has_length(2))

    # Extract out just the operators.
    ops = [op for _, op in test_pipeline]
    assert_that(ops[0], instance_of(operators.ConvertTemperatureCToF))
    assert_that(ops[1], instance_of(operators.GroupBy))


def test_invalid_pipeline_yaml_raises():

    test_pipeline_yaml = """
    A@!#0asd() <- invalid
- operator:
    name: "Convert Celcius to Fahrenheit"
    class: ConvertTemperatureCToF
    input_field: temperature_c
    output_field: temperature_f
"""

    assert_that(
        calling(load_test_pipeline_helper).with_args(test_pipeline_yaml),
        raises(yaml.YAMLError),
    )


def test_invalid_pipeline_op_raises():

    test_pipeline_yaml = """
- operator:
    name: "No such operator"
    class: DoesNotExist
    input_field: something
    output_field: something_else
"""

    assert_that(
        calling(load_test_pipeline_helper).with_args(test_pipeline_yaml),
        raises(AttributeError),
    )
