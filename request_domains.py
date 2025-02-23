"""
Read data/names/domain-names-science.txt. Call HEAD on each domain.

For a domain, domain.science, attempt the following requests:
    http://example.science
    http://www.example.science
    https://example.science
    https://www.example.science
using HEAD, then GET on a 405 status code.

The script gets more responses when it adds a User-Agent to the headers.

To do:
    Improve the logic to extract the final results.
    How many domains returned a 200 status?
    How many domains returned a status that was not 200?
    How many domains had a connection error?
"""

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
        response = request_method(request_url, headers=headers, allow_redirects=True, timeout=5)
        status_code = response.status_code
        status_reason = response.reason
        reason = response.reason
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
    
filename = 'data/names/domain-names-science-sorted.txt'
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
