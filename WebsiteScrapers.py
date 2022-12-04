from bs4 import BeautifulSoup
import requests
import concurrent.futures

def getSoup(url, timeout=None):
    try:
        try:
            r = requests.get(url, timeout=timeout)
        except requests.ConnectTimeout as e:
            print(e)
        else:
            if r.status_code!=200:
                raise ConnectionError('Connection to', url, 'errored with code', r.status_code+'.')
            return BeautifulSoup(r.content, 'lxml')
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
                for tag in getSoup(f'https://minecraft-server-list.com/page/{i}/', timeout=2).find_all('div', class_="adressen online")]
    except Exception as e:
        print(e)

def mcs(i):
    try:
        return [tag.get('data-clipboard-text')
                for tag in getSoup(f'https://minecraftservers.org/index/{i}', timeout=2).find_all('button', class_="copy-action")]
    except Exception as e:
        print(e)



addrs = []
#lastpage = 3
lastpage = int(getSoup('https://minecraft-server-list.com').find('a', string='>>').get('href').split('/')[2])
print('Started scraping',lastpage,'pages of https://minecraft-server-list.com.')
addrs+=scanWebsite(mc_s_l_com, lastpage)
print('Scraped https://minecraft-server-list.com.')
lastpage = int(getSoup('https://minecraftservers.org').find('a', string='>>').get('href').split('/')[2])
print('Started scraping',lastpage,'pages of https://minecraftservers.org.')
addrs+=scanWebsite(mcs, lastpage)
print('Scanned https://minecraftservers.org.')
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

with open('ips.txt', 'w') as f:
    f.writelines([addr+'\n'
                  for addr in addrs
                ])
