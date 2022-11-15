from curses import tigetflag
from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
import json
import datetime

f = open("onlineplayers.txt", 'w')
jsonobj = {}
ip = ''
garbage = ['TCPShield.com', 'COSMIC GUARD']

def write_json(new_data):
    with open('servers.json','r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["serverlist"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 2)
        file.close()

class PingProtocol(ClientProtocol):

    def status_response(self, data):
        for k, v in sorted(data.items()):
            if(k=='description'):
                if(v=='"text": "\u00a7cInvalid hostname. \u00a77Please refer to our documentation at docs.tcpshield.com"'):
                    exit
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