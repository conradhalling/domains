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
    - adds a User-Agent (Chrome for macOS) to the headers to get responses from
      sites that screen for web scraping
    - uses a timeout of 10 seconds
    - allows redirects

  TO DO
    - Improve the logic to extract the final results.
    - Count the results.
      - How many domains returned a 200 status?
      - How many domains returned a status that was not 200?
      - How many domains had a connection error?
"""

import argparse
import os

import fake_useragent
import requests

def make_request(scheme, subdomain, domain, request_type):
    """
        Use Chrome for macOS as the user agent.
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    """
    ua = fake_useragent.UserAgent(browsers="Chrome", os="Mac OS X", platforms="desktop")
    request_url = scheme + subdomain + domain
    request_method = get_request_method(request_type)
    status_code = None
    status_reason = None
    response_url = None
    exception_name = None
    headers = {"User-Agent": str(ua.chrome) }
    try:
        response = request_method(request_url, headers=headers, allow_redirects=True, timeout=10)
        status_code = response.status_code
        status_reason = response.reason
        response_url = response.url
    except Exception as ex:
        exception_name = type(ex).__name__
    return (request_url, request_type, exception_name, status_code, status_reason, response_url)

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
        help="file containing domains to request",
        required=True)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    filename = args.domains_file; 
    # filename = 'data/names/a_science.sorted.txt'
    # filename = 'data/names/test_domains.txt'
    with open(filename, 'r') as f:
        for line in f:
            domain = line.strip()
            print(domain)

            # Yes, yes, I know. I was lazy and repeated the code here.
            # Try with "head".
            (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                make_request("http://", "", domain, "head")
            print(request_type)
            print(request_url)
            if exception_name is not None:
                print(exception_name)
            else:
                print(status_code, status_reason)
                print(response_url)
            print(flush=True)

            # On status_code 405, try again with "get".
            if status_code == 405:
                (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                    make_request("http://", "", domain, "get")
                print(request_type)
                print(request_url)
                if exception_name is not None:
                    print(exception_name)
                else:
                    print(status_code, status_reason)
                    print(response_url)
                print(flush=True)

            # Try again with "www".
            if exception_name is not None or status_code != 200:
                (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                    make_request("http://", "www.", domain, "head")
                print(request_type)
                print(request_url)
                if exception_name is not None:
                    print(exception_name)
                else:
                    print(status_code, status_reason)
                    print(response_url)
                print(flush=True)

                # On status_code 405, try again with "get".
                if status_code == 405:
                    (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                        make_request("http://", "www.", domain, "get")
                    print(request_type)
                    print(request_url)
                    if exception_name is not None:
                        print(exception_name)
                    else:
                        print(status_code, status_reason)
                        print(response_url)
                    print(flush=True)

            # Try again with https://.
            if exception_name is not None or status_code != 200:
                (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                    make_request("https://", "", domain, "head")
                print(request_type)
                print(request_url)
                if exception_name is not None:
                    print(exception_name)
                else:
                    print(status_code, status_reason)
                    print(response_url)
                print(flush=True)

                # On status_code 405, try again with "get".
                if status_code == 405:
                    (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                        make_request("https://", "", domain, "get")
                    print(request_type)
                    print(request_url)
                    if exception_name is not None:
                        print(exception_name)
                    else:
                        print(status_code, status_reason)
                        print(response_url)
                    print(flush=True)

            # Try again with https:// and www.
            if exception_name is not None or status_code != 200:
                (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                    make_request("https://", "www.", domain, "head")
                print(request_type)
                print(request_url)
                if exception_name is not None:
                    print(exception_name)
                else:
                    print(status_code, status_reason)
                    print(response_url)
                print(flush=True)

                # On status_code 405, try again with "get".
                if status_code == 405:
                    (request_url, request_type, exception_name, status_code, status_reason, response_url) =\
                        make_request("https://", "www.", domain, "get")
                    print(request_type)
                    print(request_url)
                    if exception_name is not None:
                        print(exception_name)
                    else:
                        print(status_code, status_reason)
                        print(response_url)
                    print(flush=True)

if __name__ == "__main__":
    main()
