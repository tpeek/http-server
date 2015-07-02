import socket
import os
import sys


ROOT = "./webroot/"
ADDR = ("127.0.0.1", 8000)
server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def resolve_uri(uri):
    if "../" in uri:
        raise UserWarning("403 Forbidden")

    if os.path.isfile(uri):
        TYPE = uri.split(".")[-1].lower()
        if TYPE in ('PNG', 'JPG', 'JPEG', 'GIF'):
            TYPE = 'image/' + TYPE
        else:
            TYPE = 'text/' + TYPE
        BODY = open(uri).read()

    elif os.path.isdir(uri):
        TYPE = "text/html"
        BODY = "<!DOCTYPE HTML><html><head><title>Directory</title></head><h1>Directory</h1>"
        for root, dirs, files in os.walk(uri):
            BODY += "<h3>" + root + "</h3>"
            BODY += "<ul>"
            for f in files:
                BODY += "<li>" + f + "</li>"
            BODY += "</ul>"
        BODY += "</body></html>"

    else:
        raise IOError("404 Not Found")
    return TYPE, BODY


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
                return ROOT + uri
            else:
                raise SyntaxError("400 Bad Request")
        else:
            raise ValueError("405 Method Not Allowed")
    except IndexError:
        raise SyntaxError("400 Bad Request")


def response_ok(TYPE, BODY):

    return ("HTTP/1.1 200 OK\r\n"
            "Content-Type: " + TYPE + "\r\n"
            "Content-Length: " + str(sys.getsizeof(BODY)) + "\r\n"
            "\r\n" + BODY)


def response_error(e=Exception("500 Internal Server Error")):
    html = "<html><head><title>Error!</title></head><body><header><h1>Error!</h1></header><p>It did not work</p></body></html>"
    return ("HTTP/1.1 " + e.message + "\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: " + str(sys.getsizeof(html)) + "\r\n"
            "\r\n" + html)


if __name__ == "__main__":
    server.bind(ADDR)
    server.listen(1)
    while True:
        try:
            conn, addr = server.accept()
            s, msg = "", True
            while msg:
                msg = conn.recv(1024)
                s += msg
                if len(msg) < 1024:
                    break
            print s
            try:
                uri = parse_request(s)
                TYPE, BODY = resolve_uri(uri)
                resp = response_ok(TYPE, BODY)
            except (SyntaxError, ValueError, UserWarning) as e:
                resp = response_error(e)
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            # print e
            resp = response_error()

        conn.sendall(resp)
        conn.close()
