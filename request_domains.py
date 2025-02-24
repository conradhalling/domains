"""
    Iterate through domain names in the input file.
    Send an HTTP request to each domain and record the response.

    For a domain, e.g. "example.science", make a request to the following URLS:
        http://example.science
        http://www.example.science
        https://example.science
        https://www.example.science
    using HEAD first, then GET when HEAD returns a 405 status code.

    Each request:
        -   adds a User-Agent (Chrome for macOS) to the headers to get responses
            from sites that screen for web scraping
        -   uses a timeout of 10 seconds
        -   allows redirects

    EXAMPLES
        python3 request_domains.py --help
        python3 request_domains.py data/names/a_science.txt --csv_file a_science.csv
        python3 request_domains.py data/names/test_domains.txt --csv_file test_domains.csv

    TO DO
        -   Improve the logic to extract the final results.
        -   Count the results.
            -   How many domains returned a 200 status?
            -   How many domains returned a status that was not 200?
            -   How many domains had a connection error?
"""

import argparse
import csv
import dataclasses
import os
import sys

import fake_useragent
import requests

@dataclasses.dataclass
class DomainResponse:
    domain: str
    request_url: str
    request_type: str
    exception_name: str
    status_code: int
    status_reason: str
    response_url: str

    def print_domain_response(self, file):
        """
            file is sys.stdout or sys.stderr.
        """
        print(self.domain, file=file)
        print(self.request_type, file=file)
        print(self.request_url, file=file)
        if self.exception_name is not None:
            print(self.exception_name, file=file)
        else:
            print(self.status_code, self.status_reason, file=file)
            print(self.response_url, file=file)
        print(flush=True, file=file)

def make_request(scheme, subdomain, domain, request_type):
    """
        Use Chrome for macOS as the user agent.
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    """
    ua = fake_useragent.UserAgent(browsers="Chrome", os="Mac OS X", platforms="desktop")
    request_url = scheme + subdomain + domain
    request_method = get_request_method(request_type)
    headers = {"User-Agent": str(ua.chrome) }
    status_code = None
    status_reason = None
    response_url = None
    exception_name = None
    try:
        response = request_method(request_url, headers=headers, allow_redirects=True, timeout=10)
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

def get_request_method(request_type):
    if request_type == "head":
        return requests.head
    elif request_type == "get":
        return requests.get
    else:
        raise ValueError("Invalid request type: {}".format(request_type))

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Send an HTTP request to each domain and record the response",
        epilog=f"Example:\n  {os.path.basename(__file__)} --domains_file data/names/a_science.txt > a_science.out.txt"
    )
    parser.add_argument(
        "--domains_file",
        help="input file containing domains to request",
        required=True)
    parser.add_argument(
        "--csv_file",
        help="output file for writing results",
        required=True)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    domains_file = args.domains_file
    csv_file = args.csv_file

    # Initialize counters.
    total_domains = 0
    total_200_status = 0
    total_other_status = 0
    total_exceptions = 0

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

        # Open the input file and iterate line by line, writing the
        # results to the CSV output file.
        with open(domains_file, 'r') as domains_f:
            for line in domains_f:
                domain = line.strip()

                # Make an http request to the domain.
                domain_response = make_request("http://", "", domain, "head")
                domain_response.print_domain_response(sys.stderr)

                # On status_code 405, try again with "get".
                if domain_response.status_code == 405:
                    domain_response = make_request("http://", "", domain, "get")
                    domain_response.print_domain_response(sys.stderr)

                # If the response was an exception or a status code other than 200,
                # make an http request to the www subdomain.
                if domain_response.exception_name is not None or domain_response.status_code != 200:
                    new_domain_response = make_request("http://", "www.", domain, "head")
                    new_domain_response.print_domain_response(sys.stderr)

                    # On status_code 405, try again with "get".
                    if new_domain_response.status_code == 405:
                        new_domain_response = make_request("http://", "www.", domain, "get")
                        new_domain_response.print_domain_response(sys.stderr)
                    
                    # Keep the new reponse if it return status code 200.
                    if new_domain_response.status_code == 200:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url
                    
                    # Keep the new response if it returned a status code and the old
                    # response contained an exception.
                    if domain_response.status_code is None and new_domain_response.status_code is not None:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url

                # If the response was an exception or a status code other than 200,
                # make an https request to the domain.
                if domain_response.exception_name is not None or domain_response.status_code != 200:
                    new_domain_response = make_request("https://", "", domain, "head")
                    new_domain_response.print_domain_response(sys.stderr)

                    # On status_code 405, try again with "get".
                    if new_domain_response.status_code == 405:
                        new_domain_response = make_request("https://", "", domain, "get")
                        new_domain_response.print_domain_response(sys.stderr)
                    
                    # Keep the new reponse if it return status code 200.
                    if new_domain_response.status_code == 200:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url
                    
                    # Keep the new response if it returned a status code and the old
                    # response contained an exception.
                    if domain_response.status_code is None and new_domain_response.status_code is not None:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url

                # If the response was an exception or a status code other than 200,
                # make an https request to the www subdomain.
                # Try again with https:// and www.
                if domain_response.exception_name is not None or domain_response.status_code != 200:
                    new_domain_response = make_request("https://", "www.", domain, "head")
                    new_domain_response.print_domain_response(sys.stderr)

                    # On status_code 405, try again with "get".
                    if new_domain_response.status_code == 405:
                        new_domain_response = make_request("https://", "www.", domain, "get")
                        new_domain_response.print_domain_response(sys.stderr)

                    # Keep the new reponse if it return status code 200.
                    if new_domain_response.status_code == 200:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url
                    
                    # Keep the new response if it returned a status code and the old
                    # response contained an exception.
                    if domain_response.status_code is None and new_domain_response.status_code is not None:
                        domain_response.domain = new_domain_response.domain
                        domain_response.request_url = new_domain_response.request_url
                        domain_response.request_type = new_domain_response.request_type
                        domain_response.exception_name = new_domain_response.exception_name
                        domain_response.status_code = new_domain_response.status_code
                        domain_response.status_reason = new_domain_response.status_reason
                        domain_response.response_url = new_domain_response.response_url
                
                print("final response", file=sys.stderr)
                domain_response.print_domain_response(sys.stderr)

                # Increment the appropriate counter.
                total_domains += 1
                if domain_response.status_code == 200:
                    total_200_status += 1
                elif domain_response.status_code is not None:
                    total_other_status += 1
                else:
                    total_exceptions += 1

                # Write the output to the CSV file.
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
    # Report totals.
    print(f"total_domains: {total_domains}")
    print(f"total_200_status: {total_200_status}")
    print(f"total_other_status: {total_other_status}")
    print(f"total_exceptions: {total_exceptions}")

if __name__ == "__main__":
    main()
