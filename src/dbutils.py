import sqlite3

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

def addPing(pingdict, c):
    if 'description' not in pingdict or 'version' not in pingdict:
        return False
    if 'protocol' not in pingdict['version'] or 'name' not in pingdict['version']:
        return False
    if 'online' not in pingdict['players'] or 'max' not in pingdict['players']:
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
    values.append(1)

    c.execute('''
    UPDATE ping SET uptodate = 0 WHERE ip = ?
    ''', (pingdict['ip'], ))
    c.execute('''
    INSERT INTO ping(ip, time, desc, isColored, icon, protvers, verstext, pOn, pMax, chatreportingstatus, ismodded, uptodate)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(values))

    if 'sample' in pingdict['players']:
        pingid = str(c.lastrowid)
        for player in pingdict['players']['sample']:
            c.execute('''
            INSERT INTO pingPlayers(pingid, name, uuid)
            VALUES(?, ?, ?)
            ''', (pingid, player['name'], player['id']))
    c.close()
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