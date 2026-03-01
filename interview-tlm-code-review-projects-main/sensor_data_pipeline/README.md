# Sensor data pipeline

This project implements a data processing pipeline for sensor data.

## Installation

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment: `. ./venv/bin/activate`
3. Intall the package and dependencies: `pip install '.[dev]'`

Note: the dev dependencies are needed only for running tests.

This should install dependencies for runtime and testing and add
a command called `sensor_pipeline` to your path.

## Running the tests

Tests are implemented in the `./tests` directory and can be
run (from an activated venv) by running:

```
pytest
```

The test suite is not covering every operator but demonstrates
testing some of them. In the interest of time I omitted a few
but the others are simple to add and would follow the same pattern.

With more time... For operators there probably should be tests that
cover malformed operators and test error handling.

## Running the pipeline

The sensor_pipeline command has the following interface:

```
usage: sensor_pipeline [-h] -i INPUT [-o OUTPUT] pipeline

positional arguments:
  pipeline              The pipeline yaml definition file to run.

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     The input data file.
  -o, --output OUTPUT   The output file
```

A pipeline is described in a .yaml file and the program includes a
pipeline definition matching the specifications in the assignment.
It is possible to define alternative pipeline behavior by editing or
writing pipeline definitions in yaml.

To run the pipeline (from the root project directory)

```
sensor_pipeline pipeline.toml --input data/sensor_data.json
```

This will output the transformed data (as json) to stdout. Alternatively,
output can be written to a file via:

```
sensor_pipeline pipeline.toml --input data/sensor_data.json --output result.json
```

## Design

The pipeline is defined in a yaml file as a sequence of "operators". Each operator
has a name, operator class and operator specific configuration parameters.

A pipeline is dynamically composed by parsing this file and producing a list of
(name, operator) pairs. The name is for debugging or observability to track which
step the pipeline is performing.

Instantiating each operator requires dynamically finding its class from the `operators`
module. Therefor the class must be available in the top level `operators` namespace.
The pipeline.load function reads each operator config, finds the class, and passes
the rest of the configuration values to the class constructor.

Each operator has a single entrypoint called `run` that accepts an iterator or sequence
of records. The run method outputs a sequence of transformed records.

### Some possible refinements

- Operators are dataclasses which leverage instantation from a dictionary and some validation
that all required parameters are present. But post instantiation an operator could do
some additional validation. One option here would be to switch from dataclasses to [Pydantic](https://docs.pydantic.dev/) models.

- Operators have an expect data shape, especially downstream from a 
[GroupBy](src/sensor_pipeline/operators/group_by.py). This is not expressed
in the interface. At a minimum a `run` method could do error handling on the input.

- Some operators (and json.load) collect all of the input data into an in memory array. For larger
scale data we would need to consider how to stream records through the pipeline. The tricky
operator here is GroupBy which needs to know that it has seen all possible mesh_id values. This
could be handled by collecting the groups on different nodes.

- Implement logging with different verbosity levels.

## Testing

Unit tests can be run via `pytest` from the project root directory. The tests are not exaustive
but show examples of running tests on the pipeline builder and on some of the operators. In
the interest of time I did not implement tests for every operator but they would follow
the same pattern.

## Extensibility

It is relatively easy to define new operators. The process is:
1.  Create a new file in the operators directory
2. Implement the operator as a dataclass (to serialize it's
attributes easily from a dict)
3. Implement the `run` method following the same interface (record iterator in/out)
4. Add the import to the [`__init__.py`](src/operators/__init__.py) file.

One consideration is that operators can change the shape of the data so there are some ordering
dependencies. For example, Aggregate assumes it is receiving the output of GroupBy
which is currently hard coded to collect the grouped records into a "records" property.
This could be made a config variable if needed.

In general operators are designed to be flexible. For example it would be possible
to change the behavior of the ConvertTimezone operator to use a different time zone
and output field name.
