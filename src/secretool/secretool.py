#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# from errno import EKEYEXPIRED
import socket
import json
import base64
import pyDes
import getpass
import time
import random
import hashlib
from secretcontroller import SecretController
from secretsec import SecretSec
from secretdb import SecretDB

def main():
    controller = SecretController()
    sdb = SecretDB(controller)
    username = controller.username
    print('initiate done. enter help for guidance. :)\n')
    try:
        while True:
            if sdb.isSealed:
                sealstr = " sealed "
                sealcolor = 50
            else:
                sealstr = "unsealed"
                sealcolor = 41

            if sdb.codec.keypreload:
                keyloadstr = " super "
                keyloadcolor = 45
            else:
                keyloadstr = " safer "
                keyloadcolor = 50

            if sdb.ismodified:
                modifystr = "*"
            else:
                modifystr = ""
            # usercommand = input('%s@Secretool:[%s][%s]>' % (username, sealstr, modifystr)).split()
            usercommand = input('\033[1;32;50m%s\033[0m@\033[1;37;44mSecretool\033[0m:[\033[0;37;%dm%s\033[0m][\033[0;37;%dm%s\033[0m]\033[0;31;50m%s\033[0m> ' %
                                (username, sealcolor, sealstr, keyloadcolor, keyloadstr, modifystr)).split()

            if len(usercommand) == 0:
                continue

            elif usercommand[0] == 'quit':
                if len(usercommand) != 1:
                    print("Usage example: quit")
                    continue
                if not sdb.isSealed:
                    saveornot = input(
                        'your secret is unsealed. save it before quit?\nEnter [yes] or [no]: ')
                    if saveornot == 'yes':
                        sdb.saveDB()
                    elif saveornot != 'no':
                        print("Cancelled. please enter yes or no.")
                        continue
                break

            elif usercommand[0] == 'help':
                if len(usercommand) != 1:
                    print("Usage example: help")
                    continue
                print("help message")

            elif usercommand[0] == 'reload-server':
                if len(usercommand) != 1:
                    print("Usage example: reload-server")
                    continue
                controller.reloadServer()

            elif usercommand[0] == 'preload-keys':
                if len(usercommand) != 1:
                    print("Usage example: preload-keys")
                    continue
                if sdb.codec.ss_keypreload():
                    print("ok")

            elif usercommand[0] == 'clear-keys':
                if len(usercommand) != 1:
                    print("Usage example: clear-keys")
                    continue
                sdb.codec.ss_keyclear()
                print("ok")

            elif usercommand[0] == 'init':
                if len(usercommand) != 1:
                    print("Usage example: init")
                    continue
                sdb.initDB()

            elif usercommand[0] == 'save':
                if len(usercommand) != 1:
                    print("Usage example: save")
                    continue
                sdb.saveDB()

            elif usercommand[0] == 'unseal':
                if len(usercommand) != 1:
                    print("Usage example: unseal")
                    continue
                sdb.unsealDB()

            elif usercommand[0] == 'seal':
                if len(usercommand) != 1:
                    print("Usage example: seal")
                    continue
                sdb.sealDB()

            elif usercommand[0] == 'import':
                if len(usercommand) != 2:
                    print("Usage example: import filename.json")
                    continue
                sdb.importDB(usercommand[1])

            elif usercommand[0] == 'export':
                if len(usercommand) != 2:
                    print("Usage example: import filename.json")
                    continue
                sdb.exportDB(usercommand[1])

            elif usercommand[0] == 'list':
                if len(usercommand) == 1:
                    usercommand.append('/')
                elif len(usercommand) > 2:
                    print("Usage example: list [scope]")
                    continue
                if usercommand[1][-1] == '/':
                    scope = usercommand[1][:-1]
                else:
                    scope = usercommand[1]
                sdb.listItems(scope)

            elif usercommand[0] == 'add':
                # command
                if len(usercommand) != 4:
                    print("Usage example: add /your/path yourtitle yourvalue")
                    continue
                sdb.addItem(usercommand[1], usercommand[2], usercommand[3])

            elif usercommand[0] == 'delete':
                if len(usercommand) != 3:
                    print("Usage example: delete /your/path yourtitle")
                    continue
                sdb.deleteItem(usercommand[1], usercommand[2])

            elif usercommand[0] == 'purge':
                if len(usercommand) != 2:
                    print("Usage example: purge /your/path")
                    continue
                sdb.purgeScope(usercommand[1])

            elif usercommand[0] == 'get':
                if len(usercommand) != 3:
                    print("Usage example: get /your/path yourtitle")
                    continue
                sdb.getItem(usercommand[1], usercommand[2])

            elif usercommand[0] == 'query-remote':
                if len(usercommand) != 1:
                    print("Usage example: query-remote")
                    continue
                res = controller.query()
                print("remotedb info:")
                for item in res:
                    print("version %d ---> created in %s" %
                          (item['version'], item['date']))

            elif usercommand[0] == 'pull-remote':
                if len(usercommand) == 1:
                    version = 0
                elif len(usercommand) == 2:
                    version = int(usercommand[1])
                else:
                    print("Usage: pull-remote [version]")
                    continue

                res = controller.pull(sdb, version)
                if res:
                    print('ok')
                else:
                    print('Error!')
            elif usercommand[0] == 'push-remote':
                if len(usercommand) != 1:
                    print("Usage example: push-remote")
                    continue
                res = controller.push(sdb)
                print(res)
            elif usercommand[0] == 'clean-remote':
                if len(usercommand) != 2:
                    print("Usage example: clean-remote {version}")
                    continue
                res = controller.clean(int(usercommand[1]))
                print(res)
            else:
                print('unsupported command!')
    except EOFError:
        print("\nCtrl+D")
    except KeyboardInterrupt:
        print("\nCtrl+C")
        pass
    print("bye bye~ :)")


if __name__ == "__main__":
    main()
