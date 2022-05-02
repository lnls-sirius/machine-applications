import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('10.1.2.156', 3334))
sock.send(b'Opa')

MSGLEN=10
chunks = []
bytes_recd = 0
while bytes_recd < MSGLEN:
    chunk = sock.recv(min(MSGLEN - bytes_recd, 2048))
    if chunk == b'':
        raise RuntimeError("socket connection broken")
    chunks.append(chunk)
    bytes_recd = bytes_recd + len(chunk)
    print(b''.join(chunks))