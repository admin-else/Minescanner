import re, sqlite3, time

"""
table make cmd ....


   ** PING TABLE **
          name;   type;             exampel; info
          time;    INT; 1670072676534401627; unix ns time.time_ns()
            ip; STRING;             8.8.8.8; The pinged ip
  protocolvers;    INT;                 760; [Protocol version](https://wiki.vg/Protocol_version_numbers)
    maxplayers;    INT;                  20; max players
   description; STRING;         rpg anarchy; VERY striped down string(anti sql and short is good) (:
   isdescolord;    INT;                   1; is colored (if it contains color: or \u00a7) 1 if it is 0 if not
       version; STRING;        Paper 1.19.2; Server version string (also striped down)
      ismodded;    INT;                   0; if server gives forgedata

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

pingdictping = {
        "description": {
          "extra": [
            {
              "color": "gold",
              "text": " "
            },
            {
              "color": "#ff9911",
              "text": " "
            },
            {
              "color": "#ff8822",
              "text": " "
            },
            {
              "color": "#ff7733",
              "text": "\u2726"
            },
            {
              "color": "#ff6644",
              "text": " "
            },
            {
              "bold": True,
              "color": "white",
              "text": "T"
            },
            {
              "bold": True,
              "color": "#ffffc6",
              "text": "H"
            },
            {
              "bold": True,
              "color": "#ffff8e",
              "text": "E"
            },
            {
              "bold": True,
              "color": "yellow",
              "text": "G"
            },
            {
              "bold": True,
              "color": "#fff147",
              "text": "O"
            },
            {
              "bold": True,
              "color": "#ffe339",
              "text": "L"
            },
            {
              "bold": True,
              "color": "#ffd52b",
              "text": "D"
            },
            {
              "bold": True,
              "color": "#ffc61c",
              "text": "E"
            },
            {
              "bold": True,
              "color": "#ffb80e",
              "text": "N"
            },
            {
              "bold": True,
              "color": "gold",
              "text": "E"
            },
            {
              "bold": True,
              "color": "#ff9f0b",
              "text": "G"
            },
            {
              "bold": True,
              "color": "#ff9515",
              "text": "G"
            },
            {
              "bold": True,
              "color": "#ff8a20",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff802b",
              "text": "\u2726"
            },
            {
              "bold": True,
              "color": "#ff7535",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff6a40",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff604a",
              "text": " "
            },
            {
              "text": "\n"
            },
            {
              "bold": True,
              "color": "red",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff5753",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff5951",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff5b4f",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff5d4d",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff5e4c",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff604a",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff6248",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff6446",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff6644",
              "text": "1"
            },
            {
              "bold": True,
              "color": "#ff6842",
              "text": "."
            },
            {
              "bold": True,
              "color": "#ff6a40",
              "text": "1"
            },
            {
              "bold": True,
              "color": "#ff6c3e",
              "text": "9"
            },
            {
              "bold": True,
              "color": "#ff6e3c",
              "text": "."
            },
            {
              "bold": True,
              "color": "#ff6f3b",
              "text": "2"
            },
            {
              "bold": True,
              "color": "#ff7139",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff7337",
              "text": "N"
            },
            {
              "bold": True,
              "color": "#ff7535",
              "text": "o"
            },
            {
              "bold": True,
              "color": "#ff7733",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff7931",
              "text": "R"
            },
            {
              "bold": True,
              "color": "#ff7b2f",
              "text": "e"
            },
            {
              "bold": True,
              "color": "#ff7d2d",
              "text": "s"
            },
            {
              "bold": True,
              "color": "#ff7f2b",
              "text": "e"
            },
            {
              "bold": True,
              "color": "#ff802a",
              "text": "t"
            },
            {
              "bold": True,
              "color": "#ff8228",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff8426",
              "text": "S"
            },
            {
              "bold": True,
              "color": "#ff8624",
              "text": "u"
            },
            {
              "bold": True,
              "color": "#ff8822",
              "text": "r"
            },
            {
              "bold": True,
              "color": "#ff8a20",
              "text": "v"
            },
            {
              "bold": True,
              "color": "#ff8c1e",
              "text": "i"
            },
            {
              "bold": True,
              "color": "#ff8e1c",
              "text": "v"
            },
            {
              "bold": True,
              "color": "#ff901a",
              "text": "a"
            },
            {
              "bold": True,
              "color": "#ff9119",
              "text": "l"
            },
            {
              "bold": True,
              "color": "#ff9317",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9515",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9713",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9911",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9b0f",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9d0d",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ff9f0b",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ffa109",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ffa208",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ffa406",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ffa604",
              "text": " "
            },
            {
              "bold": True,
              "color": "#ffa802",
              "text": " "
            }
          ],
          "text": "             "
        },
        "enforcesSecureChat": False,
        "players": {
          "max": 100,
          "online": 0
        },
        "previewsChat": False,
        "version": {
          "name": "Paper 1.19.2",
          "protocol": 760
        },
        "ip": "thegoldenegg.online",
        "time": "2022-12-03 21:35:39.204514"
      }

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
        c.execute('INSERT INTO pingplayers VALUES(?, ?, ?)', (str(rowid), stripString(player['uuid']), stripString(player['name'])))
    conn.commit()
    print(data)