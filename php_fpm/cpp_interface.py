import subprocess
import os
import ctypes

fastCgiRequest = None
freeBuffer = None
def start_php_fpm():
    subprocess.run(["g++", "-c", "-fPIC", "php_fpm/fast_cgi.cpp", "-o" , "php_fpm/cgi.o" ])
    subprocess.run(["g++", "-shared", "php_fpm/cgi.o", "-o" , "php_fpm/libcgi.so" ])
    os.remove("php_fpm/cgi.o")

    lib = ctypes.CDLL("php_fpm/libcgi.so")
    global fastCgiRequest, freeBuffer
    fastCgiRequest = lib.fastCgiRequest
    fastCgiRequest.argtypes = [ ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    fastCgiRequest.restype = ctypes.c_char_p

    freeBuffer = lib.freeBuffer

def send_fpm_script_translation_request(sd, request, root_dir):
    file_path = request.getResourcePath(root_dir)
    content =  request.body.encode("ascii")  if request.body != None else None

    clh = request.getHeader("Content-Length")
    content_len = clh.encode("ascii") if clh != None else None
    
    cth = request.getHeader("Content-Type")
    content_type = cth.encode("ascii") if cth != None else None

    body = fastCgiRequest(sd, file_path.encode("ascii"), request.method.encode("ascii"), content, content_len, content_type )
    freeBuffer()
    return body
