import socket
from http_requests import HttpReuquest
from php_fpm.cpp_interface import send_fpm_script_translation_request

def requestHandler(request, clientSocket, config):
    request = HttpReuquest( request.decode("ascii",errors='ignore') )
    if request.resource == "/favicon.ico":
        response = b"HTTP/1.1 404 NOT FOUND\r\nConnection:  keep-alive\r\n"
        clientSocket.send(response)
        return

    
    fpm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    fpm_server.connect( ( config["fpm_ip"], config["fpm_port"]) )
    html_body = send_fpm_script_translation_request(fpm_server.fileno(), request, config["root_directory"])
    fpm_server.close()


    print(html_body.decode("ascii",errors='ignore'))

    body_len = str(len(html_body.partition(b"\r\n\r\n")[2])).encode("ascii") + b"\r\n"
    response = b"HTTP/1.1 200 OK\r\nConnection:  keep-alive\r\nContent-Length: "+ body_len + html_body
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
            
        if len(request) > 0:
            requestHandler(request, clientSocket, config)
        i += 1
        i %= len(clientList)