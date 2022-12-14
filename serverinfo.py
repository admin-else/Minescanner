from twisted.internet import reactor, defer
from quarry.types.uuid import UUID as uuid
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.net.auth import ProfileCLI
from quarry.net.auth import Profile
import time
import struct
import datetime
import argparse
import json
import dotenv
import os
import twisted
from quarry.net.protocol import Factory, Protocol, ProtocolError, \
    protocol_modes_inv
jsoninfo = {}
class ServerInfoProtocol(SpawningClientProtocol):

    def switch_protocol_mode(self, mode):
        self.check_protocol_mode_switch(mode)
        if mode in ("status", "login"):
            # Send handshake
            addr = self.transport.connector.getDestination()
            self.send_packet(
                "handshake",
                self.buff_type.pack_varint(self.protocol_version) +
                self.buff_type.pack_string(addr.host) +
                self.buff_type.pack('H', addr.port) +
                self.buff_type.pack_varint(
                    protocol_modes_inv[self.factory.protocol_mode_next]))

            # Switch buff type
            self.buff_type = self.factory.get_buff_type(self.protocol_version)

        self.protocol_mode = mode

        if mode == "status":
            # Send status request
            self.send_packet("status_request")

        elif mode == "login":
            # Send login start
            # TODO: Implement signatures/1.19.1 UUID sending
            if self.protocol_version >= 760:  # 1.19.1+
                self.send_packet("login_start",
                                 self.buff_type.pack_string(self.factory.profile.display_name),
                                 self.buff_type.pack("?",  False),  # No signature as we haven't implemented them here
                                 #self.buff_type.pack('Q',int(jsoninfo['profileinfo'][5])),
                                 #self.buff_type.pack_byte_array(bytes(jsoninfo['profileinfo'][3],'UTF-8')),
                                 #self.buff_type.pack_byte_array(bytes(jsoninfo['profileinfo'][4],'UTF-8')),
                                 self.buff_type.pack("?", True),
                                 self.buff_type.pack_uuid(uuid.from_hex(os.getenv('MC_UUID'))))
            elif self.protocol_version == 759:  # 1.19
                self.send_packet("login_start",
                                 self.buff_type.pack_string(self.factory.profile.display_name),
                                 self.buff_type.pack("?", False))  # No signature as we haven't implemented them here
            else:
                # Send login start
                self.send_packet("login_start", self.buff_type.pack_string(
                    self.factory.profile.display_name))

    def setup(self):
        self.players = []

    def packet_login_disconnect(self, buff):
        p_data = buff.unpack_chat()
        jsoninfo['kick']=str(p_data)
        jsoninfo['joinTime']=str(datetime.datetime.now())
        jsoninfo['tablist']=self.players
        reactor.stop()

    def packet_player_list_header_footer(self, buff):
        jsoninfo['tablistheader']=buff.unpack_string()
        jsoninfo['tablistfooter']=buff.unpack_string()

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
        elif self.protocol_version <= 758:
            p_action = buff.unpack_varint()
            p_count = buff.unpack_varint()
            for i in range(p_count):
                p_uuid = buff.unpack_uuid()
                if p_action == 0:  # ADD_PLAYER
                    p_player_name = buff.unpack_string()
                    p_properties_count = buff.unpack_varint()
                    p_properties = {}
                    for j in range(p_properties_count):
                        p_property_name = buff.unpack_string()
                        p_property_value = buff.unpack_string()
                        p_property_is_signed = buff.unpack('?')
                        if p_property_is_signed:
                            p_property_signature = buff.unpack_string()

                        p_properties[p_property_name] = p_property_value
                    p_gamemode = buff.unpack_varint()
                    p_ping = buff.unpack_varint()
                    p_has_display_name = buff.unpack('?')
                    if p_has_display_name:
                        p_display_name = buff.unpack_chat()
                    else:
                        p_display_name = None

                    # 1.19+
                    if self.protocol_version >= 759:
                        if buff.unpack('?'):
                            timestamp = buff.unpack("Q")
                            key_length = buff.unpack_varint()
                            key_bytes = buff.read(key_length)
                            signature_length = buff.unpack_varint()
                            signature = buff.read(signature_length)

                    self.players[p_uuid] = {
                        'name': p_player_name,
                        'properties': p_properties,
                        'gamemode': p_gamemode,
                        'ping': p_ping,
                        'display_name': p_display_name
                    }

                elif p_action == 1:  # UPDATE_GAMEMODE
                    p_gamemode = buff.unpack_varint()

                    if p_uuid in self.players:
                        self.players[p_uuid]['gamemode'] = p_gamemode
                elif p_action == 2:  # UPDATE_LATENCY
                    p_ping = buff.unpack_varint()

                    if p_uuid in self.players:
                        self.players[p_uuid]['ping'] = p_ping
                elif p_action == 3:  # UPDATE_DISPLAY_NAME
                    p_has_display_name = buff.unpack('?')
                    if p_has_display_name:
                        p_display_name = buff.unpack_chat()
                    else:
                        p_display_name = None

                    if p_uuid in self.players:
                        self.players[p_uuid]['display_name'] = p_display_name
                elif p_action == 4:  # REMOVE_PLAYER
                    if p_uuid in self.players:
                        del self.players[p_uuid]
        # 1.19.x
        elif self.protocol_version <= 761:
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
                    if self.protocol_version<=760:
                        if buff.unpack('?'):
                            p_sig_timestamp = buff.unpack('l')
                            p_pub_key = ""
                            p_sig_key_sig = ""
                            for k in range(buff.unpack_varint()):
                                p_pub_key =+buff.unpack('B')
                            for k in range(buff.unpack_varint()):
                                p_sig_key_sig =+buff.unpack('B')
                        else:
                            p_sig_timestamp = None
                            p_pub_key = None
                            p_sig_key_sig = None
                    else:
                        p_sig_timestamp = None
                        p_pub_key = None
                        p_sig_key_sig = None
                    data = {
                        'uuid': p_uuid,
                        'name': p_player_name,
                        'properties': p_properties,
                        'gamemode': p_gamemode,
                        'ping': p_ping,
                        'display_name': p_display_name,
                        'timestamp': p_sig_timestamp,
                        'public_key': p_pub_key,
                        'key_signature': p_sig_key_sig,
                    }
                    if data not in self.players:
                        self.players.append(data)
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
        buff.unpack_varint() # viewDistance
        buff.unpack_varint() # simulationDistance
        buff.unpack('?') # reducedDebugInfo
        buff.unpack('?') # enableRespawnScreen
        buff.unpack('?') # isDebug
        buff.unpack('?') # isFlat
        if(buff.unpack('?')):
            buff.unpack_string() # deathDimensionName
            buff.unpack_position() # deathLocation
        buff.discard()

    def packet_time_update(self, buff):
        buff.unpack('l') # on paper always returns 0 ):
        jsoninfo['daytime'] = buff.unpack('l')

    def packet_server_difficulty(self, buff):
        jsoninfo['difficulty']=buff.unpack('b')
        buff.unpack('?')# DifficultyLocked
    
    def packet_plugin_message(self, buff):
        buff.unpack_string()
        jsoninfo['brand']=buff.unpack_string()

    def packet_chunk_data(self, buff):
        buff.discard()
        jsoninfo['joinTime']=str(datetime.datetime.now())
        jsoninfo['tablist']=self.players
        try:
            reactor.stop()
        except twisted.internet.error.ReactorNotRunning:
            pass



class ChatLoggerFactory(ClientFactory):
    protocol = ServerInfoProtocol


@defer.inlineCallbacks
def run(ip):                            
    profile = yield Profile.from_token('',os.getenv('MC_TOKEN'),os.getenv('MC_NAME'),os.getenv('MC_UUID')) # U wont get my accses token (;

    # Create factory
    factory = ChatLoggerFactory(profile)

    # Connect!
    factory.connect(ip, 25565)


def main(ip):
    dotenv.load_dotenv('profile.env')
    try:
        run(ip)
        reactor.run()
    except Exception as e:
        print(e)
    if 'tablist' in jsoninfo and len(jsoninfo['tablist'])!=0:
        aPlayer = jsoninfo['tablist'][0]
        if aPlayer['uuid']==str(uuid.from_offline_player(aPlayer['name'])):
            jsoninfo['offlineMode']=True
        else:
            jsoninfo['offlineMode']=False
    return jsoninfo

def getByUUID(list, uuid):
    for item in list:
        if item['uuid']==uuid:
            return item

if __name__ == "__main__":
    import sys
    print(main(sys.argv[1]))