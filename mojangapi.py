import json
import requests
import dateutil.parser
from Crypto.PublicKey import RSA

def setSkin(token, skinUrl, skinType):
    skinTypeString = 'classic'
    if(skinType==1):
        skinTypeString='slim'

    json_data = {
        'variant': skinTypeString,
        'url': skinUrl,
    }

    return requests.post('https://api.minecraftservices.com/minecraft/profile/skins', headers={'Authorization': f'Bearer {token}','Content-Type':'application/json; charset=utf-8'}, json=json_data)

def setName(token, newName):
    return requests.put(f'https://api.minecraftservices.com/minecraft/profile/name/{newName}', headers={'Authorization': f'Bearer {token}','Content-Type':'application/json; charset=utf-8'})

def getKeyPair(token):
    return requests.post('https://api.minecraftservices.com/player/certificates', headers={'Authorization': f'Bearer {token}','Content-Type': 'application/json; charset=utf-8'})

def getProfileInfo(token):
    return requests.get('https://api.minecraftservices.com/minecraft/profile', headers={'Authorization': f'Bearer {token}','Content-Type': 'application/json; charset=utf-8'})

def r2j(r):
    return json.loads(r.content.decode(encoding='UTF-8'))

def updateprofileinfo():
    with open('../token.txt', 'r') as f:
        data = [line.rstrip()
                for line in f.readlines()]
    
    uuidAndName = r2j(getProfileInfo(data[0]))
    data[1] = uuidAndName['name']
    data[2] = uuidAndName['id']
    keys = r2j(getKeyPair(data[0]))
    data[3] = keys['keyPair']['publicKey'][30:][:-30].replace('\n', '')
    data[4] = keys['publicKeySignature']
    parsed_time = dateutil.parser.parse(keys['expiresAt'])
    t_in_millisec = parsed_time.strftime('%s%f')
    data[5] = t_in_millisec[:-3]
    with open('../token.txt', 'w') as f:
        f.writelines([line+'\n'
                for line in data])
    
updateprofileinfo()