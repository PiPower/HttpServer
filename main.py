import socket
from  ConnectionHandler.Balancer import Balancer
import settings

config = settings.getSettings()
threadPool = Balancer(config["thread count"])


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
sock.bind((config["ip"], config["port"]))
sock.listen()

while True:
    client = sock.accept()
    threadPool.add_connection(client)
