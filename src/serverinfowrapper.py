import dbutils, serverinfo, multiprocessing as mp

def scanandsave(ip):
    dbutils.addJoinScan(serverinfo.main(ip))

if __name__=='__main__':
    # Proccess input
    import sys
    if len(sys.argv)!=2:
        exit()
    # Proccess stuffss
    p = mp.Process(target=scanandsave, args=(sys.argv[1], ))
    p.start()
    p.join(8)
    if p.is_alive:
        p.terminate()