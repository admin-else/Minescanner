import socket, os, concurrent.futures, WebsiteScrapers, pinger, multiprocessing, dotenv, time, sqlite3, re
from util import log

conn = sqlite3.connect('servers.db')

def parseDesc(obj):
    text = obj['text']
    if 'extra' in obj:
        for obj in obj['extra']:
            text+=obj['text']
    isColored = False
    if "'color':" in str(obj) or "§" in str(obj):
        isColored = True
    return text, isColored

def getSavePingDescription(obj):
    badstring, hasColor = parseDesc(obj)
    return stripString(badstring), hasColor

def stripString(text):
    return re.sub(r"[^a-z0-9. ]", "", text.lower().rstrip())

def addPing(ip, port, time, pingdict):
    if 'description' not in pingdict or 'version' not in pingdict:
        return False
    if 'protocol' not in pingdict['version'] or 'name' not in pingdict['version']:
        return False
    if 'online' not in pingdict['players'] or 'max' not in pingdict['players']:
        return False
    
    values = [ip, port, time]
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


    c = conn.cursor()
    c.execute('''
    INSERT INTO ping(ip, port, time, desc, isColored, icon, protvers, verstext, pOn, pMax, chatreportingstatus, ismodded)
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
    conn.commit()
    return True

def masscan(ips):
    lines = [f'range = {ip}\n' for ip in ips]

    if os.path.exists('./masscan.conf'):
        os.remove('./masscan.conf')
    with open('./masscan.conf','w') as f:
        f.writelines(lines)
    os.system('sudo masscan -c ./masscan.conf -p 25565 --excludefile ./excludefile.txt --wait=3 --rate {} -oL output.txt'.format(os.getenv('MASSCANRATE')))
    with open('output.txt', 'r') as f:
        lines = f.readlines()
    ips = [
        line.split(' ')[3]
        for line in lines
        if line.startswith('open tcp')
    ]
    return ips

def try2ping(ip, port = 25565):
    try:
        p = multiprocessing.Process(target=try2pingandsave, args=(ip, port))
        p.start()
        p.join(2)
        if p.is_alive:
            p.terminate()
    except Exception as e:
        print(e)

def try2pingandsave(ip, port = 25565):
    try:
        ping = pinger.main(ip, port=port)
        if 'version' in ping and bool(int(os.getenv('IGNORE_FAKE_SERVERS'))) and ping['version']['name'] in ['TCPShield.com','COSMIC GUARD']:
            log(f'§cGarbage ping on §b{ip}:{port}§c.', 2)
            return
        if addPing(ip, port, time.time_ns(), ping):
            log(f'§aSuccessful ping on §b{ip}:{port}§a.', 1)
            log('§5 MOTD: §b{}§5 \n Version: §b{}§5 \n (§b{}§5,§b{}§5)'.format(parseDesc(ping['description'])[0], ping['version']['name'], ping['players']['online'], ping['players']['max']), 3)
        else:
            log(f'§cUnsuccessful ping on §b{ip}:{port}§c.', 2)
    except Exception as e:
        log(f'§cPing on §b{ip}:{port}§c errored with:', 2)
        log(str(e), 2)

    
def try2join(ip, port = 25565):
    try:
        p = multiprocessing.Process(target=pinger.main, args=(ip, port))
        p.start()
        p.join(5)
        if p.is_alive:
            p.terminate()
    except Exception as e:
        print(e)

def tcpping(ip):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(0.05)
        port = 25565
        if ':' in ip:
            ip, port = str(ip).split(':',maxsplit=2)
        ip = socket.gethostbyname(ip)
        if client.connect_ex((ip, int(port))) == 0:
            log(f'§aSuccsesfuly TCPpinged §b{ip}:{port}§a.', 1)
            return ".".join(str(ip).split(".")[:3])
        else:
            log(f'§cUnsuccsesfuly TCPpinged §b{ip}§c.', 2)
    except Exception as e:
        log(f'§cTCPping erroed of ip §b{ip}§c with:',2)
        log(str(e), 2)


dotenv.load_dotenv('profile.env')

start_time = time.time_ns()

try:
    addrslist = WebsiteScrapers.getips()
except Exception as e:
    print(e)
    exit()

iprages = []
print('Done getting all good ping-able domains')
print('Started pinging',len(addrslist),'ips.')
with concurrent.futures.ProcessPoolExecutor(max_workers=70) as executor:
    for range in executor.map(tcpping, addrslist):
        if range!=None and range not in iprages:
            iprages.append(range)
print('done pinging ips')
iplist = masscan([f'{iprange}.0-{iprange}.255' for iprange in iprages])
if os.getenv('THREADPINGS') == '0':
    for i, addr in enumerate(iplist):
        try2ping(addr)
        print(f' {i} / {len(iplist)} - {100*i/len(iplist)}% - {addr}')
else:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(try2ping, iplist)

conn.close()

    
print('START TIME IN UNIX:'+str(start_time))

