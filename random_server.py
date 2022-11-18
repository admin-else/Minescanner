import json
import random
import time

f = open("servers.json", 'r')
file_data = json.load(f)
ips = []
for server in file_data['serverlist']:
    try:
        if server['version']['protocol']==760:
            ips.append(server['ip'])
    except:
        pass

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
