import sqlite3, dbutils, time, os
from util import log
from mcstatus import JavaServer

def doPing(ip, port = 25565):
    serv = JavaServer(ip, port=port)
    ping = {}
    ping['ip'] = ip+':'+str(port)
    ping['time'] = time.time_ns()
    ping['plugins'] = None
    try:
        ping.update(serv.status().raw)
        compressed_plugins = ''
        for pl in serv.query().software.plugins:
            compressed_plugins+='§'+pl
        ping['plugins'] = compressed_plugins
    except ConnectionRefusedError or BrokenPipeError:
        log('§cServer §b{}§c broke a pipe or did not exsist.'.format(ping['ip']), 2)
        return
    return ping

def try2pingandsave(conn, ip, port = 25565):
    try:
        ping = doPing(ip, port=port)
        c = conn.cursor()
        if ping==None:
            updateUpToDate(ip, c)
            log('§cServer §b{}§c broke a pipe or did not exsist.'.format(ping['ip']), 2)
            return
        if dbutils.isPingVaild(ping) == False:
            return
        if 'version' in ping and os.getenv('IGNORE_FAKE_SERVERS')=='1' and ping['version']['name'] in ['TCPShield.com','COSMIC GUARD']:
            log(f'§cGarbage ping on §b{ip}:{port}§c.', 2)
            return
        if dbutils.addPing(ping, c):
            log(f'§aSuccessful ping on §b{ip}:{port}§a.', 1)
            log('§5 MOTD: \n§b{}§5 \n Version: §b{}§5 \n (§b{}§5,§b{}§5)'.format(dbutils.parseDesc(ping['description'])[0], ping['version']['name'], ping['players']['online'], ping['players']['max']), 3)
        else:
            log(f'§cUnsuccessful ping on §b{ip}:{port}§c.', 2)
        conn.commit()
    except Exception as e:
        log(f'§cPing on §b{ip}:{port}§c errored with:', 2)
        log(str(e), 2)

def parseDesc(obj):
    if 'text' not in obj:
        return '', False
    text = obj['text']
    if 'extra' in obj:
        for obj in obj['extra']:
            text+=obj['text']
    isColored = False
    if "'color':" in str(obj) or "§" in str(obj):
        isColored = True
    return text, isColored

def isPingVaild(pingdict):
    if pingdict == None:
        return False
    if 'description' not in pingdict or 'version' not in pingdict:
        return False
    if 'protocol' not in pingdict['version'] or 'name' not in pingdict['version']:
        return False
    if 'online' not in pingdict['players'] or 'max' not in pingdict['players']:
        return False
    return True

def updateUpToDate(ip, c):
    c.execute('''
    UPDATE ping SET uptodate = 0 WHERE ip = ?
    ''', (ip, ))

def addPing(pingdict, c):
    if isPingVaild==False:
        return False

    values = [pingdict['ip'], pingdict['time']]
    desc = parseDesc(pingdict['description'])
    values.append(desc[0])
    values.append(desc[1])
    if 'favicon' in pingdict:
        values.append(pingdict['favicon'])
    else:
        values.append(None)
    values.append(pingdict['version']['protocol'])
    values.append(pingdict['version']['name'])
    values.append(pingdict['players']['online'])
    values.append(pingdict['players']['max'])
    if 'enforcesSecureChat' in pingdict:
        if pingdict['enforcesSecureChat']:
            values.append(2)
        else:
            values.append(1)
    else:
        values.append(0)
    values.append('forgeData' in pingdict or 'modPackData' in pingdict)
    values.append(pingdict['plugins'])
    values.append(1)
    updateUpToDate(pingdict['ip'], c)
    c.execute('''
    INSERT INTO ping(ip, time, desc, isColored, icon, protvers, verstext, pOn, pMax, chatreportingstatus, ismodded, plugins, uptodate)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(values))

    if 'sample' in pingdict['players']:
        pingid = str(c.lastrowid)
        for player in pingdict['players']['sample']:
            c.execute('''
            INSERT INTO pingPlayers(pingid, name, uuid)
            VALUES(?, ?, ?)
            ''', (pingid, player['name'], player['id']))
    return True

def addJoinScan(pingdata, c=None):
    if c==None:
        conn = sqlite3.connect('servers.db')
        c = conn.cursor()
    # anti key errors
    antikeyerror = {'offlineMode': None,
                'ip': None,
                'hardcore': None,
                'hashedSeed': None, 
                'brand': None, 
                'difficulty': None, 
                'commands': None, 
                'daytime': None, 
                'joinTime': None, 
                'worlds': None,
                'tablist': None,
                'tablistfooter': None,
                'tablistheader': None
                }
    antikeyerror.update(pingdata)
    pingdata = antikeyerror

    # Formating
    worlds = ''
    if pingdata['worlds']!=None:
        for world in pingdata['worlds']:
            worlds+=world+'§'
    pingdata['worlds'] = worlds
    # SQLing!!!!
    if 'kick' in pingdata:
        c.execute('UPDATE faildscan SET uptodate = 0 WHERE ip = ?', (pingdata['ip'], ))
        c.execute('INSERT INTO faildscan(ip, time, message, uptodate) VALUES (?, ?, ?, 1)', (pingdata['ip'], pingdata['joinTime'], pingdata['kick']))
    elif 'gamemode' in pingdata:
        c.execute('UPDATE joinscan SET uptodate = 0 WHERE ip = ?', (pingdata['ip'], ))
        c.execute('INSERT INTO joinscan(ip, joinTime, offlineMode, hardcore, gamemode, hashedSeed, worlds, brand, difficulty, commands, daytime, tablistfooter, tablistheader, uptodate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)',
        (
            pingdata['ip'],
            pingdata['joinTime'],
            pingdata['offlineMode'],
            pingdata['hardcore'],
            pingdata['gamemode'],
            pingdata['hashedSeed'],
            pingdata['worlds'],
            pingdata['brand'],
            pingdata['difficulty'],
            pingdata['commands'],
            pingdata['daytime'],
            pingdata['tablistfooter'],
            pingdata['tablistheader'],
        ))
    print(pingdata['ip'])
    # Commit if needed
    if 'conn' in locals():
        conn.commit()
        conn.close()
        del conn