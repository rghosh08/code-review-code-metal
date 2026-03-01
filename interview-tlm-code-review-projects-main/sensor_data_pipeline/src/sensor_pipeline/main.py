import sys
import json
import yaml
from pathlib import Path
from argparse import ArgumentParser
import logging

import sensor_pipeline.pipeline as pipeline


def setup_logging():

    # Set root logger to log to stderr
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def fatal_error(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(-1)


def main():

    setup_logging()

    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "pipeline", type=Path, help="The pipeline yaml definition file to run."
    )
    arg_parser.add_argument(
        "-i", "--input", type=Path, help="The input data file.", required=True
    )
    arg_parser.add_argument(
        "-o", "--output", type=Path, help="The output file", required=False
    )

    args = arg_parser.parse_args()

    # Validate input.
    if not args.pipeline.exists():
        fatal_error(f"Error: Pipeline definition {args.pipeline} not found")

    if not args.input.exists():
        fatal_error(f"Error: Input data file {args.input} not found")

    try:
        sensor_pipeline = pipeline.load(args.pipeline)
    except yaml.YAMLError as yaml_err:
        fatal_error(f"Error: parsing pipeline description failed:\n\n{yaml_err}")
    except AttributeError as attr_err:
        fatal_error(f"Error: loading pipline description failed:\n\n{attr_err}")

    logging.info("Loaded pipeline from %s", args.pipeline)

    try:
        with args.input.open("r") as f:
            input_records = json.load(f)
    except json.JSONDecodeError as json_err:
        fatal_error(f"Error: loading input data failed:\n\n{json_err}")

    logging.info("Loaded %d data records from %s", len(input_records), args.input)

    output_records = pipeline.run(input_records, sensor_pipeline)

    # Pipeline returns an iterator over records, but for JSON we need
    # to materialize the whole list (unless we implement streaming JSON)
    output_records = list(output_records)

    logging.info("Pipeline produced %d output records", len(output_records))

    if args.output:
        with open(args.output, "w") as out:
            json.dump(output_records, out, indent=2)
    else:
        json.dump(output_records, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
