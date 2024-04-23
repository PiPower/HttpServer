import subprocess
import os
import ctypes
import socket
from http_requests import HttpReuquest


fastCgiRequest = None
freeBuffer = None
def start_php_fpm():
    subprocess.run(["g++", "-c", "-fPIC", "php_fpm/fast_cgi.cpp", "-DVERBOSE", "-o" , "php_fpm/cgi.o" ])
    subprocess.run(["g++", "-shared", "php_fpm/cgi.o", "-o" , "php_fpm/libcgi.so" ])
    os.remove("php_fpm/cgi.o")

    lib = ctypes.CDLL("php_fpm/libcgi.so")
    global fastCgiRequest, freeBuffer
    fastCgiRequest = lib.fastCgiRequest
    fastCgiRequest.argtypes = [ ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, 
                                                    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    fastCgiRequest.restype = ctypes.c_char_p

    freeBuffer = lib.freeBuffer

def send_fpm_script_translation_request(sd, request, root_dir):

    file_path = request.getResourcePath(root_dir)
    content =  request.body.encode("ascii")  if request.body != None else None

    ch = request.getHeader("Cookie")
    cookie = ch.encode("ascii") if ch != None else None

    clh = request.getHeader("Content-Length")
    content_len = clh.encode("ascii") if clh != None else None
    
    cth = request.getHeader("Content-Type")
    content_type = cth.encode("ascii") if cth != None else None

    body = fastCgiRequest(sd, file_path.encode("ascii"), request.method.encode("ascii"), content, content_len, content_type, cookie)
    freeBuffer()
    return body


def callPhp_Fpm(request, config):
    fpm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0 )
    fpm_server.connect( ( config["fpm_ip"], config["fpm_port"]) )
    html_body = send_fpm_script_translation_request(fpm_server.fileno(), request, config["root_directory"])
    fpm_server.close()
       
    return html_body


def process_php_file(request, config):
    fpm_response = callPhp_Fpm(request, config)

    headers, _, body = fpm_response.partition(b"\r\n\r\n")
    headers = {  line.split(b": ")[0] : line.split(b": ")[1] for line in headers.split(b"\r\n") if len(line)> 0 }

    if headers.get(b"Status")  == None: 
        status_line = b"HTTP/1.1 200 Ok\r\n"
    elif headers.get(b"Status")  == b"302 Found":
        status_line = b"HTTP/1.1 302 Found\r\n"
        del headers[b"Status"]
    else:
        print("unsuppurted php error message")
        exit(-1)

    headers = b"Connection:  keep-alive\r\nContent-Length: " + str(len(body)).encode("ascii") + \
                        b"\r\n" + b"\r\n".join([b": ".join( data) for data in headers.items()]) + b"\r\n\r\n"

    return status_line + headers + body

