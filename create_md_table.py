"""
DESCRIPTION
    Read the output CSV file and create a Markdown file with the data in a table
    with links.

EXAMPLES
    python3 create_md_table.py --help

    python3 create_md_table.py
        --csv_file      data/output/a_science.csv \
        --md_file       data/output/a_science.md \
        --log_level     info

NOTES
    To reduce the width of the table, this code omits the request_type column
    and the status_reason column, and it truncates the domain and URL strings.
    The full URLs are present in the links.
"""

import argparse
import csv
import logging
import os
import textwrap

logger = logging.getLogger(__name__)


def init_logging(args):
    logfilename = os.path.basename(os.path.splitext(__file__)[0]) + '.log'
    logging_numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(logging_numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(
        filename=logfilename,
        encoding='utf-8',
        level=logging_numeric_level)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert a domains CSV file to a Markdown file",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --csv_file   data/output/a_science.csv \\
            --md_file    data/output/a_science.md \\
            --log_level  info""")
    )
    parser.add_argument(
        "--csv_file",
        help="input CSV file",
        required=True,
    )
    parser.add_argument(
        "--md_file",
        help="output file containing Markdown table",
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


def process_csv_data(args):
    max_url_len = 35 # maximum length of a URL text string
    max_exc_len = 15 # maximum length on an exception string
    with open(args.md_file, "w") as md_file:
        with open(args.csv_file, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            # Process the header line. Override the values to omit the
            # request_url, request_type, and status_reason columns and to
            # shorten some column names.
            row = next(csv_reader)
            row = ['domain', 'exception', 'status', 'response_url']
            print("| ", " | ".join(row), " |", sep='', file=md_file)
            print("|----" * len(row), "|", sep='', file=md_file)
            # Process the data lines.
            for row in csv_reader:
                (domain, request_url, request_type, exception_name, status_code, status_reason, response_url) = row
                if len(domain) > max_url_len:
                    print(f"| {domain[0:max_url_len]}… ", end='', file=md_file)
                else:
                    print(f"| {domain[0:max_url_len]} ", end='', file=md_file)
                # if len(request_url) > max_url_len:
                #     print(f"| [{request_url[0:max_url_len - 1]}…]({request_url}) ", end='', file=md_file)
                # else:
                #     print(f"| [{request_url}]({request_url}) ", end='', file=md_file)                    
                # print(f"| {request_type} ", end='', file=md_file)
                if len(exception_name) > max_exc_len:
                    print(f"| {exception_name[0:max_exc_len - 1]}… ", end='', file=md_file)
                else:
                    print(f"| {exception_name} ", end='', file=md_file)
                print(f"| {status_code} ", end='', file=md_file)
                # print(f"| {status_reason} ", end='', file=md_file)
                if response_url != "":
                    if len(response_url) > max_url_len:
                        print(f"| [{response_url[0:max_url_len - 1]}…]({response_url})", end='', file=md_file)
                    else:
                        print(f"| [{response_url}]({response_url})", end='', file=md_file)
                else:
                    print(f"| {response_url} ", end='', file=md_file)
                print("|", file=md_file)
            print("", file=md_file)


def main():
    args = parse_args()
    init_logging(args)
    logger.info(__file__ + ' started')
    # Process the CSV file and write the Markdown file.
    process_csv_data(args)
    logger.info(__file__ + ' finished')


if __name__ == "__main__":
    main()
