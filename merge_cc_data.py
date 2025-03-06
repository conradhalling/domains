r"""
DESCRIPTION

EXAMPLES

python3 merge_cc_data.py -\
    -data_dir       data/cc \
    --data_set      2024-51 \
    --data_set      2025-05 \
    --data_set      2025-08 \
    --in_file       hostnames-science.csv \
    --out_file      data/cc/merged/hostnames-science.merged.csv \
    --log_file      logs/combine_cc_data.log \
    --log_level     info
"""

import argparse
import csv
import logging
import os
import textwrap

logger = logging.getLogger(__name__)


def init_logging(log_file, log_level):
    logging_numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(logging_numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    format = "[%(filename)s:%(lineno)4d - %(funcName)35s() ] %(levelname)s: %(message)s"
    logging.basicConfig(
        filename=log_file,
        encoding='utf-8',
        format=format,
        level=logging_numeric_level)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Merge Common Crawl domain data",
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --data_dir   data/cc \
            --data_set   2024-51 \
            --data_set   2025-05 \
            --data_set   2025-08 \
            --in_file    hostnames-science.csv \
            --csv_file   data/cc/merged/hostnames-science.merged.csv \
            --log_file   logs/merge_cc_data.log \
            --log_level  info"""
        )
    )
    parser.add_argument(
        "--data_dir",
        help="Directory containing Common Crawl data subdirectories",
        required=True,
    )
    parser.add_argument(
        "--data_set",
        help="Subdirectory containing Common Crawl data",
        required=True,
        action="append",
    )
    parser.add_argument(
        "--in_file",
        help="input file for each data set",
        required=True,
    )
    parser.add_argument(
        "--out_file",
        help="output CSV file containing merged data",
        required=True,
    )
    parser.add_argument(
        "--log_file",
        help="output log file",
        required=True,
    )
    parser.add_argument(
        "--log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="logging level",
        required=True,
    )
    args = parser.parse_args()
    return args


def merge_cc_data(data_dir, data_sets, in_file, out_file):
    # Merge the data using a dictionary using a dict, where the values
    # are overwritten for a hostname if the hostname appears in a later data set.
    hostnames_dict = {}
    for data_set in data_sets:
        in_path = os.path.join(data_dir, data_set, in_file)
        logger.debug(f"in_path: {in_path}")
        # The input file is a CSV file with columns hostname, domain, and page_count.
        with open(in_path, "r") as in_f:
            csv_reader = csv.reader(in_f)
            # Skip the header row.
            header_line = next(csv_reader)
            for row in csv_reader:
                (hostname, domain, page_count) = row
                hostnames_dict[hostname] = (hostname, domain, data_set, page_count)
    # Write the merged data to a csv file.
    with open(out_file, "w") as csv_f:
        csv_writer = csv.writer(csv_f)
        csv_writer.writerow(
            [
                "hostname",
                "domain",
                "data_set",
                "page_count",
            ]
        )
        for row in hostnames_dict.values():
            csv_writer.writerow(row)


def main():
    args = parse_args()
    init_logging(log_file=args.log_file, log_level=args.log_level)
    logger.info(__file__ + " started")
    merge_cc_data(data_dir=args.data_dir, data_sets=args.data_set, in_file=args.in_file, out_file=args.out_file)
    logger.info(__file__ + " finished")


if __name__ == "__main__":
    main()
