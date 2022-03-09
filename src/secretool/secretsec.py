import pyDes
import hashlib
import getpass
import base64
import random

class SecretSec():
    def __init__(self):
        self.keypreload = False
        self.enckey = b''
        self.signkey = b''

    def ss_keypreload(self):
        self.enckey = self.ss_setpass(type=1, notation="ENCRYPTION PASSWORD")
        if not self.enckey:
            return False
        self.signkey = self.ss_setpass(type=1, notation="SIGNING PASSWORD")
        if not self.signkey:
            self.enckey = b''
            return False
        self.keypreload = True
        return True

    def ss_keyclear(self):
        self.keypreload = False
        self.enckey = b''
        self.signkey = b''

    def ss_setpass(self, type=0, notation="ENCRYPTION PASSWORD"):
        if self.keypreload:
            if type == 0:
                return self.enckey
            elif type == 1:
                return self.signkey
        key = b''
        while True:
            inputpass1 = getpass.getpass(
                "set <%s> (length between 6 and 16): " % notation)
            plen = len(inputpass1)
            if plen < 6:
                # too short
                print("too short! not safe.")
                continue
            elif plen > 16:
                # too long
                print("too long! hard to remember.")
                continue
            else:
                break

        inputpass2 = getpass.getpass(
            "enter the above password again to confirm: ")
        if inputpass2 != inputpass1:
            print("Failed. Two input should be the same.")
            return key
        key = hashlib.md5(inputpass2.encode()).digest()[4:12]
        return key

    def ss_readpass(self, type=0, notation="ENCRYPTION PASSWORD"):
        if self.keypreload:
            if type == 0:
                return self.enckey
            elif type == 1:
                return self.signkey
        key = b''
        inputpass = getpass.getpass("enter your <%s>: " % notation)
        plen = len(inputpass)
        if plen >= 6 and plen <= 16:
            key = hashlib.md5(inputpass.encode()).digest()[4:12]
        return key

    def ss_enc(self, key, plaintext):
        iv = secret_key = key
        k = pyDes.des(secret_key, pyDes.CBC, iv,
                      pad=0, padmode=pyDes.PAD_PKCS5)
        salt = ""
        for i in range(8):
            salt += chr(random.randint(0, 128))
        plaintext = salt + plaintext
        data = k.encrypt(plaintext.encode(), padmode=pyDes.PAD_PKCS5)
        return base64.b64encode(data)

    def ss_dec(self, key, ciphertext):
        iv = secret_key = key
        k = pyDes.des(secret_key, pyDes.CBC, iv,
                      pad=0, padmode=pyDes.PAD_PKCS5)
        data = k.decrypt(base64.b64decode(ciphertext), padmode=pyDes.PAD_PKCS5)
        return data.decode()[8:]

    def ss_signature(self, signkey, enctext):
        hashobj = hashlib.md5(enctext)
        iv = secret_key = signkey
        k = pyDes.des(secret_key, pyDes.CBC, iv,
                      pad=0, padmode=pyDes.PAD_PKCS5)
        data = k.encrypt(hashobj.digest(), padmode=pyDes.PAD_PKCS5)
        return base64.b64encode(data).decode()