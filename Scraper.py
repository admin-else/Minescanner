import requests
from bs4 import BeautifulSoup
import socket
import os
import subprocess

websiteAddresses = []
pingedAddresses = []
dupelicateaddress = []
succsesfullpings = []
masscanedips = []

f = open('ips.txt', 'w')

def masscan(ip):
    ipparts = ip.split('.')
    os.system(f"sudo masscan -p 25565 --wait=0 --rate 10000 -oX output.xml --range {ipparts[0]}.{ipparts[1]}.{ipparts[2]}.0-{ipparts[0]}.{ipparts[1]}.{ipparts[2]}.255")
    soup = BeautifulSoup(open("output.xml",'r').read(),'lxml')
    hosts = soup.find_all('address')
    for host in hosts:
        masscanedips.append(host.get('addr'))


def tcpping():
    i = 0
    print("Pinging Servers")
    for ip in websiteAddresses:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(0.05)
        try:
            if client.connect_ex((ip, 25565)) == 0:
                ip = socket.gethostbyname(ip)
                ipParts = str(ip).split('.')
                iprange = f"{ipParts[0]}.{ipParts[1]}.{ipParts[2]}"
                if iprange not in pingedAddresses:
                    pingedAddresses.append(iprange)
                else: 
                    if iprange not in dupelicateaddress:
                        dupelicateaddress.append(iprange)
        except:
            pass
        i+=1
        if(i%10==0):
            print("{}% Done...".format(round(i/len(websiteAddresses)*100,2)))
    print(f"done! pinged {len(websiteAddresses)} servers!")

def scaper1():
    print("Started scrapeing topg.org!")
    i = 1
    while True:
        url = 'https://topg.org/minecraft-servers/page/{}'.format(i)
        r = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'lxml')
        ips = soup.find_all('div', class_="server-ip")
        if(len(ips)==0):
            print("Scraped {} pages of topg.org!!!".format(i))
            break
        for ip in ips:
            if not(websiteAddresses.__contains__(ip.span.text)):
                websiteAddresses.append(ip.span.text)
        print("{}% Done...".format(round(i/57*100,1)))
        i +=1
def scaper2():
    i = 1
    print("Started scrapeing minecraft-server-list.com!")
    while True: 
        url = 'https://minecraft-server-list.com/page/{}/'.format(i)
        r = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'lxml')
        tags = soup.find_all('div', class_="adressen online")
        if(len(tags)==0):            
            print("Scraped {} pages of minecraft-server-list.com!!!".format(i))
            break
        for tag in tags:
            websiteAddresses.append(tag.text)
        print("{}% Done...".format(round(i/237*100,1)))
        i+=1


if __name__=='__main__':
    scaper2()
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