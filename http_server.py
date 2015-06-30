import socket

ADDR = ("127.0.0.1", 8001)
server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)


def response_ok():
    return "HTTP/1.1 200 OK <html><head><title>Success!</title></head><body><header><h1>Success!</h1></header><p>It worked</p></body></html>"


def response_error():
    return "HTTP/1.1 500 Internal Server Error <html><head><title>Error!</title></head><body><header><h1>Error!</h1></header><p>It did not work</p></body></html>"


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
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print e
            conn.sendall(response_error())
