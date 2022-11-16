from twisted.internet import reactor, defer
import quarry.types.uuid as uuid
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.net.auth import ProfileCLI
from quarry.net.auth import Profile
from time import sleep
import struct
import datetime
import argparse
import json

ip = ''
jsoninfo = {}
class ServerInfoProtocol(SpawningClientProtocol):
    ip = ip
    def setup(self):
        self.players = []

    def packet_login_disconnect(self, buff):
        p_data = buff.unpack_chat()
        jsoninfo['kick']=str(p_data)
        jsoninfo['joinTime']=str(datetime.datetime.now())
        jsoninfo['tablist']=self.players
        reactor.stop()

    def packet_player_list_item(self, buff):
        # 1.7.x
        if self.protocol_version <= 5:
            p_player_name = buff.unpack_string()
            p_online = buff.unpack('?')
            p_ping = buff.unpack('h')

            if p_online:
                self.players.append({
                    'name': p_player_name,
                    'ping': p_ping
                })
            elif p_player_name in self.players:
                del self.players[p_player_name]
        # 1.8.x
        else:
            p_action = buff.unpack_varint()
            p_count = buff.unpack_varint()
            for i in range(p_count):
                p_uuid = str(buff.unpack_uuid())
                if p_action == 0:  # ADD_PLAYER
                    p_player_name = buff.unpack_string()
                    p_properties_count = buff.unpack_varint()
                    p_properties = []
                    for j in range(p_properties_count):
                        p_property_name = buff.unpack_string()
                        p_property_value = buff.unpack_string()
                        p_property_is_signed = buff.unpack('?')
                        if p_property_is_signed:
                            p_property_signature = buff.unpack_string()
                        else:
                            p_property_signature = None
                        p_properties.append({'name': p_property_name, 'value': p_property_value, 'signature': p_property_signature})
                    p_gamemode = buff.unpack_varint()
                    p_ping = buff.unpack_varint()
                    p_has_display_name = buff.unpack('?')
                    if p_has_display_name:
                        p_display_name = str(buff.unpack_chat())
                    else:
                        p_display_name = None
                    if buff.unpack('?'):
                        p_sig_timestamp = buff.unpack('l')
                        p_sig_pub_key = ""
                        p_sig_key_sig = ""
                        for k in range(buff.unpack_varint()):
                            p_sig_pub_key =+buff.unpack('B')
                        for k in range(buff.unpack_varint()):
                            p_sig_key_sig =+buff.unpack('B')
                    else:
                        p_sig_timestamp = None
                        p_sig_pub_key = None
                        p_sig_key_sig = None
                    data = {
                        'uuid': p_uuid,
                        'name': p_player_name,
                        'properties': p_properties,
                        'gamemode': p_gamemode,
                        'ping': p_ping,
                        'display_name': p_display_name,
                        'timestamp': p_sig_timestamp,
                        'public_key': p_sig_pub_key,
                        'key_signature': p_sig_key_sig,
                    }
                    if data not in self.players:
                        self.players.append(data)

                elif p_action == 1:  # UPDATE_GAMEMODE
                    p_gamemode = buff.unpack_varint()
                    getByUUID(self.players, p_uuid)['gamemode'] = p_gamemode
                elif p_action == 2:  # UPDATE_LATENCY
                    p_ping = buff.unpack_varint()
                    getByUUID(self.players, p_uuid)['ping'] = p_ping
                elif p_action == 3:  # UPDATE_DISPLAY_NAME
                    p_has_display_name = buff.unpack('?')
                    if p_has_display_name:
                        p_display_name = str(buff.unpack_chat())
                    else:
                        p_display_name = None
                        getByUUID(self.players, p_uuid)['display_name'] = p_display_name
                elif p_action == 4:  # REMOVE_PLAYER
                    self.players.remove(getByUUID(self.players, p_uuid))

    def packet_join_game(self, buff):
        buff.unpack('i') # eid
        jsoninfo['hardcore']=buff.unpack('?')
        jsoninfo['gamemode']=buff.unpack('B')
        buff.unpack('b') # prevGamemode
        dim_count = buff.unpack_varint()
        jsoninfo['worlds'] = []
        for i in range(dim_count):
            jsoninfo['worlds'].append(buff.unpack_string())
        buff.unpack_nbt() # registryCodec
        buff.unpack_string() # SpawnDimensionType
        buff.unpack_string() # SpawnDimensionName
        jsoninfo['hashedSeed']=buff.unpack('q')
        buff.unpack_varint() # maxPlayers
        buff.unpack_varint() #viewDistance
        buff.unpack_varint() # simulationDistance
        buff.unpack('?') # reducedDebugInfo
        buff.unpack('?') # enableRespawnScreen
        buff.unpack('?') # isDebug
        buff.unpack('?') # isFlat
        if(buff.unpack('?')):
            buff.unpack_string() # deathDimensionName
            buff.unpack_position() # deathLocation
        buff.discard()

    def packet_server_difficulty(self, buff):
        jsoninfo['difficulty']=buff.unpack('b')
        buff.unpack('?')# DifficultyLocked

    def packet_chunk_data(self, buff):
        buff.discard()
        jsoninfo['joinTime']=str(datetime.datetime.now())
        jsoninfo['tablist']=self.players
        reactor.stop()

class ChatLoggerFactory(ClientFactory):
    protocol = ServerInfoProtocol


@defer.inlineCallbacks
def run(args):
    # Log in
    #profile = yield ProfileCLI.make_profile(args)
    profile = yield Profile.from_token('',open('../token.txt','r').read().rstrip(),'Admin_Else','3632330d373742708e8f270e581c45db') # U wont get my accses token (;

    # Create factory
    factory = ChatLoggerFactory(profile)

    # Connect!
    ip = args.host
    factory.connect(ip, 25565)


def main(argv):
    #parser = ProfileCLI.make_parser()
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    args = parser.parse_args(argv)

    run(args)
    reactor.run()
    if jsoninfo['tablist'][0]['uuid']==str(uuid.UUID.from_offline_player(jsoninfo['tablist'][0]['name'])):
        jsoninfo['offlineMode']=True
    else:
        jsoninfo['offlineMode']=False
    safe(args.host)

def getByUUID(list, uuid):
    for item in list:
        if item['uuid']==uuid:
            return item

def safe(ip):
    with open('servers.json','r+') as file:
      # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["servers"][ip]=jsoninfo
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 2)
    file.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])