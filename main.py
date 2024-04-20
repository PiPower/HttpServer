import socket
from  ConnectionHandler.Balancer import Balancer
import settings
import subprocess
from php_fpm.cpp_interface import start_php_fpm



if __name__ == "__main__":
    config = settings.getSettings()
    threadPool = Balancer(config["thread count"])
    if config["use_php_fpm"]:
        start_php_fpm()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    sock.bind((config["ip"], config["port"]))
    sock.listen()

    while True:
        client = sock.accept()
        threadPool.add_connection(client)
