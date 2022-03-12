import time
import json
from secretsec import SecretSec

class SecretDB():
    def __init__(self, controller):
        if controller.ping():
            print("server is prepared. :)")
        else:
            print('run in local mode without remote server. :)')

        try:
            with open(".localdb.sdb", 'rb') as f:
                self.rawDB = f.read()
                print("localdb is found.")
        except:
            self.rawDB = ""
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")

        self.username = controller.username
        # ?!!?
        self.localDB = {}
        self.isSealed = True
        self.ismodified = False
        self.codec = SecretSec()

    def _loadDB(self):
        with open('.localdb.sdb', 'rb') as f:
            self.rawDB = f.read()
        self.ismodified = False

    def _saveDB(self):
        with open('.localdb.sdb', 'wb') as f:
            f.write(self.rawDB)
        self.ismodified = False

    def _printItem(self, node, prefix):
        # print("%s:" % prefix)
        if node['kvs'] != {}:
            print("%s: %s" % (prefix, list(node['kvs'].keys())))
        for child in node['children']:
            self._printItem(child, prefix + '/' + child['name'])

    def initDB(self):
        ensure = input(
            "This may erase previous secrets. Are you sure to initialize a new secret database?\nEnter [yes] or [no]: ")
        if ensure == "yes":
            self.isSealed = True
            self.ismodified = False
            emptydb = {"name": "", "kvs": {}, "children": [],
                       "createdate": time.strftime("%Y-%m-%d %H:%M:%S")}
            tmp = json.dumps(emptydb)
            # key = getpass.getpass("enter your key:")
            key = self.codec.ss_setpass()
            if not key:
                return ""
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            print('ok')
        elif ensure == "no":
            print("Initialization is cancelled.")
            return
        else:
            print("Cancelled. please enter yes or no.")
            return

    def saveDB(self):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if not self.isSealed:
            tmp = json.dumps(self.localDB)
            key = self.codec.ss_setpass()
            if not key:
                return
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            print('ok')
        else:
            print('ok')

    def unsealDB(self):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if not self.isSealed:
            print('ok')
            return
        # self._loadDB()
        # key = getpass.getpass("enter your key:")
        retry = 0
        while retry < 3:
            key = self.codec.ss_readpass()
            if key == '':
                retry += 1
                time.sleep(1)
                print("wrong password! you can retry %d more time(s)." %
                      (3 - retry))
                continue
            try:
                self.localDB = json.loads(self.codec.ss_dec(key, self.rawDB))
                self.isSealed = False
                break
            except:
                retry += 1
                time.sleep(1)
                print("wrong password! you can retry %d more time(s)." %
                      (3 - retry))

    def sealDB(self):
        if self.isSealed:
            print('ok')
            return
        if self.ismodified:
            saveornot = input(
                'save all changes before seal?\nEnter [yes] or [no]: ')
            if saveornot == 'yes':
                tmp = json.dumps(self.localDB)
                key = self.codec.ss_setpass()
                if not key:
                    return
                self.rawDB = self.codec.ss_enc(key, tmp)
                self._saveDB()
                self.localDB = {}
                self.isSealed = True
            elif saveornot == 'no':
                print('Discard all changes and sealed.')
                self.isSealed = True
                self.ismodified = False
            else:
                print("Cancelled. please enter yes or no.")
                return
        else:
            # tmp = json.dumps(self.localDB, indent=4, separators=(',', ': '))
            # key = self.codec.ss_setpass()
            # self.rawDB = self.codec.ss_enc(key, tmp)
            # self._saveDB()
            self.localDB = {}
            self.isSealed = True

    def exportDB(self, filename):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if not self.isSealed:
            with open(filename, 'w') as f:
                json.dump(self.localDB, f, indent=4, separators=(',', ': '))
        else:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    tmp = self.codec.ss_dec(key, self.rawDB)
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return

            with open(filename, 'w') as f:
                f.write(tmp)
            print("ok")

    def importDB(self, filename):
        try:
            with open(filename, 'r') as f:
                newdb = json.load(f)
        except:
            print("valid target file not found!")
            return

        if not self.isSealed:
            self.localDB = newdb
            self.ismodified = True
        else:
            tmp = json.dumps(newdb)
            # print(tmp)
            key = self.codec.ss_setpass()
            if not key:
                return
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            print("ok")

    def listItems(self, scope=""):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if self.isSealed:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    self.localDB = json.loads(
                        self.codec.ss_dec(key, self.rawDB))
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return
        startOfTravel = DBptr = self.localDB
        for name in scope.split('/')[1:]:
            if name == '':
                continue
            found = False
            for child in DBptr['children']:
                if child['name'] == name:
                    startOfTravel = child
                    DBptr = child
                    found = True
                    break
            if not found:
                print("not found")
                return

        self._printItem(startOfTravel, scope)

    def addItem(self, scope, title, val):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if self.isSealed:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    self.localDB = json.loads(
                        self.codec.ss_dec(key, self.rawDB))
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return
        curnode = DBptr = self.localDB
        # print("scope=<%s>" % scope )
        for name in scope.split('/')[1:]:
            # print(name)
            if name == '':
                continue
            found = False
            for child in DBptr['children']:
                if child['name'] == name:
                    # print('xxx')
                    curnode = child
                    DBptr = child
                    found = True
                    break
            if not found:
                # print('yyy')
                child = {"name": name, "kvs": {}, "children": []}
                DBptr['children'].append(child)
                curnode = child
                DBptr = child

        curnode["kvs"][title] = val

        if self.isSealed:
            tmp = json.dumps(self.localDB)
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            self.localDB = {}
        else:
            self.ismodified = True
        print('ok')

    def deleteItem(self, scope, title):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if self.isSealed:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    self.localDB = json.loads(
                        self.codec.ss_dec(key, self.rawDB))
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return

        curnode = DBptr = self.localDB
        # print(curnode['kvs'])
        for name in scope.split('/')[1:]:
            if name == '':
                continue
            # print("xxx")
            found = False
            for child in DBptr['children']:
                if child['name'] == name:
                    curnode = child
                    DBptr = child
                    found = True
                    break
            if not found:
                print("not found")
                return
        # may not exist
        # print(curnode['kvs'])
        if not curnode['kvs'].get(title):
            print("not found")
            return

        val = curnode['kvs'].pop(title)

        if self.isSealed:
            tmp = json.dumps(self.localDB)
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            self.localDB = {}
        else:
            self.ismodified = True
        print("ok. delete title=%s, val=%s..." % (title, val[:64]))

    def purgeScope(self, scope):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if self.isSealed:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    self.localDB = json.loads(
                        self.codec.ss_dec(key, self.rawDB))
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return
        curnode = DBptr = self.localDB
        father = []
        idx = 0
        # print(curnode['kvs'])
        for name in scope.split('/')[1:]:
            if name == '':
                continue
            # print("xxx")
            found = False
            father = DBptr['children']
            idx = 0
            for child in father:
                if child['name'] == name:
                    curnode = child
                    DBptr = child
                    found = True
                    break
                idx += 1
            if not found:
                print("not found")
                return
        # warning
        purgeornot = input(
            'purge is dangrous. Are you sure to purge <%s>?\nEnter [yes] to confirm: ' % scope)
        if purgeornot == 'yes':
            pass
        else:
            print("Purge cancelled.")
            return

        if father != []:
            father.pop(idx)
        else:
            # don't purge root node
            curnode['kvs'].clear()
            curnode['children'].clear()

        if self.isSealed:
            tmp = json.dumps(self.localDB)
            self.rawDB = self.codec.ss_enc(key, tmp)
            self._saveDB()
            self.localDB = {}
        else:
            self.ismodified = True
        print("ok. purge <%s>..." % scope)

    def getItem(self, scope, title):
        if len(self.rawDB) == 0:
            print(
                "localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.")
            return
        if self.isSealed:
            retry = 0
            while retry < 3:
                key = self.codec.ss_readpass()
                if key == '':
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
                    continue
                try:
                    self.localDB = json.loads(
                        self.codec.ss_dec(key, self.rawDB))
                    break
                except:
                    retry += 1
                    time.sleep(1)
                    print("wrong password! you can retry %d more time(s)." %
                          (3 - retry))
            if retry == 3:
                return

        curnode = DBptr = self.localDB
        # print(curnode['kvs'])
        for name in scope.split('/')[1:]:
            if name == '':
                continue
            # print("xxx")
            found = False
            for child in DBptr['children']:
                if child['name'] == name:
                    curnode = child
                    DBptr = child
                    found = True
                    break
            if not found:
                print("not found")
                return
        # may not exist
        # print(curnode['kvs'])
        val = curnode['kvs'].get(title)
        if not val:
            print("not found")
            return

        print("get %s under <%s>:\n%s" % (title, scope, val))
