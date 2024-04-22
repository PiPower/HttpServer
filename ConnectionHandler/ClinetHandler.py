import socket
from http_requests import HttpReuquest
from php_fpm.cpp_interface import send_fpm_script_translation_request
import mimetypes

Code_302 = False

def getContentType(resource):
    (type, encoding) = mimetypes.guess_type(resource)
    return type


def callPhp_Fpm(request, config):
    fpm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    fpm_server.connect( ( config["fpm_ip"], config["fpm_port"]) )
    html_body = send_fpm_script_translation_request(fpm_server.fileno(), request, config["root_directory"])
    fpm_server.close()

    global Code_302
    Code_302 = False

    msg = HttpReuquest( "GET / HTTP/1.1\r\n" + html_body.decode("ascii",errors='ignore') )
    if msg.getHeader("Status") == "302 Found":
        Code_302 = True
       
    
    return html_body

def getResource(request, config):
    resourcePath = request.getResourcePath(config["root_directory"])
    with open(resourcePath, mode="rb") as file:
        body = file.read()

    response =  "Content-Type: {}\r\n\r\n".format(getContentType(request.resource) ).encode("ascii") + body


    return response

def requestHandler(request, clientSocket, config):
    print(request.decode("ascii", errors='ignore'))
    print("----------")
    request = HttpReuquest( request.decode("ascii",errors='ignore') )

    if request.resource == "/favicon.ico":
        response = b"HTTP/1.1 404 Not Found\r\nConnection:  keep-alive\r\n\r\n"
        clientSocket.send(response)
        return 

    if  request.getResourcePath(config["root_directory"]).split(".")[-1] == "php" :
        html_body = callPhp_Fpm(request, config)
    else:
        html_body = getResource(request, config)


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