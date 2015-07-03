import socket
import os
import sys
import mimetypes
import select


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
        body = "<!DOCTYPE HTML><html><head><title>Directory</title></head><h1>Directory</h1>"
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
        else:
            raise ValueError("405 Method Not Allowed")
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


def run_server(adr):
    serv_sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(ADDR)
    serv_sock.listen(5)
    input = [serv_sock, sys.stdin]
    msgs = {}
    running = True
    while running:
        read_ready, write_ready, except_ready = select.select(input, [], [], 0)
        for readable in read_ready:
            if readable is serv_sock:
                hand_sock, adr = readable.accept()
                input.append(hand_sock)
                msgs[id(hand_sock)] = ""
            elif readable is sys.stdin:
                sys.stdin.readline()
                running = False
            else:
                s = echo(readable, msgs[id(readable)])
                if type(s) == list:
                    msgs[id(readable)] += s[0]
                else:
                    readable.sendall(s)
                    input.remove(readable)
    serv_sock.close()


def echo(sock, s):
    try:
        msg = sock.recv(1024)
        s += msg
        if msg == "":
            try:
                uri = parse_request(s)
                ctype, body = resolve_uri(uri)
                resp = response_ok(ctype, body)
            except (SyntaxError, ValueError, UserWarning) as e:
                resp = response_error(e)
        else:
            return [s]
    except Exception as e:
        resp = response_error()
    return resp

if __name__ == "__main__":
    run_server(ADDR)
            # try:
            #     conn, addr = server.accept()
            #     s, msg = "", True
            #     while msg:
            #         msg = conn.recv(1024)
            #         s += msg
            #         if len(msg) < 1024:
            #             break
            #     print s
            #     try:
            #         uri = parse_request(s)
            #         ctype, body = resolve_uri(uri)
            #         resp = response_ok(ctype, body)
            #     except (SyntaxError, ValueError, UserWarning) as e:
            #         resp = response_error(e)
            # except KeyboardInterrupt as e:
            #     break
            # except Exception as e:
            #     resp = response_error()

            # conn.sendall(resp)
            # conn.close()
