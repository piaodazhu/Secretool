#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import socket               # 导入 socket 模块
import time
import json
import base64
import pyDes

s = socket.socket()         # 创建 socket 对象
host = socket.gethostname() # 获取本地主机名
port = 9933               # 设置端口号

s.connect((host, port))
msg = json.dumps({"username": "user1", "passwd":"xxxx", "command":"pull", "args": 1})
s.send(msg.encode())
rbuf = s.recv(4096)
rmsg = base64.b64decode(rbuf.decode())
k = pyDes.des("12121212", pyDes.CBC, "12121212", pad=None, padmode = pyDes.PAD_PKCS5)
data = k.decrypt(rmsg, padmode=pyDes.PAD_PKCS5)
        
print(data)