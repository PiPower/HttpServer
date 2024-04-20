import subprocess
import os

def start_php_fpm():
    subprocess.run(["g++", "-c", "-fPIC", "php_fpm/fast_cgi.cpp", "-o" , "php_fpm/cgi.o" ])
    subprocess.run(["g++", "-shared", "php_fpm/cgi.o", "-o" , "php_fpm/libcgi.so" ])
    os.remove("php_fpm/cgi.o")
