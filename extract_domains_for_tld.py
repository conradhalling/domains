r"""
DESCRIPTION

Extract the distinct domains for a given TLD and sort the values in reverse order
by the number of hits.

This requires looking at the cdx-nnnnn.gz files, which are sorted alphabetically
by TLD, to find the files containing the TLD you're interested in. Or you could
download all the files (230 GB of .gz files) and process them all.

EXAMPLES

python3 extract_domains_for_tld.py \
    --tld           .science \
    --cdx_file      data/2025-08/cdx/cdx-00278.gz \
    --out_file      data/2025-08/names/domains-science.txt \
    --log_file      logs/extract_domains_for_tld.log \
    --log_level     debug

    python3 extract_domains_for_tld.py \
    --tld           .info \
    --cdx_file      data/2025-05/cdx/cdx-00200.gz \
    --cdx_file      data/2025-05/cdx/cdx-00201.gz \
    --cdx-file      data/2025-05/cdx/cdx-00202.gz \
    --out_file      data/2025-05/names/domains-info.txt \
    --log_file      logs/extract_domains_for_tld.log \
    --log_level     debug
"""

import argparse
import collections
import gzip
import logging
import os
import re
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
        description="Extract domains from a Common Crawl cdx file",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --tld        .science \\
            --cdx_file   data/2025-08/cdx/cdx-00278.gz \\
            --out_file   data/2025-08/names/domains-science.txt \\
            --log_file   logs/extract_domains.log \\
            --log_level  info""")
    )
    parser.add_argument(
        "--tld",
        help="TLD for domains to extract",
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
        help="output text file",
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
    domains_dict = collections.defaultdict(int)
    with gzip.open(filename, 'rb') as f:
        for line in f:
            match = re.search(pattern, line.decode())
            if match is not None:
                match_string = match.group(1)
                domains_dict[match.group(1)] += 1
    return domains_dict


def main():
    args = parse_args()
    init_logging(log_file=args.log_file, log_level=args.log_level)
    logger.info(__file__ + " started")
    total_dict = dict()
    tld = args.tld
    # For my purposes, a URL ends with ":", "/", or "?", or exhausts the string,
    # which is terminated with '"'.
    pattern = "{}\"url\": \"https?://([^:?/\"]+?\\{})[:?/\"]".format("{", tld)
    logger.debug(f"pattern: {pattern}")
    for cdx_file in args.cdx_file:
        logger.info(f"  Processing {cdx_file}...")
        file_dict = process_file(filename=cdx_file, pattern=pattern)
        total_dict.update(file_dict)
        logger.info("    Done.")
    sorted_by_values = dict(sorted(total_dict.items(), key=lambda item: item[1], reverse=True))
    with open(args.out_file, "w") as out_f:
        for key, value in sorted_by_values.items():
            print("{} {}".format(key, value), file=out_f)
    logger.info(__file__ + " finished")


if __name__ == "__main__":
    main()
