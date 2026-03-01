#! /usr/env python

import sys
import json
import yaml
from pathlib import Path
from typing import Iterator
import logging

import sensor_pipeline.operators as operators

logger = logging.getLogger(__name__)

Record = dict[str, any]
Operator = tuple[str, any]


def load(pipeline_file: Path) -> list[Operator]:
    """
    Reads a pipeline definition file and builds the pipeline.

    Args:
        pipeline_file (Path): The pipeline yaml file.

    Returns:
        list[Operator]: A list of Operator (tuple of name, operator class).

    Raises:
        AttributeError: If the named operator class could not be found.
    """

    with pipeline_file.open("rb") as f:
        pipeline_desc = yaml.load(f, Loader=yaml.Loader)

    def build_op(opdef: dict[str, any]):
        # Properties that live outside the operator object.
        class_name = opdef.pop("class")
        op_name = opdef.pop("name")

        # Get the cls object from the module by name.
        op_cls = getattr(operators, class_name)

        # Instantiates the operator class with its configuration.
        return (op_name, op_cls(**opdef))

    # Result is an array of dictionaries with an operator key.abs
    # Transform into the operator configs:
    return [build_op(op_dict["operator"]) for op_dict in pipeline_desc]


def run(records: Iterator[Record], ops) -> Iterator[Record]:
    """
    Run a pipeline on a set of input records (dictionaries).

    Args:
        records: Iterator over input records to process.

    Returns:
        Iterator(Record): Iterator over processed records.
    """
    # Runs the pipeline. Each operator takes a sequence
    # of records and returns a new sequence.
    for name, op in ops:
        logger.info("Running %s", name)
        records = op.run(records)

    return records
