import socket
from http_requests import HttpReuquest
from php_fpm.fpm_interface import send_fpm_script_translation_request
import RequestHandlers as RH


def requestHandler(request, clientSocket, config):
    request = HttpReuquest( request.decode("ascii",errors='ignore') )

    if request.getMethod() == "GET":
        response = RH.handle_get(request, config)

    elif request.getMethod() == "POST":
        response = RH.handle_post(request, config)

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