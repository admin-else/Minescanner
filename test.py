# SuperFastPython.com
# example of returning a variable from a process using a queue
from random import random
from time import sleep
from multiprocessing import Queue
from multiprocessing import Process
import pinger
from _queue import Empty
 
# function to execute in a child process
def task(queue):
    sleep(12)
    # generate some data
    data = random()
    # block, to simulate computational effort
    print(f'Generated {data}', flush=True)
    sleep(data)
    # return data via queue
    queue.put({'data': 'sus'})
    queue.put({'data': 'sus1'})
    queue.put(None)
 
# protect the entry point
def ping(ip, q):
    try:
        process = Process(target=pinger.main, args=(ip,q,))
        process.start()
        process.join(2)
        process.terminate()
    except Exception:
        pass

def main():
    q = Queue()
    
    ping('play.hypixel.net', q)
    list = []
    while(True):
        try:
            item = q.get()
            if item!=None:
                list.append(item)
            else:
                break
        except:
            break
    print(list)

main()