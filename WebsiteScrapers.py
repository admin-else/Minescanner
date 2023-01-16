import requests, dotenv, os
from bs4 import BeautifulSoup
import concurrent.futures
from util import log

def getSoup(url, timeout=None):
    try:
        try:
            r = requests.get(url, timeout=timeout)
        except requests.ConnectTimeout as e:
            print(e)
        else:
            if r.status_code!=200:
                raise ConnectionError('Connection to', url, 'errored with code', r.status_code+'.')
            return BeautifulSoup(r.content, 'html.parser')
    except Exception as e:
        print(e)

def scanWebsite(method, lastpage):
    addresses = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for ips in executor.map(method, range(1, lastpage)):
            if ips!=None:
                addresses+=ips
    return addresses


def mc_s_l_com(i):
    try:
        log(f'§aSuccsesfuly pinged the §b{i}§a page of §bhttps://minecraft-server-list.com§a.',1,end='\r')
        return [tag.text
                for tag in getSoup(f'https://minecraft-server-list.com/page/{i}/').find_all('div', class_="adressen online")]
    except Exception as e:
        log(f'§cThe ping to the §b{i}§a page of §bhttps://minecraft-server-list.com§a.', 2)
        log(e, 2)

def mcs(i):
    try:
        log(f'§aSuccsesfuly pinged the §b{i}§a page of §bhttps://minecraftservers.org§a.',1,end='\r')
        return [tag.get('data-clipboard-text')
                for tag in getSoup(f'https://minecraftservers.org/index/{i}').find_all('button', class_="copy-action")]
    except Exception as e:
        log(f'§cThe ping to the §b{i}§a page of §bhttps://minecraftservers.org§a.', 2)
        log(e, 2)
def mcl(i):
    try:
        log(f'§aSuccsesfuly pinged the §b{i}§a page of §bhttps://minecraftlist.com/servers§a.',1,end='\r')
        return [tag.text
                for tag in getSoup(f'https://minecraftlist.com/servers/{i}').find_all('strong', class_="block truncate")]
    except Exception as e:
        log(f'§cThe ping to the §b{i}§a page of §bhttps://minecraftlist.com/servers§a.', 2)
        log(e, 2)


def getips():
    dotenv.load_dotenv('profile.env')
    addrs = []
    if os.getenv('DEBUG')=='1':
        lastpage = 3
    
    if os.getenv('DEBUG')!='1':
        lastpage = int(getSoup('https://minecraft-server-list.com').find('a', string='>>').get('href').split('/')[2])
    log(f'§aStarted scraping §b{lastpage}§a pages of §bhttps://minecraft-server-list.com§a.', 0)
    addrs+=scanWebsite(mc_s_l_com, lastpage)

    if os.getenv('DEBUG')!='1':
        lastpage = int(getSoup('https://minecraftservers.org').find('a', string='>>').get('href').split('/')[2])
    log(f'§aStarted scraping §b{lastpage}§a pages of §bhttps://minecraftservers.org§a.', 0)
    addrs+=scanWebsite(mcs, lastpage)
    
    log('§aCutting ips.', 0)
    addrs = list(dict.fromkeys(addrs))
    tmpaddrs = []
    garbage = ['hypixel.io', 'aternos.me', 'hypixel.net', 'nerd.nu', 'minehut.gg']
    for ip in addrs:
        isgood = True
        for indicator in garbage:
            if ip.__contains__(indicator):
                isgood = False
        if ip not in tmpaddrs and isgood:
            tmpaddrs.append(ip)
    addrs = tmpaddrs
    return addrs


