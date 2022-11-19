from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
import json
import datetime

jsonobj = {}
ip = ''
garbage = ['TCPShield.com', 'COSMIC GUARD']

def write_json(new_data):
    with open('servers.json','r') as file:
        file_data = json.load(file)
    
    file_data["serverlist"].append(new_data)

    with open('servers.json', 'w') as file:
        json.dump(file_data, file, indent = 2)

class PingProtocol(ClientProtocol):
    def status_response(self, data):
        jsonobj["description"]=data['description']
        jsonobj["players"]=data['players']
        jsonobj["version"]=data['version']
        reactor.stop()

class PingFactory(ClientFactory):
    protocol = PingProtocol
    protocol_mode_next = "status"

def main(address, q):
    ip = str(address)
    factory = PingFactory()
    factory.connect(ip, 25565)
    reactor.run()
            
    jsonobj['ip']=ip
    jsonobj["time"]=str(datetime.datetime.now())
    if 'version' in jsonobj and jsonobj['version']['name'] not in garbage:
        q.put(jsonobj)
    else:
        q.put(None)
    return

if __name__ == "__main__":
    import sys
    main(sys.argv[1])