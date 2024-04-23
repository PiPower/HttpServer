import mimetypes

def getContentType(resource):
    (type, encoding) = mimetypes.guess_type(resource)
    return type

def getResource(request, config):
    resourcePath = request.getResourcePath(config["root_directory"])
    try:
        file = open(resourcePath, mode="rb")
        body = file.read()
        file.close()
    except Exception:
        return b"HTTP/1.1 404 Not Found\r\nConnection:  keep-alive\r\n\r\n"
    
    response =  "Content-Length: {}\r\nContent-Type: {}\r\n\r\n".format(len(body), getContentType(request.resource) ).encode("ascii")
    status_line = b"HTTP/1.1 200 Ok\r\n"

    return status_line + response + body