import mimetypes

def getContentType(resource):
    (type, encoding) = mimetypes.guess_type(resource)
    return type

def getResource(request, config):
    resourcePath = request.getResourcePath(config["root_directory"])
    with open(resourcePath, mode="rb") as file:
        body = file.read()

    response =  "Content-Type: {}\r\n\r\n".format(getContentType(request.resource) ).encode("ascii") + body


    return response