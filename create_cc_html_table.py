r"""
DESCRIPTION

Read the Common Crawl CSV file for checked domains and create an HTML file with
the data in a table with links.

EXAMPLES

python3 create_cc_html_table.py --help

python3 create_cc_html_table.py
    --csv_file      data/cc/merged/domains-science.merged.checked.csv \
    --html_file     data/cc/merged/domains-science.merged.checked.html \
    --log_file      logs/create_cc_html_table.log \
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
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --csv_file   data/cc/merged/domains-science.merged.checked.csv \
            --html_file  data/cc/merged/domains-science.merged.checked.html \
            --log_file   logs/create_cc_html_table.log \
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
                (   hostname, domain, data_set, page_count, request_url, 
                    request_type, exception_name, status_code,
                    status_reason, response_url) = row
                print('        <tr class="adaptive">', file=html_f)
                print(f'          <td class="adaptive">{hostname}</td>', file=html_f)
                print(f'          <td class="adaptive">{data_set}</td>', file=html_f)
                print(f'          <td class="adaptive right">{page_count}</td>', file=html_f)
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
        <title>.science Websites</title>
        <style>
          :root {
            font-family: Georgia, serif;
            line-height: 2rem;
            background-color: #f2f2f2;
            color: #000000;
          }

          p {
            max-width: 40rem;
            font-size: larger;
          }
          
          table {
            table-layout: fixed;
            border-collapse: collapse;
            border: 3px solid #bfbfbf;
            line-height: 1rem;
          }

          table > caption {
            text-align: left;
            font-family: Verdana;
          }

          table > thead > tr {
            background-color: #d9d9d9;
          }
          
          tbody > tr:nth-child(odd) {
            background-color: #f2f2f2;
          }

          tbody > tr:nth-child(even) {
            background-color: #e6e6e6;
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

          .right {
            text-align: right;
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
        <h1>Websites in the .science TLD</h1>
        <p>
          Using Python scripts, I obtained these data from the <a
          href="https://commoncrawl.org/" class="adaptive"> Common Crawl</a>
          CC-MAIN-2024-51, CC-MAIN-2025-05, and CC-MAIN-2025-08 data sets. I
          extracted hostnames from the <a href="http://nic.science/"
          class="adaptive">.science TLD</a> records in the cdx-nnnnn.gz files
          from each data set while counting the number of web pages found in the
          crawl for each hostname. The <em>hostname</em> column gives the
          hostname extracted from the Common Crawl data. The <em>data_set</em>
          column indicates the latest data set in which the hostname appeared.
          The <em>page_count</em> column gives the number of website pages
          present in the Common Crawl data.
        </p>

        <p>
          I wrote a Python script that used the Python <a
          href="https://docs.python-requests.org/en/latest/index.html"
          class="adaptive">requests</a> module to send an HTTPS or HTTP request
          allowing redirects to each hostname. The hostnames table presents the
          responses in the <em>exception_name</em>, <em>status_code</em>,
          <em>status_reason</em>, and <em>response_url</em> fields. 
        </p>

        <p>
          The source code is available in my <a
          href="https://github.com/conradhalling/domains/"
          class="adaptive">GitHub repository</a>.
        </p>

        <table class="adaptive">
          <caption><strong>Table 1.</strong> Key to the fields in Table 2</caption>
          <thead>
            <tr class="adaptive">
              <th class="adaptive">Field</th>
              <th class="adaptive">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr class="adaptive">
              <td class="adaptive">hostname</td>
              <td class="adaptive">Hostname from Common Crawl data</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">data_set</td>
              <td class="adaptive">Latest Common Crawl data set in which the hostname appears</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">page_count</td>
              <td class="adaptive">Number of website pages for the hostname in the Common Crawl data set</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">exception_name</td>
              <td class="adaptive">Python requests exception from website response</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">status_code</td>
              <td class="adaptive">HTTP status code returned by website</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">status reason</td>
              <td class="adaptive">HTTP status reason returned by website</td>
            </tr>
            <tr class="adaptive">
              <td class="adaptive">response_url</td>
              <td class="adaptive">URL returned in website response</td>
            </tr>
          </tbody>
        </table>
        <br>
        <table class="adaptive">
          <caption><strong>Table 2.</strong> Hostnames in the .science TLD</caption>
          <thead>
            <tr class="adaptive">
              <th class="adaptive">hostname</th>
              <th class="adaptive">data_set</th>
              <th class="adaptive">page_count</th>
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
