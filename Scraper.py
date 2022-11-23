from bs4 import BeautifulSoup
import socket, json, os, concurrent.futures, subprocess, requests
from multiprocessing import Pool

def masscan(ipranges):
    lines = [f'range = {iprange}.0-{iprange}.255\n' for iprange in ipranges]
    with open('./masscan.conf','w') as f:
        f.writelines(lines)
    os.system('sudo masscan -c ./masscan.conf -p 25565 --wait=3 --rate 1000 -oL output.txt')
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
        subprocess.run(['python3','./pinger.py',ip], timeout=2)
    except Exception:
        print(Exception)

def try2join(ip):
    try:
        subprocess.run(['python3','./pinger.py',ip], timeout=5)
    except Exception:
        print(Exception)

def tcpping(ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(0.05)
    try:
        if client.connect_ex((ip, 25565)) == 0:
            ip = socket.gethostbyname(ip)
            return ".".join(str(ip).split(".")[:3])
    except:
        pass

def scaper2(i):
    r = requests.get(f'https://minecraft-server-list.com/page/{i}/')
    soup = BeautifulSoup(r.content, 'lxml')
    tags = soup.find_all('div', class_="adressen online")
    addrslist = []
    for tag in tags:
        addrslist.append(tag.text)
    return addrslist

if __name__=='__main__':
    addrslist = []
    iprages = []
    res = requests.get('https://minecraft-server-list.com/')
    if res.status_code!=200:
        raise ConnectionError
    lastpage = int(str(BeautifulSoup(res.content,'lxml').find('a', string='>>').get('href')).split('/')[2])
    #lastpage = 3
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for ips in executor.map(scaper2, range(1, lastpage)):
            if ips!=None:
                addrslist=addrslist+ips
    addrslist = list(dict.fromkeys(addrslist))
    print('done downloading ips')
    with concurrent.futures.ProcessPoolExecutor(max_workers=70) as executor:
        for range in executor.map(tcpping, addrslist):
            if range!=None and range not in iprages:
                iprages.append(range)
    print('done pinging ips')
    iplist = masscan(iprages)
    for i, ip in enumerate(iplist):
        try2ping(ip)
        i+=1
        print(f'Pinged {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')

    with open("servers.save.json", 'r') as f:
        file_data = json.load(f)
        iplist = [
            server['ip']
            for server in file_data['serverlist']
            if server['version']['protocol']>=750 and server['version']['protocol']<=760
            ]

    for i, ip in enumerate(iplist):
        try2join(ip)
        i+=1
        print(f'Joined {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')