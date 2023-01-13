import requests, dotenv, os
from bs4 import BeautifulSoup
import concurrent.futures

def masscan(ips):
    lines = [f'range = {ip}\n' for ip in ips]

    if os.path.exists('./paused.conf'):
        os.remove('./paused.conf')
    if os.path.exists('./masscan.conf'):
        os.remove('./masscan.conf')
    
    with open('./masscan.conf','w') as f:
        f.writelines(lines)
    
    out = os.popen('sudo masscan -c ./masscan.conf -p 25565-25577 --excludefile ./excludefile.txt --interactive --wait=3 --rate {}'.format(os.getenv('MASSCANRATE'))).read().splitlines()
    out = [line.rstrip()
           for line in out
           if line.startswith('Discovered open port')]
    for server in out:
        print(server[21:][:5])
        print(server[34:])

def getSoup(url, timeout=None):
    print (url, end="\r")
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
        return [tag.text
                for tag in getSoup(f'https://minecraft-server-list.com/page/{i}/').find_all('div', class_="adressen online")]
    except Exception as e:
        print(e)

def mcs(i):
    try:
        return [tag.get('data-clipboard-text')
                for tag in getSoup(f'https://minecraftservers.org/index/{i}').find_all('button', class_="copy-action")]
    except Exception as e:
        print(e)

def mcl(i):
    try:
        return [tag.text
                for tag in getSoup(f'https://minecraftlist.com/servers/{i}').find_all('strong', class_="block truncate")]
    except Exception as e:
        print(e)


def getips():
    dotenv.load_dotenv('profile.env')
    addrs = []
    if os.getenv('DEBUG')=='1':
        lastpage = 3
    
    if os.getenv('DEBUG')!='1':
        lastpage = int(getSoup('https://minecraft-server-list.com').find('a', string='>>').get('href').split('/')[2])
    print('Started scraping',lastpage,'pages of https://minecraft-server-list.com.')
    addrs+=scanWebsite(mc_s_l_com, lastpage)
    print('Scraped https://minecraft-server-list.com.')

    if os.getenv('DEBUG')!='1':
        lastpage = int(getSoup('https://minecraftservers.org').find('a', string='>>').get('href').split('/')[2])
    print('Started scraping',lastpage,'pages of https://minecraftservers.org.')
    addrs+=scanWebsite(mcs, lastpage)
    print('Scanned https://minecraftservers.org.')

    #print('Stating scanning https://minecraftlist.com')
    #if os.getenv('DEBUG')!='1':
    #    addrs+=scanWebsite(mcl, 100)
    #print('Done scanning https://minecraftlist.com')
    
    print('Cutting ips')
    addrs = list(dict.fromkeys(addrs))
    tmpaddrs = []
    garbage = ['hypixel.io', 'aternos.me', 'hypixel.net', 'nerd.nu', 'minehut.gg', ':']
    for ip in addrs:
        isgood = True
        for indicator in garbage:
            if ip.__contains__(indicator):
                isgood = False
        if ip not in tmpaddrs and isgood:
            tmpaddrs.append(ip)
    addrs = tmpaddrs
    print('Done Cutting ips')
    return addrs


