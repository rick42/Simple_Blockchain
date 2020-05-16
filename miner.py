import os
import requests
import threading

class Miner:
    def __init__(self, port, hash_rate=None):
        self.port = port
        self.hash_rate = hash_rate
        self.node_thread = threading.Thread(target=self.start_server)
        #self.mining_thread
        print('MINER CREATED: port={}  hashrate={}'.format(port, hash_rate))
    
    def start_server(self):
        print('STARTING THE SERVER')
        os.system("python node.py --port {} --hashrate {}".format(self.port,self.hash_rate))
    
    def create_node(self):
        print("Entered create_node method")
        #self.node_thread = threading.Thread(target=self.start_server)
        self.node_thread.start()
        print("Exiting create_node method")
        pass

    def shutdown_node(self):
        url = 'http://localhost:{}/shutdown'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            pass
