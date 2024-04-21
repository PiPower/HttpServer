import socket
from http_requests import HttpReuquest
from php_fpm.cpp_interface import send_fpm_script_translation_request

Code_302 = False

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


def requestHandler(request, clientSocket, config):
    request = HttpReuquest( request.decode("ascii",errors='ignore') )

    html_body = callPhp_Fpm(request, config)

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