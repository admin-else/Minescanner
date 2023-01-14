import socket, os, concurrent.futures, WebsiteScrapers, pinger, multiprocessing, dotenv, time, dbutils
from util import log

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
    ping = pinger.main(ip, port)
    if dbutils.addPing(ip, port, time.time_ns(), ping):
        log(f'§aSuccessful ping on {ip}:{port}', 1)
        log(f'§5 MOTD: {ping['']}', 3)
    else:
        log(f'§cunSuccessful ping on {ip}:{port}', 2)

    
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
    print('Scanning '+ip+'.', end='\r')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(0.05)
    try:
        if client.connect_ex((ip, 25565)) == 0:
            ip = socket.gethostbyname(ip)
            return ".".join(str(ip).split(".")[:3])
    except:
        pass

if __name__=='__main__':
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
    
    print('START TIME IN UNIX:'+str(start_time))

