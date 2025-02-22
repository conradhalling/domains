import collections
import gzip
import re
import sys

"""
Extract the distinct domains for a given TLD and sort the values in reverse order
by the number of hits.

This requires looking at the cdx-nnnnn.gz files, which are sorted alphabetically
by TLD, to find the files containing the TLD you're interested in. Or you could
download all the files (230 GB of .gz files) and process them all.
"""

def process_file(filename, tld):
    # tld is ".info", ".science", etc.
    domains_dict = collections.defaultdict(int)
    # For my purposes, a URL ends with ":", "/", or exhausts the string. 
    #   shop2.skinchakra.science?force_sid=lel9iuvcauker6obdb6jh7jklb&ref=greencosmetic.science 1
    #   www.google.sc/url?q=http://yogicentral.science
    pattern = "{}\"url\": \"https?://(.+?\\{}.*?)[:/\"]".format("{", tld)
    with gzip.open(filename, 'rb') as f:
        for line in f:
            match = re.search(pattern, line.decode())
            if match is not None:
                match_string = match.group(1)
                # Omit matches like:
                #   www.info.uni-globe.in
                #   www.info.lootex.io
                #   ww25.info.billionbox.io
                #   maps.google.com.sa/url?q=https://ai-db.science 1
                if "/" not in match_string and "?" not in match_string:
                    if match_string.endswith(tld):
                        domains_dict[match.group(1)] += 1
            # else:
            #     print("No match!\n", line.decode(), "\n", file=sys.stderr)
    return domains_dict

if __name__ == "__main__":
    total_dict = dict()
    # .info
    # tld = ".info"
    # for filename in ('cdx-00200.gz', 'cdx-00201.gz', 'cdx-00202.gz'):
    tld = ".science"
    for filename in ('cdx-00278.gz',):
        print("  Processing {}...".format(filename), file=sys.stderr)
        file_dict = process_file(filename=filename, tld=tld)
        total_dict.update(file_dict)
        print("    Done.", file=sys.stderr)
    sorted_by_values = dict(sorted(total_dict.items(), key=lambda item: item[1], reverse=True))
    for key, value in sorted_by_values.items():
        print("{} {}".format(key, value))
