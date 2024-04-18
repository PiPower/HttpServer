import socket

def handleClients(clientList):
    i = 0
    while True:
        if len(clientList) < 1:
            continue
        clientServed = clientList[i]
        print(clientServed[1])
        clientServed[0].close()
        i += 1
        i %= len(clientList)