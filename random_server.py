import json
import random
import time

with open("servers.save.json", 'r') as f:
    file_data = json.load(f)
    ips = [
        server['ip']
        for server in file_data['serverlist']
        if server['version']['protocol']==760
    ]

f = open('ips.txt', 'w')
f.writelines([
    ip+'\n'
    for ip in ips
])
f.close()


for ip in ips:
    print(ip)

print('will radomly pick a server from a pool of '+str(len(ips))+'.')

while True:
    ip=random.choice(ips)
    print(f'New ip: {ip}')
    data = open('/etc/hosts', 'r').readlines()
    data[2] = f'{ip}	random_server.local'
    open('/etc/hosts', 'w').writelines(data)
    time.sleep(1)
