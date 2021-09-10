import struct


def receive(sock) -> bytes:
    request_length = struct.unpack(">I", sock.recv(4))[0]
    return sock.recv(request_length)


def send(sock, data: bytes):
    sock.sendall(struct.pack(">I", len(data)) + data)
