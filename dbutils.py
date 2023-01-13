import re, sqlite3, time

"""
table make cmd ....

CREATE TABLE ping(
  time INTEGER,
  ip TEXT,
  protvers INTEGER,
  maxplayers INTEGER,
  desc TEXT,
  iscolored INTEGER,
  version TEXT,
  ismodded INTEGER
)


"""

def parse(obj):
    if isinstance(obj, str):
        return obj, str(obj).__contains__("'color': ") or str(obj).__contains__("\u00a7")
    if isinstance(obj, list):
        return "".join((parse(e)[0] for e in obj))
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

def addPing(pingdict):
    descinfo = parse(pingdict['description'])
    data = [
    time.time_ns(),
    pingdict['ip'],
    pingdict['version']['protocol'],
    pingdict['players']['max'],
    descinfo[0],
    descinfo[1],
    pingdict['version']['name'],
    'forgeData' in pingdict
    ]

    tmpdata = []
    for item in data:
        if isinstance(item, bool):
            item = int(item)
        tmpdata.append(stripString(str(item)))
    data = tuple(tmpdata)
    # SQLITE3 data part
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("""
    INSERT INTO ping VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    if 'sample' in pingdict['players']:
      rowid = c.lastrowid
      for player in pingdict['players']['sample']:
        c.execute('INSERT INTO pingplayers VALUES(?, ?, ?)', (str(rowid), stripString(player['id']), stripString(player['name'])))
    conn.commit()
    print(data)