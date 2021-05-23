import socket

MAX_LENGTH = 1024
MAX_LENGH_SPAN = 10


class Client:

    def __init__(self, port=37020) -> None:
        self.port = port

    def get_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                               socket.IPPROTO_UDP)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", self.port))
        self.client = client
        return client

    def sendto(self, message):
        self.client.sendto(message, ("<broadcast>", 37020))

    def recvfrom(self):
        data, addr = self.client.recvfrom(1024)
        print(f"recieved from {addr}")
        return data, addr


# count = 0
# while True:
#     client = Client()
#     client.sendto("hai")
