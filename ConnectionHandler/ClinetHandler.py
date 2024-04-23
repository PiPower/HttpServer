import socket
from http_requests import HttpReuquest
from php_fpm.fpm_interface import send_fpm_script_translation_request
import RequestHandlers as RH

Code_302 = False

def requestHandler(request, clientSocket, config):
    request = HttpReuquest( request.decode("ascii",errors='ignore') )

    if request.resource == "/favicon.ico":
        response = b"HTTP/1.1 404 Not Found\r\nConnection:  keep-alive\r\n\r\n"
        clientSocket.send(response)
        return 

    if request.getMethod() == "GET":
        html_body = RH.handle_get(request, config)

    elif request.getMethod() == "POST":
        html_body = RH.handle_post(request, config)


    body_len = str(len(html_body.partition(b"\r\n\r\n")[2])).encode("ascii") + b"\r\n"
    global Code_302
    if not(Code_302):
        response = b"HTTP/1.1 200 OK\r\nConnection:  keep-alive\r\nContent-Length: "+ body_len + html_body
    else:
        response = b"HTTP/1.1 302 Found\r\nConnection:  keep-alive\r\nContent-Length: "+ body_len + html_body
    clientSocket.send(response)


def handleClients(clientList, config):
    i = 0
    while True:
        if len(clientList) < 1:
            continue

        i %= len(clientList)
        (clientSocket, clientAddress) = clientList[i]

        request = bytearray()

        while True:
            try:
                buff = clientSocket.recv(10000, socket.MSG_DONTWAIT)
            except Exception as ioErr:
                break
            request = request + buff

            #closed socket
            if len(buff) == 0:
                clientList.pop(i )
                break
            
        if len(request) > 0:
            requestHandler(request, clientSocket, config)
        i += 1