import pinger, time, sqlite3, os, dotenv, multiprocessing
from util import log
import concurrent.futures

conn = sqlite3.connect('servers.db')
dotenv.load_dotenv('profile.env')

def parseDesc(obj):
    text = obj['text']
    if 'extra' in obj:
        for obj in obj['extra']:
            text+=obj['text']
    isColored = False
    if "'color':" in str(obj) or "§" in str(obj):
        isColored = True
    return text, isColored

def addPing(ip, port, time, pingdict):
    if 'description' not in pingdict or 'version' not in pingdict:
        return False
    if 'protocol' not in pingdict['version'] or 'name' not in pingdict['version']:
        return False
    if 'online' not in pingdict['players'] or 'max' not in pingdict['players']:
        return False
    
    if port != 25565:
        ip+=':'+str(port)

    values = [ip, time]
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


    c = conn.cursor()
    c.execute('''
    UPDATE ping SET uptodate = 0 WHERE ip = ?
    ''', (ip, ))
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
    conn.commit()
    return True

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

def try2ping(ip):
    port = 25565
    if ':' in ip:
        port = ip.split(':')[1]
        ip = ip.split(':')[0]
    try:
        p = multiprocessing.Process(target=try2pingandsave, args=(ip, port))
        p.start()
        p.join(2)
        if p.is_alive:
            p.terminate()
    except Exception as e:
        print(e)

if __name__=='__main__':
    
    c = conn.cursor()
    c.execute("""SELECT ip FROM ping""")
    iplist = [v[0] for v in c.fetchall()]
    c.close()

    print(iplist)

    if os.getenv('THREADPINGS') == '0':
            for i, addr in enumerate(iplist):
                try2ping(addr)
                log(f'§b {i} / {len(iplist)} - {100*i/len(iplist)}% - {addr}', 1)
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(try2ping, iplist)

    log('§aDone rescanning.', 0)