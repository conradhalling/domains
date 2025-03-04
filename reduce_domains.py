r"""
DESCRIPTION

Reduce a domain like shs.hal.science to hal.science to build a list
of primary domains found in the Common Crawl data.

EXAMPLE

python3 reduce_comains.py \
    --input_file    data/2025-05/names/domains-info.4.txt \
    --output_file   data/2025-05/output/reduced-domains-info.txt
"""

import argparse
import collections
import os
import textwrap

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Reduce domains from multiple to two fields",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --input_file   data/names/domains-info.4.txt \\
            --output_file  data/output/reduced-domains-info.txt
        """
        )
    )
    parser.add_argument(
        "--input_file",
        help="input text file containing domains and counts",
        required=True,
    )
    parser.add_argument(
        "--output_file",
        help="output text file containing reduced domains",
        required=True,
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    domains_dict = collections.defaultdict(int)
    with open(args.output_file, "w") as out_f:
        with open(args.input_file, "r") as in_f:
            for data_line in in_f:
                (domain, _) = data_line.split()
                # print(domain, file=out_f)
                dot_count = domain.count(".")
                if dot_count == 1:
                    domains_dict[domain] += 1
                else:
                    while domain.count(".") > 1:
                        domain = domain[domain.index(".") + 1:]
                    domains_dict[domain] += 1
        domains_list = list(domains_dict.keys())
        domains_list.sort()
        for domain in domains_list:
            print(domain, file=out_f)


if __name__ == "__main__":
    main()
