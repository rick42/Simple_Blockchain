import os
import node
import threading
import requests

def make_miner(port):
    os.system("python node.py --port {}".format(port))

def shutdown_miner(port):
    url = 'http://localhost:{}/shutdown'.format(port)
    try:
        response = requests.post(url)
        # if response.status_code == 400 or response.status_code == 500:
        #     print('Transaction declined, needs resolving')
        #     return False
    except requests.exceptions.ConnectionError:
        pass

if __name__ == '__main__':
    threads = list()

    for i in range(2):
        x = threading.Thread(target=make_miner, args=(5000+i,))
        threads.append(x)
        x.start()

    input('Press Enter to shutdown node localhost:5000')

    shutdown_miner(5000)

    input('Press Enter again to end script')

    
    print('THREADS CREATED!!')
