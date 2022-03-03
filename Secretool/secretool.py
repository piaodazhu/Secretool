#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from msilib.schema import Error
import socket
import time
import json
import base64
import pyDes

class SecreteDB(dict):
    def __init__(self, username, serverConf={}, rawdb=""):
        if serverConf:
            self.serverConf = serverConf
            validServer = True
            try:
                ping = json.dumps({"username": username, "passwd": serverConf['password'], "command":"ping"})
                clientSock = socket.socket()
                clientSock.connect(serverConf['host'], serverConf['port'])
                clientSock.send(ping.encode())
                response = clientSock.recv(256).decode()
                if response != 'pong':
                    raise ValueError(response)
                print("remote server is prepared!")
            except ValueError as e:
                print(e)
                validServer = False
            except ConnectionRefusedError as e:
                print(e)
                validServer = False
            except:
                print('something wrong with server!')
                validServer = False
        else:
            print('run in local mode without remote server. :)')
            validServer = False

        self.validServer = validServer
        self.encdb = rawdb


def main():
    try:
        with open("config.json", 'r') as f:
            raw = f.read()
            

if __name__=="__main__":
    main()