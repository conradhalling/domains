"""
DESCRIPTION
    Find active internet domains by iterating through domain names from the
    input file, sending one or more HTTP(S) requests to the domain, and
    recording the best response.

    For a domain, e.g. "example.science", make a request to the following URLS:
        http://example.science
        http://www.example.science
        https://example.science
        https://www.example.science
    using a HEAD request first, then a GET request if the HEAD request returns
    a 405 status code, iterating through the URLs until the returned status
    code is 200 OK or the URLs are exhausted.

    Each request adds a User-Agent (Chrome for macOS) to the headers (to get
    a response from a site that screens for web scraping), uses a timeout of
    10 seconds, and allows redirects.

    The earliest HTTP 200 response is recorded for the domain. Otherwise, a
    response containing a status code is preferred over a failed connection.
        
    For each domain, one result is written to the CSV output file, which
    contains the following columns:
        domain          the input domain (e.g., "example.science")
        request_url     the URL (e.g., "http://example.science") to which
                        the request was made
        request_type    the type of HTTP request used ("head" or "get")
        exception_name  the name of the exception raised if no connection
                        could be made (ConnectionError, ConnectionTimeout,
                        ReadTimeout, or SSLError)
        status_code     the HTTP status code from the response (e.g., 200)
        status_reason   the HTTP status code reason from the response
                        (e.g., "OK")
        response_url    the URL from the response after redirects (e.g.,
                        "https://www.example.science/")

    The script logs the total counts for:
        -   domains
        -   200 status codes
        -   combined other status codes
        -   combined exceptions

    The script writes a log file named check_domains.log to the working
    directory. The logging level must be set to one of the following: debug,
    info, warning, error, or critical.
    
EXAMPLES
    python3 check_domains.py --help

    # Process some domains from the .science TLD.
    python3 check_domains.py \
        --domains_file  data/names/a_science.txt \
        --csv_file      data/output/a_science.csv \
        --log_level     info

    # Test with 11 domains from the .science TLD.
    python3 check_domains.py \
        --domains_file  data/names/test_domains.txt \
        --csv_file      data/output/test_domains.csv \
        --log_level     info

NOTES
    This script provides examples of using the following packages: argparse,
    csv, dataclasses, logging, os.path, fake_useragent, and requests.
"""

import argparse
import csv
import dataclasses
import logging
import os
import textwrap

import fake_useragent
import requests

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Counters:
    total_domains: int = 0
    total_200_status: int = 0
    total_other_status: int = 0
    total_exceptions: int = 0

    def increment(self, status_code):
        self.total_domains += 1
        if status_code == 200:
            self.total_200_status += 1
        elif status_code is not None:
            self.total_other_status += 1
        else:
            self.total_exceptions += 1

    def log(self):
        logger.info("total_domains: {}".format(self.total_domains))
        logger.info("total_200_status: {}".format(self.total_200_status))
        logger.info("total_other_status: {}".format(self.total_other_status))
        logger.info("total_exceptions: {}".format(self.total_exceptions))


@dataclasses.dataclass
class DomainResponse:
    domain: str
    request_url: str
    request_type: str
    exception_name: str
    status_code: int
    status_reason: str
    response_url: str

    def log(self):
        logger.info(self.domain)
        logger.info(self.request_type)
        logger.info(self.request_url)
        if self.exception_name is not None:
            logger.info(self.exception_name)
        else:
            logger.info(self.status_code)
            logger.info(self.status_reason)
            logger.info(self.response_url)
        logger.info("")
    
    def update_from(self, other_domain_response):
        self.domain = other_domain_response.domain
        self.request_url = other_domain_response.request_url
        self.request_type = other_domain_response.request_type
        self.exception_name = other_domain_response.exception_name
        self.status_code = other_domain_response.status_code
        self.status_reason = other_domain_response.status_reason
        self.response_url = other_domain_response.response_url


def get_domain_response(domain):
    # Make an http request to the domain.
    domain_response = make_request("http://", "", domain, "head")
    domain_response.log()

    # On status_code 405, try again with "get".
    if domain_response.status_code == 405:
        domain_response = make_request("http://", "", domain, "get")
        domain_response.log()

    # If the response was an exception or a status code other than 200,
    # make an http request to the www subdomain.
    if domain_response.exception_name is not None or domain_response.status_code != 200:
        new_domain_response = make_request("http://", "www.", domain, "head")
        new_domain_response.log()

        # On status_code 405, try again with "get".
        if new_domain_response.status_code == 405:
            new_domain_response = make_request("http://", "www.", domain, "get")
            new_domain_response.log()
        
        # Keep the new reponse if it returned status code 200.
        if new_domain_response.status_code == 200:
            domain_response.update_from(new_domain_response)
        
        # Keep the new response if it returned a status code and the old
        # response contained an exception.
        if domain_response.status_code is None and new_domain_response.status_code is not None:
            domain_response.update_from(new_domain_response)

    # If the response was an exception or a status code other than 200,
    # make an https request to the domain.
    if domain_response.exception_name is not None or domain_response.status_code != 200:
        new_domain_response = make_request("https://", "", domain, "head")
        new_domain_response.log()

        # On status_code 405, try again with "get".
        if new_domain_response.status_code == 405:
            new_domain_response = make_request("https://", "", domain, "get")
            new_domain_response.log()
        
        # Keep the new reponse if it returned status code 200.
        if new_domain_response.status_code == 200:
            domain_response.update_from(new_domain_response)
        
        # Keep the new response if it returned a status code and the old
        # response contained an exception.
        if domain_response.status_code is None and new_domain_response.status_code is not None:
            domain_response.update_from(new_domain_response)

    # If the response was an exception or a status code other than 200,
    # make an https request to the www subdomain.
    # Try again with https:// and www.
    if domain_response.exception_name is not None or domain_response.status_code != 200:
        new_domain_response = make_request("https://", "www.", domain, "head")
        new_domain_response.log()

        # On status_code 405, try again with "get".
        if new_domain_response.status_code == 405:
            new_domain_response = make_request("https://", "www.", domain, "get")
            new_domain_response.log()

        # Keep the new reponse if it returned status code 200.
        if new_domain_response.status_code == 200:
            domain_response.update_from(new_domain_response)
        
        # Keep the new response if it returned a status code and the old
        # response contained an exception.
        if domain_response.status_code is None and new_domain_response.status_code is not None:
            domain_response.update_from(new_domain_response)
    
    logger.info("final response")
    domain_response.log()
    return domain_response


def get_request_method(request_type):
    if request_type == "head":
        return requests.head
    elif request_type == "get":
        return requests.get
    else:
        raise ValueError("Invalid request type: {}".format(request_type))


def init_logging(args):
    logfilename = os.path.basename(os.path.splitext(__file__)[0]) + '.log'
    logging_numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(logging_numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(
        filename=logfilename,
        encoding='utf-8',
        level=logging_numeric_level)


def make_request(scheme, subdomain, domain, request_type):
    """
        Use Chrome for macOS as the user agent.
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    """
    ua = fake_useragent.UserAgent(
        browsers="Chrome", os="Mac OS X", platforms="desktop")
    request_url = scheme + subdomain + domain
    request_method = get_request_method(request_type)
    headers = {"User-Agent": str(ua.chrome) }
    status_code = None
    status_reason = None
    response_url = None
    exception_name = None
    try:
        response = request_method(
            request_url, headers=headers, allow_redirects=True, timeout=10)
        status_code = response.status_code
        status_reason = response.reason
        response_url = response.url
    except Exception as ex:
        exception_name = type(ex).__name__
    domain_response = DomainResponse(
        domain=domain,
        request_url=request_url,
        request_type=request_type,
        exception_name=exception_name,
        status_code=status_code,
        status_reason=status_reason,
        response_url=response_url)
    return domain_response


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Send an HTTP request to each domain website and record the response",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --domains_file  data/names/a_science.txt \\
            --csv_file      data/output/a_science.csv \\
            --log_level     info""")
    )
    parser.add_argument(
        "--domains_file",
        help="input file containing domains to check",
        required=True,
    )
    parser.add_argument(
        "--csv_file",
        help="output file for writing results",
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


def process_data(args):
    domains_file = args.domains_file
    csv_file = args.csv_file
    counters = Counters()

    # Initialize the csv output file as a text file with a header line.
    with open(csv_file, "w") as csv_f:
        csv_writer = csv.writer(csv_f)
        csv_writer.writerow(
            [
                "domain",
                "request_url",
                "request_type",
                "exception_name",
                "status_code",
                "status_reason",
                "response_url",
            ]
        )

        # Open the input file and iterate through the domains line by line.
        # Get the response for each domain (logging at the INFO level).
        # Write the response to the CSV output file.
        # Log the totals.
        with open(domains_file, 'r') as domains_f:
            for line in domains_f:
                domain = line.strip()
                domain_response = get_domain_response(domain)
                counters.increment(domain_response.status_code)
                csv_writer.writerow(
                    [
                        domain_response.domain,
                        domain_response.request_url,
                        domain_response.request_type,
                        domain_response.exception_name,
                        domain_response.status_code,
                        domain_response.status_reason,
                        domain_response.response_url,
                    ]
                )
    return counters


def main():
    args = parse_args()
    init_logging(args)
    logger.info(__file__ + ' started')
    # Process the data and write the response data to the CSV file.
    counters = process_data(args)
    counters.log()
    logger.info(__file__ + ' finished')


if __name__ == "__main__":
    main()
