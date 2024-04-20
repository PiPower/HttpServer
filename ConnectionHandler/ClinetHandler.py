import socket
from http_requests import HttpReuquest
from php_fpm.cpp_interface import send_fpm_script_translation_request

def requestHandler(request, clientSocket, config):
    request = HttpReuquest( request.decode("ascii") )

    fpm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    fpm_server.connect( ( config["fpm_ip"], config["fpm_port"]) )
    html_body = send_fpm_script_translation_request(fpm_server.fileno(), request.getResourcePath(config["root_directory"]) )
    fpm_server.close()

    response = b"HTTP/1.1 200 OK\r\n" + html_body
    clientSocket.send(response)


def handleClients(clientList, config):
    i = 0
    while True:
        if len(clientList) < 1:
            continue
        (clientSocket, clientAddress) = clientList[i]
        request = bytearray()

        while True:
            try:
                buff = clientSocket.recv(1024, socket.MSG_DONTWAIT)
            except BlockingIOError as ioErr:
                break

            request = request + buff
        requestHandler(request, clientSocket, config)
        i += 1
        i %= len(clientList)