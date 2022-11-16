import requests
from bs4 import BeautifulSoup
import socket
import os
import subprocess
import multiprocessing
from multiprocessing.pool import ThreadPool
import concurrent.futures
import pinger

def masscan(ip):
    if ip==None:
        return
    ipparts = ip.split('.')
    os.system(f"sudo masscan -p 25565 --wait=0 --rate 10000 -oX output.xml --range {ipparts[0]}.{ipparts[1]}.{ipparts[2]}.0-{ipparts[0]}.{ipparts[1]}.{ipparts[2]}.255")
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
    #lastpage = int(str(BeautifulSoup(requests.get('https://minecraft-server-list.com/').content,'lxml').find('a', string='>>').get('href')).split('/')[2])
    lastpage = 3
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
    i=1
    for ip in iprages:
        masscan(ip)
        os.system("clear")
        print(f"{round(i/len(iprages)*100,2)}% Done with masscaning!")
        i+=1
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(pinger.main,iplist)
    
        


    exit()
    tcpping()
    i = 1
    for ip in dupelicateaddress:
        masscan(ip)
        os.system("clear")
        print(f"{round(i/len(dupelicateaddress)*100,2)}% Done with masscaning!")
        i+=1
    for ip in masscanedips:
        try:
            subprocess.run(['python3', './pinger.py', ip], timeout=2)
        except:
            pass
        print(f"{round(i/len(masscanedips)*100,2)}% Done with pinging!")
        i+=1
    f.close()