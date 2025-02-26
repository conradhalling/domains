"""
DESCRIPTION
    Read the output CSV file and create an HTML file with
    the data in a table with links.

EXAMPLES
    python3 create_html_table.py --help

    python3 create_html_table.py
        --csv_file      data/output/a_science.csv \
        --html_file     data/output/a_science.html \
        --log_level     info
"""

import argparse
import csv
import dataclasses
import logging
import os
import textwrap

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DomainResponse:
    domain: str
    request_url: str
    request_type: str
    exception_name: str
    status_code: int
    status_reason: str
    response_url: str


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
        description="Send an HTTP request to each domain and record the response",
        epilog=f"Example:\n  python3 {os.path.basename(__file__)} --domains_file data/names/a_science.txt > a_science.out.txt"
    )
    parser.add_argument(
        "--csv_file",
        help="input file for reading data",
        required=True,
    )
    parser.add_argument(
        "--html_file",
        help="output file containing HTML table",
        required=True,
    )
    parser.add_argument(
        "--log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="logging level, one of debug, info, warning, error, critical",
        required=True,
    )
    args = parser.parse_args()
    return args


def process_csv_data(args):
    with open(args.html_file, "w") as html_file:
        start_html(html_file)
        with open(args.csv_file, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            # Skip the header line.
            row = next(csv_reader)
            # Process the data lines.
            for row in csv_reader:
                (domain, request_url, request_type, exception_name, status_code, status_reason, response_url) = row
                print('        <tr class="adaptive">', file=html_file)
                print(f'          <td class="adaptive">{domain}</td>', file=html_file)
                print(f'          <td class="adaptive"><a class="adaptive" href="{request_url}" target="_blank">{request_url}</td>', file=html_file)
                print(f'          <td class="adaptive">{request_type}</td>', file=html_file)
                if exception_name != "":
                    print(f'          <td class="adaptive">{exception_name}</td>', file=html_file)
                else:
                    print('          <td class="adaptive"></td>', file=html_file)
                if status_code != "":
                    print(f'          <td class="adaptive">{status_code}</td>', file=html_file)
                else:
                    print('          <td class="adaptive"></td>', file=html_file)
                if status_reason != "":
                    print(f'          <td class="adaptive">{status_reason}</td>', file=html_file)
                else:
                    print('          <td class="adaptive"></td>', file=html_file)
                if response_url != "":
                    print(f'          <td class="adaptive"><a class="adaptive" href="{response_url}" target="_blank">{response_url}</td>', file=html_file)
                else:
                    print('          <td class="adaptive"></td>', file=html_file)
                print('        </tr>', file=html_file)
        finish_html(html_file)


def start_html(html_file):
    html_start = """\
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Domains</title>
        <style>
          caption {
            text-align: left;
            font-family: Verdana;
          }
          
          table {
            table-layout: fixed;
            border-collapse: collapse;
            border: 3px solid #cccccc;
          }

          thead tr {
            background-color: #dddddd;
          }
          
          tbody tr:nth-child(odd) {
            background-color: #ffffff;
          }

          tbody tr:nth-child(even) {
            background-color: #eeeeee;
          }

          th, td {
            border: 1px solid #cccccc;
            font-family: Verdana;
            font-size: 0.625rem;
            padding: 2px 3px;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 15rem;
          }

          @media (prefers-color-scheme: dark) {
            :root {
              background-color: #111111;
              color: #ffffff;
            }

            table.adaptive {
              border: 3px solid #444444;
            }
            
            thead tr.adaptive {
              background-color: #333333;
            }

            tbody tr:nth-child(odd).adaptive {
              background-color: #111111;
            }

            tbody tr:nth-child(even).adaptive {
              background-color: #1c1c1c;
            }

            th.adaptive,
            td.adaptive {
              border: 1px solid #444444;
            }

            a.adaptive {
              color: #9999ff;
            }

            a:visited.adaptive {
              color: #cda9ef;
            }
          }
        </style>
      </head>

      <body>
        <table class="adaptive">
          <caption>Domains from the .science TLD starting with "a"</caption>
          <thead>
            <tr class="adaptive">
              <th class="adaptive">domain</th>
              <th class="adaptive">request_url</th>
              <th class="adaptive">request_type</th>
              <th class="adaptive">exception_name</th>
              <th class="adaptive">status_code</th>
              <th class="adaptive">status_reason</th>
              <th class="adaptive">response_url</th>
            </tr>
          </thead>
          <tbody>"""
    print(textwrap.dedent(html_start), file=html_file)


def finish_html(html_file):
    html_finish = """\
          </tbody>
        </table>
      </body>
    </html>
    """
    print(textwrap.dedent(html_finish), file=html_file)


def main():
    args = parse_args()
    init_logging(args)
    logger.info(__file__ + ' started')
    # Process the CSV file and write the HTML file.
    process_csv_data(args)
    logger.info(__file__ + ' finished')


if __name__ == "__main__":
    main()
