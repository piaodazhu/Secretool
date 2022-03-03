#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from curses.ascii import isdigit
import threading
import socket               # 导入 socket 模块
import time
import json

class processThread (threading.Thread):
    def __init__(self, clientSocket, clientAddr):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
    def run(self):
        # receive message
        # check user
        # if fetch  read file
        #           return file
        # if upload read file
        #           update file
        # return response
        print(self.clientAddr)

        rawmsg = self.clientSocket.recv(1024)
        try:
            msg = json.loads(rawmsg.decode())
            username = msg['username']
            passwd = msg['passwd']
            command = msg['command']
            version = 0
            raw = ""
            if 'version' in msg:
                version = msg['version']
            if not isdigit(version):
                raise ValueError('version should be a number')
            if 'raw' in msg:
                raw = msg['raw']
        except:
            time.sleep(3)
            self.clientSocket.send("invalid message!")
            self.clientSocket.close()
            return

        item = getItemwdByUser(username)
        if not item:
            time.sleep(3)
            self.clientSocket.send("Wrong username!".encode())
            self.clientSocket.close()
            return
        
        if passwd != item['passwd']:
            time.sleep(3)
            self.clientSocket.send("Wrong password!".encode())
            self.clientSocket.close()
            return
        # judge
        if command == 'pull':
            latestVersion = item['content'][-1]['version']
            if version == 0 or version > latestVersion:
                version = latestVersion
            content = item['content'][version - 1]['raw']
            self.clientSocket.send(json.dumps(content).encode())
            self.clientSocket.close()
            return
        elif command == 'push':
            if 'content' not in item:
                item['content'] = [raw]
            else:
                item['content'].append(raw)
            self.clientSocket.send("ok".encode())
            self.clientSocket.close()
            return
        elif command == 'query':
            tmp = []
            if 'content' in item:
                for record in item['content']:
                    tmp.append({'version': record['version'], 'date': record['date']})
            self.clientSocket.send(json.dumps(tmp).encode())
            self.clientSocket.close()
            return
        else:
            time.sleep(3)
            self.clientSocket.send("Wrong command!".encode())
            self.clientSocket.close()
            return

threadLock = threading.Lock()
threads = []
filename = 'secretdb_template.json'
with open(filename, 'rb') as f:
    secretdb = json.load(f)

def getItemwdByUser(username):
    for item in secretdb:
        if item['username'] == username:
            return item
    return {}

def main():
    serverSocket = socket.socket()
    host = socket.gethostname()
    port = 9933
    serverSocket.bind((host, port))
    serverSocket.listen(12)
    print("initating done! waiting for connection...")
    while True:
        clientSocket,clientAddr = serverSocket.accept()     # 建立客户端连接
        i = 100
        while i > 8:
            i = 0
            for t in threads[:]:
                if t.is_alive() == True:
                    i += 1
                else:
                    threads.remove(t)
            time.sleep(0.01)
        th = processThread(clientSocket, clientAddr)
        th.start()
        threads.append(th)


if __name__=='__main__':
    main()