import os, datetime
from pprint import pprint
from itertools import islice, chain, repeat

def color(msg):
    msg = msg.replace('§0', '\033[0;30m')
    msg = msg.replace('§1', '\033[0;34m')
    msg = msg.replace('§2', '\033[0;32m')
    msg = msg.replace('§3', '\033[0;36m')
    msg = msg.replace('§4', '\033[0;31m')
    msg = msg.replace('§5', '\033[0;35m')
    msg = msg.replace('§6', '\033[0;33m')
    msg = msg.replace('§7', '\033[0;37m')
    msg = msg.replace('§8', '\033[0;90m')
    msg = msg.replace('§9', '\033[0;94m')
    msg = msg.replace('§a', '\033[0;92m')
    msg = msg.replace('§b', '\033[0;96m')
    msg = msg.replace('§c', '\033[0;91m')
    msg = msg.replace('§d', '\033[0;95m')
    msg = msg.replace('§e', '\033[0;93m')
    msg = msg.replace('§f', '')
    msg = msg.replace('§g', '')
    msg = msg.replace('§k', '\033[8m')
    msg = msg.replace('§l', '\033[1m')
    msg = msg.replace('§m', '\033[9m')
    msg = msg.replace('§n', '\033[4m')
    msg = msg.replace('§o', '\033[3m')
    msg = msg.replace('§r', '\033[0m')
    msg = msg.replace('Â', '')
    msg = msg.replace('§c', '\033[H\033[J')
    return msg

def chunk_pad(it, size, padval=None):
    it = chain(iter(it), repeat(padval))
    return iter(lambda: tuple(islice(it, size)), (padval,) * size)

def s_to_dict(lst):
    if lst==None:
        return None
    return {'ip': lst[0],
            'time': str(datetime.datetime.fromtimestamp(lst[1] // 1000000000)),
            'description': lst[2],
            'players': {
                'max': lst[8],
                'online': lst[7]
            },
            'version': {
                'name': lst[6],
                'protocol': lst[5]
            },
            'favicon': lst[4]
            }
              

def log(msg, loglevel, pretty = False, end = '\n', colored = True):
    loglevelenv = os.getenv('LOG_LEVEL')
    if loglevelenv==None or loglevel<=int(loglevelenv):
        msg = str(msg)+'§r'
        if colored:
            msg = color(msg)
        if pretty:
            pprint(msg)
        else:
            print(msg, end=end)