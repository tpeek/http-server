#!/usr/bin/env python
import pytest
import socket
from http_server import response_ok, response_error, parse_request, resolve_uri


#
#  Fixtures
#
@pytest.fixture()
def make_client():
    ADDR = ("127.0.0.1", 8000)
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.connect(ADDR)
    return client


#
#  Helper functions
#
def client_helper(client, msg):
    client.sendall(msg)
    client.shutdown(socket.SHUT_WR)
    response = ""
    while True:
        part = client.recv(16)
        response += part
        if len(part) < 16:
            client.close()
            return response


def parse_helper(request):
    request = request.split("\r\n\r\n", 1)
    req = request[0].split("\r\n")
    for i, r in enumerate(req):
        req[i] = r.split()
    proto = req[0][0]
    code = " ".join(req[0][1:])
    body = request[-1]
    headers = {}
    for line in req[1:]:
        headers[line[0].upper()] = line[1]
    d = {'code': code, 'proto': proto, 'body': body}
    d.update(headers)
    return d


def get_parsed_response_helper(request):
    client = make_client()
    response = client_helper(client, request)
    response = parse_helper(response)
    return response


#
#  Unit Tests
#
def test_response_ok():
    response_dict = parse_helper(response_ok("text/html", "<html></html>"))
    assert "HTTP/1.1" == response_dict['proto']
    assert "200 OK" == response_dict['code']
    assert "CONTENT-TYPE:" in response_dict
    assert "text/html" == response_dict["CONTENT-TYPE:"]
    assert "CONTENT-LENGTH:" in response_dict


def test_response_error():
    assert "HTTP/1.1 500 Internal Server Error" in response_error()
    err = "HTTP/1.1 400 Bad Request"
    assert err in response_error(SyntaxError("400 Bad Request"))


def test_parse_request():
    #  parse_request returns the resource requested.
    uri = "/path/templates/thing.html"
    assert uri == parse_request("GET /path/templates/thing.html HTTP/1.1\r\n"
                                "HOST: www.site.com\r\n\r\n"
                                "<html>stuff</html>")
    #  Bad Method
    with pytest.raises(ValueError):
        parse_request("POST /path/thing.html HTTP/1.1\r\nHOST: www.site.com")
    #  Bad request
    with pytest.raises(SyntaxError):
        parse_request("asdfasdF")
    #  Bad HTTP Version
    with pytest.raises(SyntaxError):
        parse_request("GET /path/templates/thing.html HTTP/1.0\r\n"
                      "HOST: www.aol.com\r\n\r\n"
                      "<html>stuff</html>")
    #  No Host
    with pytest.raises(SyntaxError):
        parse_request("GET /path/templates/thing.html HTTP/1.0\r\n")


def test_resolve_uri():
    uri = parse_request("GET ./ HTTP/1.1\r\n"
                        "HOST: www.site.com\r\n\r\n"
                        "<html>stuff</html>")
    assert "text/html" in resolve_uri(uri)
    with pytest.raises(IOError):
        resolve_uri("~")
    with pytest.raises(IOError):
        resolve_uri("./cat.gif")


def test_security():
    with pytest.raises(UserWarning):
        resolve_uri("./../../../")


#
#  Functional Tests
#
def test_server_response_dir():
    request = "GET . HTTP/1.1\r\nHOST: www.site.com\r\n\r\n"
    response = get_parsed_response_helper(request)
    assert "HTTP/1.1 200 OK" == response['proto'] + " " + response["code"]
    assert response["CONTENT-TYPE:"] == 'text/html'
    assert 'Directory' in response['body']


def test_server_response_picture():
    request = "GET images/sample_1.png HTTP/1.1\r\nHOST: www.cewing.us\r\n\r\n"
    response = get_parsed_response_helper(request)
    assert "HTTP/1.1 200 OK" == response['proto'] + " " + response["code"]
    assert response["CONTENT-TYPE:"] == 'image/png'


def test_server_response_text():
    request = "GET sample.txt HTTP/1.1\r\nHOST: www.cewing.us\r\n\r\n"
    response = get_parsed_response_helper(request)
    assert "HTTP/1.1 200 OK" == response['proto'] + " " + response["code"]
    assert response["CONTENT-TYPE:"] == 'text/plain'
    assert ("This is a very simple text file.\n"
            "Just to show that we can server it up.\n"
            "It is three lines long.") in response["body"]


def test_server_response_python():
    request = "GET make_time.py HTTP/1.1\r\nHOST: www.cewing.us\r\n\r\n"
    response = get_parsed_response_helper(request)
    assert "HTTP/1.1 200 OK" == response['proto'] + " " + response["code"]
    assert response["CONTENT-TYPE:"] == 'text/x-python'
    assert ("simple script that returns and HTML page with the current time"
            in response['body'])


def test_server_bad_method():
    request = "POST /path/thing.html HTTP/1.1\r\nHOST: www.site.com"
    response = get_parsed_response_helper(request)
    assert ('HTTP/1.1 405 Method Not Allowed' ==
            response['proto'] + " " + response["code"])


def test_server_bad_request():
    request = "This is totally not a valid HTTP request, dude."
    response = get_parsed_response_helper(request)
    assert ('HTTP/1.1 400 Bad Request' ==
            response['proto'] + " " + response["code"])


def test_server_bad_http():
    request = "GET . HTTP/1.0\r\nHOST: www.whalesrus.com"
    response = get_parsed_response_helper(request)
    assert ('HTTP/1.1 400 Bad Request' ==
            response['proto'] + " " + response["code"])


def test_server_no_host():
    request = "GET . HTTP/1.0\r\n"
    response = get_parsed_response_helper(request)
    assert ('HTTP/1.1 400 Bad Request' ==
            response['proto'] + " " + response["code"])
