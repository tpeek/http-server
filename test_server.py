#!/usr/bin/env python

import pytest
from urllib2 import HTTPError
import socket
from http_server import response_ok, response_error, parse_request


@pytest.fixture()
def make_client():
    ADDR = ("127.0.0.1", 8000)
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.connect(ADDR)
    return client


def helper(client, msg):
    try:
        client.sendall(msg)
        client.shutdown(socket.SHUT_WR)
        response = ""
        while True:
            part = client.recv(16)
            response += part
            if len(part) < 16:
                client.close()
                return response
    except Exception as e:
        print e


def test_client1(make_client):
    client = make_client
    assert "HTTP/1.1 200 OK" in helper(client, "What I put here does not matter")


def test_response_ok():
    assert "HTTP/1.1 200 OK" in response_ok()


def test_response_error():
    assert "HTTP/1.1 500 Internal Server Error" in response_error()

def test_parse_request():
    assert "/path/templates/thing.html" == parse_request("GET /path/templates/thing.html HTTP/1.1\r\nHOST: www.site.com")
    with pytest.raises(ValueError):
        parse_request("POST /path/thing.html HTTP/1.1\r\nHOST: www.site.com")
    with pytest.raises(ValueError):
        parse_request("asdfasdF")


