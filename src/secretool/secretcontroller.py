import socket
import json
import time

class SecretController():
    def __init__(self):
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            self.username = config['username']
        except:
            print("invalid configuration!")
            return

        try:
            serverConf = config['servers'][0]
            self.serverIP = serverConf['ip']
            self.serverPort = serverConf['port']
            self.serverToken = serverConf['token']
            self.loadServer = True
        except:
            print("no valid server configuration in config.json!")
            self.loadServer = False

    def reloadServer(self):
        try:
            with open("config.json", 'r') as f:
                serverConf = json.load(f)['servers'][0]
        except:
            print("invalid configuration!")
            return

        try:
            self.serverIP = serverConf['ip']
            self.serverPort = serverConf['port']
            self.serverToken = serverConf['token']
            self.loadServer = True
        except:
            print("no valid server configuration in config.json!")
            self.loadServer = False

        if self.ping():
            print("server is prepared. :)")
        else:
            print('server is not prepared. :(')

    def ping(self):
        if self.loadServer == False:
            print("no server configuration loaded!")
            return False
        try:
            ping = json.dumps({"username": self.username,
                               "token": self.serverToken, "command": "ping"})
            # print(self.serverIP, self.serverPort)
            clientSock = socket.socket()
            clientSock.connect((self.serverIP, self.serverPort))
            clientSock.send(ping.encode())
            response = clientSock.recv(256).decode()
            clientSock.close()
            if response != 'pong':
                raise ValueError(response)
            print("remote server is prepared!")
            return True
        except ValueError as e:
            print(e)
            self.loadServer = False
        except ConnectionRefusedError as e:
            print(e)
            self.loadServer = False
        except:
            print('something wrong with server!')
            self.loadServer = False
        return False

    def query(self):
        if self.loadServer == False:
            print("no server configuration loaded!")
            return []
        try:
            qmsg = json.dumps({"username": self.username,
                               "token": self.serverToken, "command": "query"})
            clientSock = socket.socket()
            clientSock.connect((self.serverIP, self.serverPort))
            clientSock.send(qmsg.encode())
            response = clientSock.recv(32768).decode()
            clientSock.close()
            versionlist = json.loads(response)
            # for item in versionlist:
            #     print("version %d ---> created in %s" % (item['version'], item['date']))
            return versionlist
        except ConnectionRefusedError as e:
            print(e)
            self.loadServer = False
        except:
            print('something wrong with server!')
        return []

    def push(self, sdb):
        if self.loadServer == False:
            print("no server configuration loaded!")
            return ""
        if sdb.ismodified == True:
            print("cannot push when secret is modified! Try to save first.")
            return ""
        # key confirm
        key = sdb.codec.ss_setpass(type=1, notation="SIGNING PASSWORD")
        if not key:
            return ""
        digest = sdb.codec.ss_signature(key, sdb.rawDB)
        pmsg = json.dumps(
            {"username": self.username, "token": self.serverToken, "command": "push", "raw": sdb.rawDB.decode(), "digest": digest})
        try:
            clientSock = socket.socket()
            clientSock.connect((self.serverIP, self.serverPort))
            clientSock.send(pmsg.encode())
            response = clientSock.recv(256).decode()
            clientSock.close()
            return response
        except ConnectionRefusedError as e:
            print(e)
            self.loadServer = False
        except:
            print('something wrong with server!')
        return ""

    def pull(self, sdb, version=0):
        if self.loadServer == False:
            print("no server configuration loaded!")
            return False
        if sdb.isSealed == False:
            print("cannot pull when secret is unsealed!")
            return False
        try:
            pmsg = json.dumps(
                {"username": self.username, "token": self.serverToken, "command": "pull", "version": version})
            clientSock = socket.socket()
            clientSock.connect((self.serverIP, self.serverPort))
            clientSock.send(pmsg.encode())
            response = clientSock.recv(65536).decode()
            clientSock.close()
            # print(response)
            res = json.loads(response)
            if res["success"] == 0:
                print("Invalid version!")

            content = res["content"]
            digest = res["digest"]
            # print(content)
            # three times
            retry = 0
            while retry < 3:
                key = sdb.codec.ss_readpass(
                    type=1, notation="SIGNING PASSWORD")
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong signature! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    signature = sdb.codec.ss_signature(key, content.encode())
                    if digest != signature:
                        raise Exception("wrong signature")
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong signature! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                print(
                    "Failed. this version is maybe poisoned! your server may be in danger!")
                return False

            with open('.localdb.sdb', 'w') as f:
                f.write(content)
            sdb._loadDB()
            return True
        except ConnectionRefusedError as e:
            print(e)
            self.loadServer = False
        except:
            print('something wrong with server!')
        return False

    def clean(self, version):
        if self.loadServer == False:
            print("no server configuration loaded!")
            return ""
        try:
            cmsg = json.dumps(
                {"username": self.username, "token": self.serverToken, "command": "clean", "version": version})
            clientSock = socket.socket()
            clientSock.connect((self.serverIP, self.serverPort))
            clientSock.send(cmsg.encode())
            response = clientSock.recv(256).decode()
            clientSock.close()
            return response
        except ConnectionRefusedError as e:
            print(e)
            self.loadServer = False
        except:
            print('something wrong with server!')
        return ""
