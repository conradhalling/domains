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

NOTES
    I copied the background color and link colors for dark mode from the Mozilla
    Developer Network dark theme.
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
        description="Convert a domains CSV file to an HTML file",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --csv_file   data/output/a_science.csv \\
            --html_file  data/output/a_science.html \\
            --log_file   logs/create_html_table.log \\
            --log_level  info""")
    )
    parser.add_argument(
        "--csv_file",
        help="input CSV file",
        required=True,
    )
    parser.add_argument(
        "--html_file",
        help="output HTML file",
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


def process_csv_data(csv_file, html_file):
    with open(html_file, "w") as html_f:
        start_html(html_f)
        with open(csv_file, "r") as csv_f:
            csv_reader = csv.reader(csv_f)
            # Skip the header line.
            row = next(csv_reader)
            # Process the data lines.
            for row in csv_reader:
                (domain, request_url, request_type, exception_name, status_code, status_reason, response_url) = row
                print('        <tr class="adaptive">', file=html_f)
                print(f'          <td class="adaptive">{domain}</td>', file=html_f)
                print(f'          <td class="adaptive"><a class="adaptive" href="{request_url}" target="_blank">{request_url}</td>', file=html_f)
                print(f'          <td class="adaptive">{request_type}</td>', file=html_f)
                print(f'          <td class="adaptive">{exception_name}</td>', file=html_f)
                print(f'          <td class="adaptive">{status_code}</td>', file=html_f)
                print(f'          <td class="adaptive">{status_reason}</td>', file=html_f)
                if response_url != "":
                    print(f'          <td class="adaptive"><a class="adaptive" href="{response_url}" target="_blank">{response_url}</td>', file=html_f)
                else:
                    print('          <td class="adaptive"></td>', file=html_f)
                print('        </tr>', file=html_f)
        finish_html(html_f)


def start_html(html_f):
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
            border: 3px solid #bfbfbf;
          }

          thead tr {
            background-color: #d9d9d9;
          }
          
          tbody tr:nth-child(odd) {
            background-color: #e6e6e6;
          }

          tbody tr:nth-child(even) {
            background-color: #d9d9d9;
          }

          th, td {
            border: 1px solid #bfbfbf;
            font-family: Verdana;
            font-size: 0.625rem;
            padding: 2px 3px;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 15rem;
          }

          @media (prefers-color-scheme: dark) {
            :root {
              background-color: #1a1a1a;
              color: #ffffff;
            }

            table.adaptive {
              border: 3px solid #404040;
            }
            
            thead tr.adaptive {
              background-color: #333333;
            }

            tbody tr:nth-child(odd).adaptive {
              background-color: #1a1a1a;
            }

            tbody tr:nth-child(even).adaptive {
              background-color: #262626;
            }

            th.adaptive,
            td.adaptive {
              border: 1px solid #404040;
            }

            a.adaptive {
              color: rgb(140, 180, 255);
            }

            a:visited.adaptive {
              color: rgb(255, 173, 255);
            }
          }
        </style>
      </head>

      <body>
        <table class="adaptive">
          <caption>Domains from the .science TLD</caption>
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
    print(textwrap.dedent(html_start), file=html_f)


def finish_html(html_f):
    html_finish = """\
          </tbody>
        </table>
      </body>
    </html>
    """
    print(textwrap.dedent(html_finish), file=html_f)


def main():
    args = parse_args()
    init_logging(args.log_file, args.log_level)
    logger.info(__file__ + ' started')
    process_csv_data(args.csv_file, args.html_file)
    logger.info(__file__ + ' finished')


if __name__ == "__main__":
    main()
