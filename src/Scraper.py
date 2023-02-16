import socket, os, concurrent.futures, WebsiteScrapers, multiprocessing, dotenv, time, sqlite3, re, dbutils, ipwhois
from util import log
from ipwhois import IPWhois

conn = sqlite3.connect('servers.db')

def iptotuple(ip):
    return tuple([int(v) for v in ip.split('.')])

def getRangesFromIps(data):
    rangelist = []
    datalen = len(data)
    for i, ip in enumerate(data):
        if ':' in ip:
            ip = ip.split(':')[0]
        ipp = iptotuple(ip)
        isInRange = False
        for range in rangelist:
            if range[0]<=ipp[0] and range[4]>=ipp[0]:
                if range[1]<=ipp[1] and range[5]>=ipp[1]:
                    if range[2]<=ipp[2] and range[6]>=ipp[2]:
                        if range[3]<=ipp[3] and range[7]>=ipp[3]:
                            isInRange = True
                            break
        if isInRange:
            continue
        lookup = IPWhois(ip)
        try:
            lookup_rdap = lookup.lookup_rdap()
            start_adrr = lookup_rdap['network']['start_address']
            end_adrr = lookup_rdap['network']['end_address']
            rangelist.append(iptotuple(start_adrr) + iptotuple(end_adrr))
            log(f'§b{round(i/datalen*100, 2)}§a% - §b{i}§a/§b{datalen}§a - §b{start_adrr}§a-§b{end_adrr}§a', 1)
        except ipwhois.exceptions.HTTPRateLimitError:
            log('§cIt seems like u have been rate limitied so i gonna wait for a few seconds', 0)
            time.sleep(int(os.getenv('WHOIS_RATE_LIMIT_TIME')))
    return [f'{p1}.{p2}.{p3}.{p4}-{p5}.{p6}.{p7}.{p8}' for (p1, p2, p3, p4, p5, p6, p7, p8) in rangelist]

def stripString(text):
    return re.sub(r"[^a-z0-9. ]", "", text.lower().rstrip())

def masscan(ips):
    lines = [f'range = {ip}\n' for ip in ips]

    if os.path.exists('./masscan.conf'):
        os.remove('./masscan.conf')
    with open('./masscan.conf','w') as f:
        f.writelines(lines)
    """os.system('sudo masscan -c ./masscan.conf -p 25565 --excludefile ./excludefile.txt --wait=3 --rate {} -oL output.txt'.format(os.getenv('MASSCANRATE')))
    
    with open('output.txt', 'r') as f:
        lines = f.readlines()
    ips = [
        line.split(' ')[3]
        for line in lines
        if line.startswith('open tcp')
    ]"""
    return ips

def try2ping(ip, port = 25565):
    try:
        p = multiprocessing.Process(target=dbutils.try2pingandsave, args=(ip, port))
        p.start()
        p.join(2)
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
            ip, port = str(ip).split(':',maxsplit=2)[0], int(str(ip).split(':',maxsplit=2)[1])
        if client.connect_ex((ip, int(port))) == 0:
            ip = socket.gethostbyname(ip)+':'+str(port)
            log(f'§aSuccsesfuly TCPpinged §b{ip}§a.', 1)
            return ip
        else:
            log(f'§cUnsuccsesfuly TCPpinged §b{ip}§c.', 2)
    except Exception as e:
        log(f'§cTCPping erroed of ip §b{ip}§c with:',2)
        log(str(e), 2)

dotenv.load_dotenv('profile.env')

if __name__=='__main__':
    start_time = time.time_ns()

    try:
        addrslist = WebsiteScrapers.getips()
    except Exception as e:
        print(e)
        exit()

    ips = []
    log('§aDone getting all good ping-able domains', 0)
    log(f'§aStarted pinging {len(addrslist)} ips.', 0)
    if os.getenv('THREADTCPINGS') == '0':
        for i, addr in enumerate(addrslist):
            ip = tcpping(addr)
            if ip != None and ip not in ips:
                ips.append(ip)
            log(f'§b {i} / {len(addrslist)} - {100*i/len(addrslist)}% - {addr}', 1)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            for ip in executor.map(tcpping, addrslist):
                if ip!=None and ip not in ips:
                    ips.append(ip)

    ipranges = getRangesFromIps(ips)

    log('§adone pinging ips', 0)
    iplist = masscan(ipranges)
    if os.getenv('THREADPINGS') == '0':
        for i, addr in enumerate(iplist):
            try2ping(addr)
            log(f'§b {i} / {len(iplist)} - {100*i/len(iplist)}% - {addr}', 1)
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(try2ping, iplist)

    conn.close()

        
    log('§aSTART TIME IN UNIX:'+str(start_time), 0)

