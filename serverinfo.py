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


defaultcommads = ['advancement',
'attribute',
'ban',
'ban-ip',
'banlist',
'bossbar',
'clear',
'clone',
'data',
'datapack',
'debug',
'defaultgamemode',
'deop',
'difficulty',
'effect',
'enchant',
'execute',
'experience',
'fill',
'forceload',
'function',
'gamemode',
'gamerule',
'give',
'help',
'item',
'jfr',
'kick',
'kill',
'list',
'locate',
'loot',
'me',
'msg',
'op',
'pardon',
'pardon-ip',
'particle',
'perf',
'place',
'playsound',
'recipe',
'reload',
'save-all',
'save-off',
'save-on',
'say',
'schedule',
'scoreboard',
'seed',
'setblock',
'setidletimeout',
'setworldspawn',
'spawnpoint',
'spectate',
'spreadplayers',
'stop',
'stopsound',
'summon',
'tag',
'team',
'teammsg',
'teleport',
'tell',
'tellraw',
'time',
'title',
'tm',
'tp',
'trigger',
'w',
'weather',
'whitelist',
'worldborder',
'xp']

command_propertie_id_regex = [
    (0, 'brigadier:bool'),
    (1, 'brigadier:float'),
    (2, 'brigadier:double'),
    (3, 'brigadier:integer'),
    (4, 'brigadier:long'),
    (5, 'brigadier:string'),
    (6, 'minecraft:entity'),
    (7, 'minecraft:game_profile'),
    (8, 'minecraft:block_pos'),
    (9, 'minecraft:column_pos'),
    (10, 'minecraft:vec3'),
    (11, 'minecraft:vec2'),
    (12, 'minecraft:block_state'),
    (13, 'minecraft:block_predicate'),
    (14, 'minecraft:item_stack'),
    (15, 'minecraft:item_predicate'),
    (16, 'minecraft:color'),
    (17, 'minecraft:component'),
    (18, 'minecraft:message'),
    (19, 'minecraft:nbt'),
    (20, 'minecraft:nbt_tag'),
    (21, 'minecraft:nbt_path'),
    (22, 'minecraft:objective'),
    (23, 'minecraft:objective_criteria'),
    (24, 'minecraft:operation'),
    (25, 'minecraft:particle'),
    (26, 'minecraft:angle'),
    (27, 'minecraft:rotation'),
    (28, 'minecraft:scoreboard_slot'),
    (29, 'minecraft:score_holder'),
    (30, 'minecraft:swizzle'),
    (31, 'minecraft:team'),
    (32, 'minecraft:item_slot'),
    (33, 'minecraft:resource_location'),
    (34, 'minecraft:mob_effect'),
    (35, 'minecraft:function'),
    (36, 'minecraft:entity_anchor'),
    (-1, 'minecraft:range'),
    (37, 'minecraft:int_range'),
    (38, 'minecraft:float_range'),
    (39, 'minecraft:item_enchantment'),
    (40, 'minecraft:entity_summon'),
    (41, 'minecraft:dimension'),
    (-1, 'minecraft:nbt_compound_tag'),
    (42, 'minecraft:time'),
    (43, 'minecraft:resource_or_tag'),
    (44, 'minecraft:resource'),
    (45, ' 	(added in 1.19) Template mirror'),
    (46, ' 	(added in 1.19) Template rotation'),
    (47, 'minecraft:uuid'),
]

class ServerInfoProtocol(SpawningClientProtocol):

    def packet_login_encryption_request(self, buff):
        jsoninfo['offlineMode']=False
        super().packet_login_encryption_request(buff)

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
                    data = {
                        'uuid': p_uuid,
                        'name': p_player_name,
                        'properties': p_properties,
                        'gamemode': p_gamemode,
                        'ping': p_ping,
                        'display_name': p_display_name
                    }
                    if data not in self.players:
                        self.players.append(data)
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

    def packet_declare_commands(self, buff):
        global jsoninfo
        jsoninfo['commands'] = ''
        count = buff.unpack_varint()
        for i in range(count):
            flag = buff.unpack('b')
            node_type = flag & 0x03
            childcount = buff.unpack_varint()
            clildrenids = []
            redirect_node = None
            name = None
            suggestion_type = None
            parser_id = None
            for _ in range(childcount):
                clildrenids.append(buff.unpack_varint())
            if flag & 0x08 != 0:
                redirect_node = buff.unpack_varint()
            if node_type == 1 or node_type == 2:
                name = buff.unpack_string()
            if node_type == 2:
                argument_type_id = -1
                if self.protocol_version <= 758:
                    argument_type_mc_name = buff.unpack_string()
                    for i, arg_type in enumerate(command_propertie_id_regex):
                        if arg_type[1] == argument_type_mc_name:
                            argument_type_id = i
                else:
                    argument_type_mc_id = buff.unpack('i')
                    for i, arg_type in enumerate(command_propertie_id_regex):
                        if arg_type[1] == argument_type_mc_id:
                            argument_type_id =  i
                # TODO DO STUFF (MAKE prpeties parser reader)
                return
            if flag & 0x10 != 0:
                suggestion_type = buff.unpack_string()
            if name != None and '§' not in name and name not in defaultcommads and 'minecraft:' not in name:
                jsoninfo['commands']+='§'+name
            
            
        rootindex = buff.unpack_varint()

class ChatLoggerFactory(ClientFactory):
    protocol = ServerInfoProtocol


@defer.inlineCallbacks
def run(ip, port):
    profile = yield Profile.from_token('',os.getenv('MC_TOKEN'),os.getenv('MC_NAME'),os.getenv('MC_UUID')) # U wont get my accses token (;

    # Create factory
    factory = ChatLoggerFactory(profile)

    # Connect!
    factory.connect(ip, port)


def main(ip, port = 25565):
    dotenv.load_dotenv('profile.env')
    global jsoninfo
    jsoninfo = {}
    jsoninfo['offlineMode']=True
    try:
        run(ip, port)
        reactor.run()
    except Exception as e:
        print(e)
    return jsoninfo

if __name__ == "__main__":
    import sys
    print(main(sys.argv[1]))