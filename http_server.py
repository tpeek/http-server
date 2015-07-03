import os
import sys
import mimetypes


ROOT = "./webroot/"
ADDR = ("127.0.0.1", 8000)


def resolve_uri(uri):
    uri = os.path.join(ROOT, uri)
    if ".." in uri:
        raise UserWarning("403 Forbidden")

    if os.path.isfile(uri):
        ctype = mimetypes.guess_type(uri, strict=True)[0]
        body = open(uri).read()

    elif os.path.isdir(uri):
        ctype = "text/html"
        body = ("<!DOCTYPE HTML><html><head><title>Directory</title>"
                "</head><h1>Directory</h1>")
        for root, dirs, files in os.walk(uri):
            body += "<h3>{}</h3><ul>".format(root)
            for f in files:
                body += "<li>{}</li>".format(f)
            body += "</ul><ul>"
            for d in dirs:
                body += "<li>{}</li>".format(d)
            body += "</ul>"
        body += "</body></html>"
    else:
        raise IOError("404 Not Found")
    return ctype, body


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
        elif method in ["POST", "UPDATE", "DELETE", "PUT",
                        "HEAD", "OPTIONS", "CONNECT"]:
            raise ValueError("405 Method Not Allowed")
        else:
            raise SyntaxError("400 Bad Request")
    except IndexError:
        raise SyntaxError("400 Bad Request")


def response_ok(ctype, body):
    return ("HTTP/1.1 200 OK\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n"
            "\r\n{}").format(ctype,  str(sys.getsizeof(body)), body)


def response_error(e=Exception("500 Internal Server Error")):
    html = ("<html><head><title>Error!</title></head>"
            "<body><header><h1>Error!</h1></header>"
            "<p>{}</p></body></html>").format(e.message)
    return ("HTTP/1.1 {}\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: {}\r\n"
            "\r\n{}").format(e.message, str(sys.getsizeof(html)), html)


def run_http_server():
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


if __name__ == "__main__":
    run_http_server()
