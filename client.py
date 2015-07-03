import socket

ADDR = ("127.0.0.1", 8000)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
msg = "GET ./images/sample_1.png HTTP/1.1\r\nHOST: www.site.com\r\n\r\n<html>stuff</html>"

try:
    client.sendall(msg)
    client.shutdown(socket.SHUT_WR)
    while True:
        part = client.recv(16)
        print part
        if len(part) < 16:
            client.close()
            break
except Exception as e:
    print e
