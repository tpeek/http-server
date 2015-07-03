#!/usr/bin/env python
import pytest
import socket
from http_server import response_ok, response_error, parse_request, resolve_uri


@pytest.fixture()
def make_client():
    ADDR = ("127.0.0.1", 8000)
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.connect(ADDR)
    return client


def helper(client, msg):
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
    print proto
    code = req[0][1]+" "+req[0][2]
    headers = {}
    for line in req[1:]:
        headers[line[0].upper()] = line[1:]
    d = {'code': code, 'proto': proto, 'headers': headers}
    d.update(headers)
    return d


def test_client1(make_client):
    client = make_client
    assert "HTTP/1.1 200 OK" in helper(client, "GET ./.. HTTP/1.1\r\nHOST: www.site.com\r\n\r\n")


def test_response_ok():
    response_dict = parse_helper(response_ok("text/html", "<html></html>"))
    assert "HTTP/1.1" == response_dict['proto']
    assert "200 OK" == response_dict['code']
    assert "CONTENT-TYPE:" in response_dict
    assert "text/html" == response_dict["CONTENT-TYPE:"][0]
    assert "CONTENT-LENGTH:" in response_dict


def test_response_error():
    assert "HTTP/1.1 500 Internal Server Error" in response_error()
    assert "HTTP/1.1 400 Bad Request" in response_error(SyntaxError("400 Bad Request"))


def test_parse_request():
    #  parse_request returns the resource requested.
    assert "/path/templates/thing.html" == parse_request("GET /path/templates/thing.html HTTP/1.1\r\nHOST: www.site.com\r\n\r\n<html>stuff</html>")
    #  Bad Method
    with pytest.raises(ValueError):
        parse_request("POST /path/thing.html HTTP/1.1\r\nHOST: www.site.com")
    #  Bad request
    with pytest.raises(SyntaxError):
        parse_request("asdfasdF")
    #  Bad HTTP Version
    with pytest.raises(SyntaxError):
        parse_request("GET /path/templates/thing.html HTTP/1.0\r\nHOST: www.aol.com\r\n\r\n<html>stuff</html>")
    #  No Host
    with pytest.raises(SyntaxError):
        parse_request("GET /path/templates/thing.html HTTP/1.0\r\n")


def test_security():
    with pytest.raises(UserWarning):
        resolve_uri("./../../../")


def test_resolve_uri():
    uri = parse_request("GET ./ HTTP/1.1\r\nHOST: www.site.com\r\n\r\n<html>stuff</html>")
    assert "text/html" in resolve_uri(uri)
    with pytest.raises(IOError):
        resolve_uri("~")
    with pytest.raises(IOError):
        resolve_uri("./cat.gif")
