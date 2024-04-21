class HttpReuquest:
    def __init__(self, request) -> None:
        headers, _,  body = request.partition("\r\n\r\n") 
        headers = headers.split("\r\n")
        self.body = body if len(body) > 0  else None
        self.method = headers[0].split(" ", 2)[0]
        self.resource = headers[0].split(" ", 2)[1]
        self.protocol_version = headers[0].split(" ", 2)[2]
        self.headers = {  line.split(": ")[0] : line.split(": ")[1] for line in headers[1:] }
    
    def getResourcePath(self, rootDir):
        if self.resource == "/":
            return rootDir + "index.php"
        return rootDir + self.resource[1:]
    
    def getHeader(self, key):
        return self.headers.get(key)