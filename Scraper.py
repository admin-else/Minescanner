import socket, os, concurrent.futures, subprocess, WebsiteScrapers, pinger, multiprocessing, signal, dotenv, time

def masscan(ipranges):
    lines = [f'range = {iprange}.0-{iprange}.255\n' for iprange in ipranges]

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
        if line.startswith('open tcp 25565 ')
    ]
    return ips

def try2ping(ip):
    try:
        p = multiprocessing.Process(target=pinger.main, args=(ip,))
        p.start()
        p.join(2)
        if p.is_alive:
            p.terminate()
    except Exception as e:
        print(e)

def tcpping(ip):
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
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for range in executor.map(tcpping, addrslist):
            if range!=None and range not in iprages:
                iprages.append(range)
    print('done pinging ips')
    iplist = masscan(iprages)
    if os.getenv('THREADPINGS') == '0':
        for i, addr in enumerate(iplist):
            try2ping(addr)
            print(f' {i} / {len(iplist)} - {100*i/len(iplist)}% - {addr}')
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(try2ping, iplist)
    
    print(start_time)

