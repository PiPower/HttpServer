import subprocess
import os
import ctypes

fastCgiRequest = None

def start_php_fpm():
    subprocess.run(["g++", "-c", "-fPIC", "php_fpm/fast_cgi.cpp", "-o" , "php_fpm/cgi.o" ])
    subprocess.run(["g++", "-shared", "php_fpm/cgi.o", "-o" , "php_fpm/libcgi.so" ])
    os.remove("php_fpm/cgi.o")

    lib = ctypes.CDLL("php_fpm/libcgi.so")
    global fastCgiRequest
    fastCgiRequest = lib.fastCgiRequest
    fastCgiRequest.argtypes = [ ctypes.c_int, ctypes.c_char_p]
    fastCgiRequest.restype = ctypes.c_char_p

def send_fpm_script_translation_request(sd, file_path):
    body = fastCgiRequest(sd, file_path.encode("ascii") )
    return body
