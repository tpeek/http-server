import http_server

ADDR = ("127.0.0.1", 8000)
BUFF = 1024


def run_server(conn, adr):
    request = ""
    try:
        while True:
            s = conn.recv(BUFF)
            request += s
            if len(s) < BUFF:
                break
        print request
        try:
            uri = http_server.parse_request(request)
            body, ctype = http_server.resolve_uri(uri)
            response = http_server.response_ok(body, ctype)
        except (SyntaxError, ValueError, UserWarning) as e:
            response = http_server.response_error(e)
    except Exception as e:
        response = http_server.response_error()
    conn.sendall(response)
    conn.close()


def run_gserver():
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    gserver = StreamServer(ADDR, run_server)
    print('Gen Server spinning up on port 8000')
    gserver.serve_forever()


if __name__ == "__main__":
    run_gserver()
