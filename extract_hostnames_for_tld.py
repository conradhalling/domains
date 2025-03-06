r"""
DESCRIPTION

Scan cdx-nnnnn.gz files and extract the distinct hostnames for a given TLD,
count the number of pages for each hostname.  Sort the results in descending
order by the page_count value. Extract the domain from the hostname value. Write
the hostname, domain, and page_count values to a CSV output file.

To find the cdx-nnnnn.gz files containing the URLs for the desired TLD, scan
the cluster.idx file. For data set 2024-51, the URLs for .science were in
cdx-00278.gz.

EXAMPLES

python3 extract_hostnames_for_tld.py \
    --tld           .science \
    --cdx_file      data/cc/2024-51/cdx-00278.gz \
    --out_file      data/cc/2024-51/hostnames-science.csv \
    --log_file      logs/extract_hostnames_for_tld.log \
    --log_level     debug

python3 extract_hostnames_for_tld.py \
    --tld           .info \
    --cdx_file      data/cc/2025-05/cdx-00200.gz \
    --cdx_file      data/cc/2025-05/cdx-00201.gz \
    --cdx-file      data/cc/2025-05/cdx-00202.gz \
    --out_file      data/cc/2025-05/hostnames-info.csv \
    --log_file      logs/extract_hostnames_for_tld.log \
    --log_level     debug
"""

import argparse
import collections
import csv
import gzip
import logging
import os
import re
import textwrap

logger = logging.getLogger(__name__)


def extract_domain_from_hostname(hostname):
    dot_count = hostname.count(".")
    domain = hostname
    while domain.count(".") > 1:
        domain = domain[domain.index(".") + 1:]
    return domain


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
        description="Extract domains from a Common Crawl cdx file",
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --tld        .science \
            --cdx_file   data/cc/2025-08/cdx-00278.gz \
            --out_file   data/cc/2025-08/hostnames-science.csv \
            --log_file   logs/extract_hostnames_for_tld.log \
            --log_level  info""")
    )
    parser.add_argument(
        "--tld",
        help="TLD for hostnames to extract",
        required=True
    )
    parser.add_argument(
        "--cdx_file",
        help="Common Crawl compressed cdx file",
        required=True,
        action="append",
    )
    parser.add_argument(
        "--out_file",
        help="output csv file",
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


def process_file(filename, pattern):
    # tld is ".info", ".science", etc.
    hostnames_dict = collections.defaultdict(int)
    with gzip.open(filename, 'rb') as f:
        for line in f:
            match = re.search(pattern, line.decode())
            if match is not None:
                hostnames_dict[match.group(1)] += 1
    return hostnames_dict


def main():
    args = parse_args()
    init_logging(log_file=args.log_file, log_level=args.log_level)
    logger.info(__file__ + " started")
    total_hostnames_dict = dict()
    tld = args.tld
    # For my purposes, a URL ends with ":", "/", or "?", or exhausts the string,
    # which is terminated with '"'.
    pattern = "{}\"url\": \"https?://([^:?/\"]+?\\{})[:?/\"]".format("{", tld)
    logger.debug(f"pattern: {pattern}")
    for cdx_file in args.cdx_file:
        logger.info(f"  Processing {cdx_file}...")
        hostnames_dict = process_file(filename=cdx_file, pattern=pattern)
        total_hostnames_dict.update(hostnames_dict)
        logger.info("    Done.")
    sorted_by_values = dict(sorted(total_hostnames_dict.items(), key=lambda item: item[1], reverse=True))
    with open(args.out_file, "w") as out_f:
        csv_writer = csv.writer(out_f)
        csv_writer.writerow(["hostname", "domain", "page_count"])
        for hostname, page_count in sorted_by_values.items():
            domain = extract_domain_from_hostname(hostname)
            csv_writer.writerow([hostname, domain, page_count])
    logger.info(__file__ + " finished")


if __name__ == "__main__":
    main()
