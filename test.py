import subprocess, os

def try2ping(ip):
    try:
        subprocess.run(['python3','./serverinfo.py',ip], timeout=5)
    except Exception as e:
        print(e)
        
f = open('ips.txt', 'r')
iplist = [ip.rstrip()
          for ip in f.readlines()]
f.close()

for i, ip in enumerate(iplist):
    try2ping(ip)
    i+=1
    print(f'Pinged {ip} - {i}/{len(iplist)} - {round(i/len(iplist)*100,2)}%')