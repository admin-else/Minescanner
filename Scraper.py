import requests
from bs4 import BeautifulSoup
import socket
import os
import json
import concurrent.futures
import pinger
import subprocess
from multiprocessing import Pool

def write_jsondata(new_data):
    with open('servers.json','r+') as file:
        file_data = json.load(file)
        file_data["serverlist"]=new_data+file_data["serverlist"]
        file.seek(0)
        json.dump(file_data, file, indent = 2)
        file.close()

def masscan(ipranges):
    lines = []
    for iprange in ipranges:
        lines.append('range = '+ iprange+'.0-'+iprange+'.255\n')
    open('./masscan.conf','w').writelines(lines)
    os.system(f"sudo masscan -c ./masscan.conf -p 25565 --wait=3 --rate 1000 -oL output.txt")
    lines = open('output.txt', 'r').readlines()
    ips = []
    for line in lines:
        if str(line).startswith('open tcp 25565 '):
            ips.append(line.split(' ')[3])
    print(len(ips))
    return ips

def try2ping(ip):
    try:
        subprocess.run(['python3','/home/simon/src/python/minescaner/pinger.py',ip], timeout=2)
    except:
        pass

def tcpping(ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(0.05)
    try:
        if client.connect_ex((ip, 25565)) == 0:
            ip = socket.gethostbyname(ip)
            ipParts = str(ip).split('.')
            return f"{ipParts[0]}.{ipParts[1]}.{ipParts[2]}"
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
    lastpage = int(str(BeautifulSoup(requests.get('https://minecraft-server-list.com/').content,'lxml').find('a', string='>>').get('href')).split('/')[2])
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
    i = 0
    for ip in iplist:
        try2ping(ip)
        i+=1
        os.system('clear')
        print(f'Pinged {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')
