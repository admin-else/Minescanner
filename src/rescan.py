import time, sqlite3, os, dotenv, multiprocessing, dbutils
from mcstatus import JavaServer
from util import log
import concurrent.futures

conn = sqlite3.connect('/home/simon/src/python/minescaner/src/servers.db')
dotenv.load_dotenv('profile.env')

def try2ping(ip):
    port = 25565
    if ':' in ip:
        port = int(ip.split(':')[1])
        ip = ip.split(':')[0]
    c = conn.cursor()
    try:
        p = multiprocessing.Process(target=dbutils.try2pingandsave, args=(c, ip, port))
        p.start()
        p.join(2)
        if p.is_alive:
            p.terminate()
        conn.commit()
    except Exception as e:
        print(e)

def main():
    global c
    c = conn.cursor()
    c.execute("""SELECT ip FROM ping WHERE uptodate = 1""")
    iplist = [v[0] for v in c.fetchall()]
    print(iplist)
    if os.getenv('THREADPINGS') == '0':
            for i, addr in enumerate(iplist):
                try2ping(addr)
                log(f'§b {i} / {len(iplist)} - {100*i/len(iplist)}% - {addr}', 1)
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(try2ping, iplist)

if __name__=='__main__':
    log('§aRescan started!', 0)
    main()
    log('§aRescan ended.', 0)