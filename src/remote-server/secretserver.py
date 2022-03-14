#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import threading
import socket
import time
import json


global secretdb
global dirty
global threadLock

dbfile = 'secretdb.json'
conffile = 'config.json'

class storeThread(threading.Thread):
    def __init__(self, delay=1):
        threading.Thread.__init__(self)
        self.delay = delay
        self.killed = False

    def run(self):
        global dirty
        global threadLock
        global secretdb
        while True and not self.killed:
            if dirty == True:
                time.sleep(self.delay)
                threadLock.acquire()
                with open(dbfile, 'w') as f:
                    json.dump(secretdb, f, indent=4, separators=(',', ': '))
                # print("write!")
                dirty = False
                threadLock.release()
            else:
                time.sleep(self.delay)


class processThread(threading.Thread):
    def __init__(self, clientSocket, clientAddr):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.killed = False

    def run(self):
        if self.killed:
            return
        print(self.clientAddr)
        global dirty
        global threadLock
        global secretdb

        rawmsg = self.clientSocket.recv(65536)
        try:
            # print(rawmsg.decode())
            msg = json.loads(rawmsg.decode())
            username = msg['username']
            token = msg['token']
            command = msg['command']
            version = 0
            raw = ""
            digest = ""
            if 'version' in msg:
                version = msg['version']
            if type(version) != int:
                raise ValueError('version should be a number')
            if 'raw' in msg:
                raw = msg['raw']
                digest = msg['digest']
        except:
            time.sleep(3)
            self.clientSocket.send("Invalid message!".encode())
            self.clientSocket.close()
            return

        item = secretdb.get(username)
        if not item:
            time.sleep(3)
            self.clientSocket.send("Wrong username!".encode())
            self.clientSocket.close()
            return
        if token != item['token']:
            time.sleep(3)
            self.clientSocket.send("Wrong token!".encode())
            self.clientSocket.close()
            return

        if command == 'pull':
            idx = 0
            found = False
            res = {"success": 1, "content": "", "digest": ""}
            for record in item['content']:
                if record['version'] > version:
                    break
                if record['version'] == version:
                    found = True
                    break
                idx += 1

            if version == 0:
                content = item['content'][-1]['raw']
                digest = item['content'][-1]['digest']
            elif found:
                content = item['content'][idx]['raw']
                digest = item['content'][idx]['digest']
            else:
                content = ""
                digest = ""
                res["success"] = 0

            res["content"] = content
            res["digest"] = digest
            self.clientSocket.send(json.dumps(res).encode())
            self.clientSocket.close()
            return
        elif command == 'push':
            if 'content' not in item:
                item['content'] = []
                latestVersion = 0
            elif len(item['content']) == 0:
                latestVersion = 0
            else:
                latestVersion = item['content'][-1]['version']
            threadLock.acquire()
            item['content'].append(
                {"version": latestVersion + 1, "date": time.strftime("%Y-%m-%d %H:%M:%S"), "raw": raw, "digest": digest})
            dirty = True
            threadLock.release()
            self.clientSocket.send("ok".encode())
            self.clientSocket.close()
            # save

            return
        elif command == 'clean':
            # bug
            self.clientSocket.send(
                "clean is now unsupported because it is unsafe.".encode())
            self.clientSocket.close()
            # save
            return

            idx = 0
            found = False
            for record in item['content']:
                if record['version'] > version:
                    break
                if record['version'] == version:
                    found = True
                    break
                idx += 1

            if not found:
                time.sleep(3)
                self.clientSocket.send("Invalid version!".encode())
                self.clientSocket.close()
                return
            else:
                threadLock.acquire()
                item['content'].pop(idx)
                dirty = True
                threadLock.release()

            self.clientSocket.send(
                ("ok. delete version %d" % version).encode())
            self.clientSocket.close()
            # save
            return
        elif command == 'query':
            tmp = []
            if 'content' in item:
                for record in item['content']:
                    tmp.append(
                        {'version': record['version'], 'date': record['date']})
            self.clientSocket.send(json.dumps(tmp).encode())
            self.clientSocket.close()
            return
        elif command == 'ping':
            self.clientSocket.send("pong".encode())
            self.clientSocket.close()
        else:
            time.sleep(3)
            self.clientSocket.send("Wrong command!".encode())
            self.clientSocket.close()
            return


# def getItemwdByUser(username):
#     for item in secretdb:
#         if item['username'] == username:
#             return item
#     return {}


def main():
    global secretdb
    global threadLock
    global dirty
    dirty = False
    try:
        with open(conffile, 'r') as f:
            conf = json.load(f)
        host = conf['serveip']
        port = conf['serveport']
        clientlist = conf['clientlist']
        clientset = set()
        for client in clientlist:
            if client['username'] in clientset:
                raise Exception
            clientset.add(client['username'])
        print('client count: %d' % len(clientset))
    except:
        print("invalid config file!")
        return
    
    try:
        with open(dbfile, 'rb') as f:
            secretdb = json.load(f)
        for client in clientlist:
            account = secretdb.get(client['username'])
            if account:
                account['token'] = client['token']
            else:
                secretdb[client['username']] = {'token': client['token'], 'content': []}
    except:
        print("invalid database file!")
        return

    try:
        serverSocket = socket.socket()
        serverSocket.bind((host, port))
        serverSocket.listen(12)
    except:
        print("network error!")
        return

    threads = []
    threadLock = threading.Lock()
    print("initating done! listen on %s:%d. waiting for connection..." % (host, port))
    storeth = storeThread()
    storeth.start()
    while True:
        try:
            clientSocket, clientAddr = serverSocket.accept()
        except KeyboardInterrupt:
            print("bye bye~ :)")
            storeth.killed = True
            exit()
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


if __name__ == '__main__':
    main()
