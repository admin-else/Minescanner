from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
import json
import datetime

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
        jsonobj["description"]=data['description']
        jsonobj["players"]=data['players']
        jsonobj["version"]=data['version']
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
    except Exception as e:
        print(e)
    jsonobj['ip']=ip
    jsonobj["time"]=str(datetime.datetime.now())
    if 'version' in jsonobj and jsonobj['version']['name'] not in garbage:
        write_json(jsonobj, ip)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])