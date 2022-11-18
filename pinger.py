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
        for k, v in sorted(data.items()):
            if(k=='description'):
                jsonobj["description"]=v
            if(k=='players'):
                jsonobj["players"]=v
            if(k=='version'):
                jsonobj["version"]=v
        reactor.stop()

class PingFactory(ClientFactory):
    protocol = PingProtocol
    protocol_mode_next = "status"

def main(address):
    from twisted.internet import reactor
    from quarry.net.client import ClientFactory, ClientProtocol
    import json
    import datetime
    

    ip = str(address)
    factory = PingFactory()
    factory.connect(ip, 25565)
    reactor.run()
            

    jsonobj['ip']=ip
    jsonobj["time"]=str(datetime.datetime.now())
    if jsonobj['version']['name'] not in garbage:
        write_json(jsonobj)



if __name__ == "__main__":
    import sys
    main(sys.argv[1])