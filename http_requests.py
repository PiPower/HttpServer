class HttpReuquest:
    def __init__(self, request) -> None:
        lines = request.split("\r\n") 
        self.body = lines[-1] if len(lines[-1]) > 0  else None
        self.method = lines[0].split(" ", 2)[0]
        self.resource = lines[0].split(" ", 2)[1]
        self.protocol_version = lines[0].split(" ", 2)[2]
        self.headers = {  line.split(": ")[0] : line.split(": ")[1] for line in lines[1:-2]  }
    
    def getResourcePath(self, rootDir):
        if self.resource == "/":
            return rootDir + "/index.php"
        return rootDir + self.resource
    
    def getHeader(self, key):
        return self.headers.get(key)