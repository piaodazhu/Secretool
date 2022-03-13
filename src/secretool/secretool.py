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
import sys
from secretcontroller import SecretController
from secretsec import SecretSec
from secretdb import SecretDB

try:
    import readline
except ImportError:
    print("warning: module readline or pyreadline not found. SShell may won't autocomplete.")
else:
    import rlcompleter
    print("ok")
    if(sys.platform == 'darwin'):
        readline.parse_and_bind ("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

CMD = ['help', 'quit', 'init', 'list', 'add',
        'add', 'get', 'delete', 'purge', 'save',
        'export', 'import', 'unseal', 'seal',
        'query-remote', 'pull-remote', 'push-remote',
        'reload-server', 'preload-keys', 'clear-keys']

def completer(text, state):
    
    options = [cmd for cmd in CMD if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

helpmessage = "\n\
command             explaination\n\
=============================================\n\
help                print usage of Secretool\n\
quit                quit the Scretool Shell\n\
init                initialize a encrypted secret zone\n\
list [$s]           list all keys under the scope s\n\
add $s $k [-f|s] $v add key-value pair (k,v) in the scope s. -f: v is a filename, -s: v is a sentence\n\
get $s $k           get value of k under scope\n\
delete $s $k        delete key-value pair (k,*) in the scope s\n\
purge $s            purge scope, clear all key-value pairs in and under the scope s\n\
save                save the modified secret zone into disk\n\
export $filename    decrypt and export the secret zone to a cleartext json file\n\
import $filename    import the secret zone from a cleartext json file and encrypt\n\
unseal              switch to the mode where you can read and edit without password\n\
seal                switch to the mode where you must input password to see your secrets\n\
query-remote        query the remote server for historical uploaded encrypted secret zones\n\
pull-remote [$v]    download the encrypted secret zone version $v from the remote server\n\
push-remote         upload current encrypted secret zone to the remote server\n\
reload-server       reload and check remote server configuration from config.json\n\
preload-keys        preload your encryption key and signing key for autofill\n\
clear-keys          clear the keys and cancel autofill\n\
    read the manual for more details.\n\
"

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
            # print('\033[1;32;50m%s\033[0m@\033[1;37;44mSecretool\033[0m:[\033[0;37;%dm%s\033[0m][\033[0;37;%dm%s\033[0m]\033[0;31;50m%s\033[0m' %
            #                     (username, sealcolor, sealstr, keyloadcolor, keyloadstr, modifystr))
            userinput = input('\033[1;32;50m%s\033[0m@\033[1;37;44mSecretool\033[0m:[\033[0;37;%dm%s\033[0m][\033[0;37;%dm%s\033[0m]\033[0;31;50m%s\033[0m$> ' %
                                (username, sealcolor, sealstr, keyloadcolor, keyloadstr, modifystr))
            usercommand = userinput.split()

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
                print(helpmessage)

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
                tmp = userinput.split("'")
                buf = ""
                valid = True
                if len(usercommand) < 5:
                    valid = False
                elif usercommand[3] == '-s' and len(tmp) == 3:
                    buf = tmp[1]
                elif usercommand[3] == '-s' and len(tmp) == 1 and len(usercommand) == 5:
                    buf = usercommand[4]
                elif len(usercommand) == 5 and usercommand[3] == '-f' and len(tmp) == 1:
                    try:
                        with open(usercommand[4], 'r') as f:
                            buf = f.read()
                    except:
                        print("invalid filename")
                        valid = False
                else:
                    valid = False
                
                if valid:
                    sdb.addItem(usercommand[1], usercommand[2], buf)
                else:
                    print("Usage example: add /your/path yourtitle [-s 'sentence' | -f filename]")
                    continue
                # if valid == False and usercommand[3] == '-s'
                # if len(usercommand) != 5:
                #     print("Usage example: add /your/path yourtitle [-s 'sentence' | -f filename]")
                #     continue
                # sdb.addItem(usercommand[1], usercommand[2], usercommand[3])

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
