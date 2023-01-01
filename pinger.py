#from twisted.internet import reactor
from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
import json
import datetime
import dbutils

jsonobj = {}
ip = ''
garbage = ['TCPShield.com', 'COSMIC GUARD']

def write_json(new_data, ip):
    with open('servers.json','r') as file:
        file_data = json.load(file)
    
    if ip not in file_data['serverlist']:
        file_data['serverlist'][ip] = []
    file_data["serverlist"][ip].append(new_data)

    with open('servers.json', 'w') as file:
        json.dump(file_data, file, indent = 2)

class PingProtocol(ClientProtocol):
    def status_response(self, data):
        for k, v in sorted(data.items()):
            if k != "favicon":
                jsonobj[k]=v
        reactor.stop()

class PingFactory(ClientFactory):
    protocol = PingProtocol
    protocol_mode_next = "status"

def main(address):
    ip = str(address)
    factory = PingFactory()
    try:
        factory.connect(ip, 25565)
        reactor.run()
    except:
        return
    jsonobj['ip']=ip
    jsonobj["time"]=str(datetime.datetime.now())
    if 'version' in jsonobj and jsonobj['version']['name'] not in garbage:
        dbutils.addPing(jsonobj)
    return

import sys
if __name__=='__main__':
    main(sys.argv[1])
