import requests
from bs4 import BeautifulSoup
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
    return [tag.text
            for tag in getSoup(f'https://minecraft-server-list.com/page/{i}/').find_all('div', class_="adressen online")]
        
addrs = []
lastpage = int(getSoup('https://minecraft-server-list.com').find('a', string='>>').get('href').split('/')[2])
addrs+=scanWebsite(mc_s_l_com, lastpage)

print(addrs)