import socket
from  ConnectionHandler.Balancer import Balancer
import settings
import subprocess
from php_fpm.fpm_interface import start_php_fpm



if __name__ == "__main__":
    config = settings.getSettings()
    threadPool = Balancer(config["thread_count"], config)

    start_php_fpm(config)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config["ip"], config["port"]))
    sock.listen()
    while True:
        client = sock.accept()
        threadPool.add_connection(client)
