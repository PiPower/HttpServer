import threading
import copy
from ConnectionHandler.ClinetHandler import handleClients
class Balancer:
    def __init__(self, threadCount, config):
        self.threadLists = [ [] for _ in range(threadCount)]
        self.threads = [] 
        for t in range(threadCount):
            t_conf =  copy.deepcopy(config)
            t_conf["thread_id"] = int(t)
            self.threads.append(threading.Thread(target = handleClients, args=(self.threadLists[t], t_conf )) )
        for thread in self.threads:
            thread.start()
          

        self.currentThread = 0
    def add_connection(self, client):
        self.threadLists[self.currentThread].append(client)
        self.currentThread =  (self.currentThread + 1) % len(self.threadLists)
