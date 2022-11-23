import requests
import json
from Crypto.PublicKey import RSA
from cryptography import x509
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64decode
from base64 import b64encode

def rsa_decrypt(s, pem):
    key = key.replace("-----BEGIN RSA PRIVATE KEY-----", "").replace("-----END RSA PRIVATE KEY-----", "").replace("\n", "")
    key = b64decode(key)
    key = RSA.importKey(key)

    cipher = PKCS1_v1_5.new(key)
    plaintext = cipher.decrypt(b64decode(s), "Error while decrypting")

    return plaintext

    return ciphertext
def r2j(r):
    return json.loads(r.content.decode(encoding='UTF-8'))

def getKeyPair(token):
    return requests.post('https://api.minecraftservices.com/player/certificates', headers={'Authorization': f'Bearer {token}','Content-Type': 'application/json; charset=utf-8'})

publicKeyString = r2j(getKeyPair('NO!!!'))['keyPair']['publicKey']
publicKeyBytes = bytes(publicKeyString, 'UTF-8')

print(publicKeyString)