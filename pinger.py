from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
import dbutils
garbage, jsonobj = ['TCPShield.com', 'COSMIC GUARD'], {}
class PingProtocol(ClientProtocol):
    def status_response(self, data):    
        global jsonobj
        jsonobj = data
        reactor.stop()

class PingFactory(ClientFactory):
    protocol = PingProtocol
    protocol_mode_next = "status"

def main(address, port = 25565):
    factory = PingFactory()
    try:
        factory.connect(address, port)
        reactor.run()
    except Exception as e:
        print(e)
    return jsonobj

import sys
if __name__=='__main__':
    print(main(sys.argv[1]))