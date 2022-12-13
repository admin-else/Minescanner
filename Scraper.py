from bs4 import BeautifulSoup
import socket, json, os, concurrent.futures, subprocess, requests
from multiprocessing import Pool
from twisted.internet import reactor
from quarry.net.client import ClientFactory, ClientProtocol
from eventlet.timeout import Timeout
import json
import datetime

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
        subprocess.run(['python3','./pinger.py',ip], timeout=3)
    except Exception as e:
        print(e)

def try2join(ip):
    try:
        subprocess.run(['python3','./serverinfo.py',ip], timeout=5)
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
    with open('servers.json', 'w') as f:
        f.write('{"serverlist":{},"servers":{}}')

    try:
        os.system('/bin/python3.8 ./WebsiteScrapers.py')
    except Exception as e:
        print(e)
        exit()

    with open('ips.txt', 'r') as f:
        addrslist  = f.readlines()
    addrslist = [addr.rstrip()
                 for addr in addrslist]
    iprages = []
    print('done downloading ips')
    with concurrent.futures.ProcessPoolExecutor(max_workers=70) as executor:
        for range in executor.map(tcpping, addrslist):
            if range!=None and range not in iprages:
                iprages.append(range)
    print('done pinging ips')
    iplist = masscan(iprages)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(try2ping, iplist)
    #for i, ip in enumerate(iplist):
    #    try2ping(ip)
    #    print(f'Pinged {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')

    #with open("servers.json", 'r') as f:
    #    file_data = json.load(f)
    #    iplist = [
    #        server['ip']
    #        for server in file_data['serverlist']
    #        if server['version']['protocol']>=750 and server['version']['protocol']<=760
    #        ]

    #for i, ip in enumerate(iplist):
    #    try2join(ip)
    #    print(f'Joined {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')
