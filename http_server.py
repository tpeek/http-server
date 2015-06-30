import socket
from urllib2 import HTTPError

ADDR = ("127.0.0.1", 8000)
server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def parse_request(request):
    req = request.split("\r\n")
    try:
        for i, r in enumerate(req):
            req[i] = r.split()
        method = req[0][0].upper()
        res = req[0][1]
        proto = req[0][2].upper()
        headers = {}
        for line in req[1:]:
            if line[0][0] == "<": break
            headers[line[0].upper()] = line[1:]
    except IndexError:
        raise ValueError("That was not a request I understand")
    if method == "GET" and proto == "HTTP/1.1" and "HOST:" in headers:
        return res
    else:
        raise ValueError
        

def response_ok():
    html = "<html><head><title>Success!</title></head><body><header><h1>Success!</h1></header><p>It worked</p></body></html>"
    return ("HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: "+ str(len(html)) + "\r\n"
            "\r\n" + html)
    


def response_error():
    html = "<html><head><title>Error!</title></head><body><header><h1>Error!</h1></header><p>It did not work</p></body></html>"
    return ("HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: "+ str(len(html)) + "\r\n"
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
                    conn.sendall(response_ok())
                    conn.close()
                    break
            print s
            try:
                parse_request(s)
                conn.sendall(response_ok())
            except:
                conn.sendall(response_error())
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print e
            conn.sendall(response_error())
