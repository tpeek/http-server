import socket

ADDR = ("127.0.0.1", 8001)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
msg = "do you hear me? Cause I hear you. I am going to eat food"

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
