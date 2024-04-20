class HttpReuquest:
    def __init__(self, request) -> None:
        lines = request.split("\r\n")
        self.methord = lines[0].split(" ")[0]
        self.resource = lines[0].split(" ")[1]
        self.host = lines[0].split(" ")[2]
    
    def getResourcePath(self, rootDir):
        if self.resource == "/":
            return rootDir + "/index.php"
        return rootDir + self.resource