import requests
from bs4 import BeautifulSoup
import socket
import os
import subprocess
import multiprocessing
from multiprocessing.pool import ThreadPool
import concurrent.futures
import pinger

def serverlistping(ip):
    try:
            pinger.main(ip)
    except:
        pass

def masscan(ipranges):
    lines = []
    for iprange in ipranges:
        lines.append('range = '+ iprange+'.0-'+iprange+'.255\n')
        open('./masscan.conf','w').writelines(lines)
    os.system(f"sudo masscan -c ./masscan.conf -p 25565 --wait=0 --rate 10000 -oX output.xml")
    soup = BeautifulSoup(open("output.xml",'r').read(),'lxml')
    hosts = soup.find_all('address')
    for host in hosts:
        iplist.append(host.get('addr'))


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
    iplist = []
    lastpage = int(str(BeautifulSoup(requests.get('https://minecraft-server-list.com/').content,'lxml').find('a', string='>>').get('href')).split('/')[2])
    #lastpage = 3
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for ips in executor.map(scaper2, range(1, lastpage)):
            if ips!=None:
                addrslist=addrslist+ips
    addrslist = list(dict.fromkeys(addrslist))
    print('done downloading ips')
    with concurrent.futures.ProcessPoolExecutor(max_workers=200) as executor:
        for range in executor.map(tcpping, addrslist):
            if range!=None and range not in iprages:
                iprages.append(range)
    print('done pinging ips')
    masscan(iprages)
    for ip in iprages:
        try:
            subprocess.run(['python3','/home/simon/src/python/minescaner/pinger.py',ip], timeout=2)
        except:
            pass
        print('pinged')