import os
import node
import threading

def make_miner(port):
    os.system("python node.py --port {}".format(port))

if __name__ == '__main__':
    threads = list()

    for i in range(2):
        x = threading.Thread(target=make_miner, args=(5000+i,))
        threads.append(x)
        x.start()
    
    print('THREADS CREATED!!')
