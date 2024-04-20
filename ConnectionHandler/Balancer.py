import threading
from ConnectionHandler.ClinetHandler import handleClients
class Balancer:
    def __init__(self, threadCount, config):
        self.threadLists = [ [] for _ in range(threadCount)]
        self.threads = [
            threading.Thread(target = handleClients, args=(self.threadLists[t], config))
              for t in range(threadCount) ]
        for thread in self.threads:
            thread.start()
          

        self.currentThread = 0
    def add_connection(self, client):
        self.threadLists[self.currentThread].append(client)
        self.currentThread =  (self.currentThread + 1) % len(self.threadLists)
