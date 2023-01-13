import re, time, time

gamemoderegex = {0: "Survival", 1: "Creative", 2: "Adventure", 3: "Spectator"}

versionregex = [('1.19.3', 761),
                ('1.19.2', 760),
                ('1.19.1', 760),
                ('1.19', 759),
                ('1.18.2', 758),
                ('1.18.1', 757),
                ('1.18', 757),
                ('1.17.1', 756),
                ('1.17', 755),
                ('1.16.5', 754),
                ('1.16.4', 754),
                ('1.16.3', 753),
                ('1.16.2', 751),
                ('1.16.1', 736),
                ('1.16', 735),
                ('1.15.2', 578),
                ('1.15.1', 575),
                ('1.15', 573),
                ('1.14.4', 498),
                ('1.14.3', 490),
                ('1.14.2', 485),
                ('1.14.1', 480),
                ('1.14', 477),
                ('1.13.2', 404),
                ('1.13.1', 401),
                ('1.13', 393),
                ('1.12.2', 340),
                ('1.12.1', 338),
                ('1.12', 335),
                ('1.11.2', 316),
                ('1.11.1', 316),
                ('1.11', 315),
                ('1.10.2', 210),
                ('1.10.1', 210),
                ('1.10', 210),
                ('1.9.4', 110),
                ('1.9.3', 110),
                ('1.9.2', 109),
                ('1.9.1', 108),
                ('1.9', 107),
                ('1.8.9', 47),
                ('1.8.8', 47),
                ('1.8.7', 47),
                ('1.8.6', 47),
                ('1.8.5', 47),
                ('1.8.4', 47),
                ('1.8.3', 47),
                ('1.8.2', 47),
                ('1.8.1', 47),
                ('1.8', 47),
                ('1.7.10', 5),
                ('1.7.9', 5),
                ('1.7.8', 5),
                ('1.7.7', 5),
                ('1.7.6', 5),
                ('1.7.5', 4),
                ('1.7.4', 4),
                ('1.7.3', 4),
                ('1.7.2', 4)]

def translate2versionNumber(version):
    for vers in versionregex:
        if vers[0]==version:
            return vers[1]
    return -1

def serverTupleToDict(servertuple):
    return {
        # general info
        'time': servertuple[0],
        'ip': servertuple[1],
        'port': servertuple[2],
        # ping info
        'desc': servertuple[3],
        'isColored': bool(servertuple[4]),
        'protvers': servertuple[5],
        'version': servertuple[6],
        'ismodded': bool(servertuple[7]),
        'maxplayers': servertuple[8],
        # join info
        'kickmsg': servertuple[9],
        'brand': servertuple[10],
        'difficulty': servertuple[11],
        'gamemode': gamemoderegex[servertuple[12]],
        'hardcore': servertuple[13],
        'hashedSeed': servertuple[14],
        'offlineMode': bool(servertuple[15]),
        'commands': servertuple[16]
    }

def parse(obj):
    if isinstance(obj, str):
        return obj, str(obj).__contains__("'color': ") or str(obj).__contains__("\u00a7")
    if isinstance(obj, dict):
        hasColor = str(obj).__contains__("'color': ") or str(obj).__contains__("\u00a7")
        text = ""
        if "text" in obj:
            text += re.sub("\u00A7.", "", obj["text"])
        if "extra" in obj:
            text += parse(obj["extra"])
        return text, hasColor

def getSavePingDescription(obj):
    badstring, hasColor = parse(obj)
    return stripString(badstring), hasColor

def stripString(text):
    return re.sub(r"[^a-z0-9. ]", "", text.lower().rstrip())

def addServer(pingdict, joindict, conn):
    descinfo = parse(pingdict['description'])
    data = [
    # general info 
    time.time_ns(),
    pingdict['ip'],
    pingdict['port'],
    # ping scan
    descinfo[0],
    descinfo[1],
    pingdict['version']['protocol'],
    pingdict['version']['name'],
    'forgeData' in pingdict or 'modpackData' in pingdict,
    pingdict['players']['max'],
    # Join scan
    joindict['kickmsg'],
    joindict['brand'],
    joindict['difficulty'],
    joindict['gamemode'],
    joindict['hardcore'],
    joindict['hashedSeed'],
    joindict['offlineMode'],
    joindict['commands']]

    tmpdata = []
    for item in data:
        if isinstance(item, bool):
            item = int(item)
        tmpdata.append(stripString(str(item)))
    data = tuple(tmpdata)
    # SQLITE3 data part
    c = conn.cursor()
    c.execute("""
    INSERT INTO ping VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    if 'sample' in pingdict['players']:
      rowid = c.lastrowid
      for player in pingdict['players']['sample']:
        c.execute('INSERT INTO pingplayers VALUES(?, ?, ?)', (str(rowid), stripString(player['id']), stripString(player['name'])))
    c.close()

async def server(conn,
                 description: str = None,
                 iscolored: bool = None,
                 ismodded: bool = None,
                 version: str = None,
                 versiontext: str = None):
    response = {}
    sqlcommand = 'SELECT * FROM ping WHERE maxplayers <> 0 '
    sqlarguments = []
    searchoptions= ''
    if description!=None:
        sqlcommand+='AND desc LIKE ? '
        sqlarguments.append(f'%{description}%')
        searchoptions+=f'description contains {description}, '
    if iscolored!=None:
        sqlcommand+='AND iscolored = ? '
        if iscolored:
            sqlarguments.append('1')
            searchoptions+='description is colored, '
        else:
            sqlarguments.append('0')
            searchoptions+='description is not colored, '
    if ismodded!=None:
        sqlcommand+='AND ismodded = ? '
        if ismodded:
            sqlarguments.append('1')
            searchoptions+='server is modded, '
        else:
            sqlarguments.append('0')
            searchoptions+='server is not modded, '
    if version!=None:
        sqlcommand+='AND protvers = ? '
        if translate2versionNumber(version)==-1:
            response.clear()
            response['error'] = f'Iam sorry but i dont know any version called "{version}".\nU can try a non snapshot from this https://wiki.vg/Protocol_version_numbers (and also 1.7.3 that isnt listed there for some reason).'
            return response
        searchoptions+=f'version is {version}, '
        sqlarguments.append(str(translate2versionNumber(version)))
    if versiontext!=None:
        sqlcommand+='AND version LIKE ? '
        searchoptions+=f'version contains {versiontext}, '
        sqlarguments.append(f'%{versiontext}%')
    sqlcommand+='ORDER BY ip DESC'
    
    c = conn.cursor()

    c.execute(sqlcommand, tuple(sqlarguments))
    reponse                  = {}
    reponse['count']         = 0
    reponse['servers']       = c.fetchall()
    reponse['searchoptions'] = searchoptions

    c.close()

    if len(reponse['servers'])==0:
        response['error'] = f'the scan u did did not yield any results ):'
    return response

import serverinfo
import pinger

ip, port = 'localhost', 25565

print(serverinfo.main('98.128.204.204', 25565))
print(pinger.main('mc.hypixel.net', 25565))


