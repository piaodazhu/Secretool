import pyDes
import binascii         #二进制和 ASCII 码互转

#创建类
class Descryption:
    # pyDes.des（key，[mode]，[IV]，[pad]，[padmode]）
    # 加密密钥的字节、加密类型、可选参数用来设置填充字符、设置填充模式
    def des_encrypt(self, key, plaintext):
        iv = secret_key = key
        k = pyDes.des(secret_key, pyDes.CBC, iv, pad=None, padmode = pyDes.PAD_PKCS5)
        data = k.encrypt(plaintext, padmode=pyDes.PAD_PKCS5)
        # print(binascii.b2a_hex(data).decode())      #data.进制返回文本字符串.解码字符串
        return data

    def des_decrypt(self, key, ciphertext):
        iv = secret_key = key
        k = pyDes.des(secret_key, pyDes.CBC, iv, pad=None, padmode = pyDes.PAD_PKCS5)
        data = k.decrypt(binascii.a2b_hex(ciphertext), padmode=pyDes.PAD_PKCS5)
        # print(data.decode())
        return data

#调用
des = Descryption()

while True:
    key = input("请输入秘钥：\n")
    mode = input("encrypt or decrypt?：\n")
    if mode.strip() == 'encrypt':
        plaintext = input("请输入明文：\n")
        des.des_encrypt(key, plaintext.strip())
    else:
        ciphertext = input("请输入密文：\n")
        des.des_decrypt(key, ciphertext.strip())
