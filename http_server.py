import socket
#  from urllib2 import HTTPError

ADDR = ("127.0.0.1", 8000)
server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def parse_request(request):
    try:
        request = request.split("\r\n\r\n", 1)
        req = request[0].split("\r\n")
        for i, r in enumerate(req):
            req[i] = r.split()
        method = req[0][0].upper()
        uri = req[0][1]
        proto = req[0][2].upper()
        headers = {}
        for line in req[1:]:
            headers[line[0].upper()] = line[1:]
        if method == "GET":
            if proto == "HTTP/1.1" and "HOST:" in headers:
                return uri
            else:
                raise SyntaxError("400 Bad Request")
        else:
            raise ValueError("405 Method Not Allowed")
    except IndexError:
        raise SyntaxError("400 Bad Request")


def response_ok():
    html = "<html><head><title>Success!</title></head><body><header><h1>Success!</h1></header><p>It worked</p></body></html>"
    return ("HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: " + str(len(html)) + "\r\n"
            "\r\n" + html)


def response_error(e=Exception("500 Internal Server Error")):
    html = "<html><head><title>Error!</title></head><body><header><h1>Error!</h1></header><p>It did not work</p></body></html>"
    return ("HTTP/1.1 " + e.message + "\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: " + str(len(html)) + "\r\n"
            "\r\n" + html)


if __name__ == "__main__":
    server.bind(ADDR)
    server.listen(1)
    while True:
        try:
            conn, addr = server.accept()
            s, msg = "", True
            while msg:
                msg = conn.recv(16)
                s += msg
                if len(msg) < 16:
                    break
            print s
            try:
                parse_request(s)
                resp = response_ok()
            except (SyntaxError, ValueError) as e:
                resp = response_error(e)
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            # print e
            resp = response_error()

        conn.sendall(resp)
        conn.close()
